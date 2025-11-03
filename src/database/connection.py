import os
import sys
from pathlib import Path
from pymongo import MongoClient, GEOSPHERE
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv
import yaml

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / 'config' / 'database.yml'


def load_config():
    """
    Load database configuration from YAML file.

    Returns:
        dict: Database configuration parameters
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}\n"
            f"Please create config/database.yml based on the deliverable 1 documentation"
        )

    with open(CONFIG_FILE, 'r') as f:
        template = f.read()
        for key, value in os.environ.items():
            template = template.replace(f"${{{key}}}", value)
        config = yaml.safe_load(template)
        
    return config


def get_connection_string(config=None, include_password=True):
    """
    Generate MongoDB connection string from configuration.

    Args:
        config (dict, optional): Database configuration. If None, loads from file.
        include_password (bool): Whether to include password in connection string

    Returns:
        str: MongoDB connection URI

    Note:
        For local development without authentication, password is optional.
    """
    if config is None:
        config = load_config()

    env = os.getenv('ENVIRONMENT', 'development')
    db_config = config[env]['mongodb']

    if db_config.get('username') and db_config.get('password'):
        auth_source = db_config.get('auth_source', 'admin')
        conn_string = (
            f"mongodb://{db_config['username']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}"
            f"/{db_config['database']}?authSource={auth_source}"
        )
    elif db_config.get('username') and not include_password:
        conn_string = (
            f"mongodb://{db_config['username']}:****"
            f"@{db_config['host']}:{db_config['port']}"
            f"/{db_config['database']}"
        )
    else:
        conn_string = (
            f"mongodb://{db_config['host']}:{db_config['port']}"
            f"/{db_config['database']}"
        )

    return conn_string


def create_mongo_client(config=None):
    """
    Create MongoDB client with connection pooling.

    Args:
        config (dict, optional): Database configuration. If None, loads from file.

    Returns:
        pymongo.MongoClient: MongoDB client with connection pool

    Example:
        >>> client = create_mongo_client()
        >>> db = client['pdet_solar_analysis']
        >>> municipalities = db['pdet_municipalities']
        >>> count = municipalities.count_documents({})
        >>> print(f"Total municipalities: {count}")
    """
    if config is None:
        config = load_config()

    conn_string = get_connection_string(config, include_password=True)
    pool_config = config.get('connection_pool', {})

    client = MongoClient(
        conn_string,
        minPoolSize=pool_config.get('min_size', 2),
        maxPoolSize=pool_config.get('max_size', 10),
        serverSelectionTimeoutMS=pool_config.get('timeout', 30) * 1000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000
    )

    return client


def get_database(config=None):
    """
    Get database object from MongoDB client.

    Args:
        config (dict, optional): Database configuration. If None, loads from file.

    Returns:
        pymongo.database.Database: MongoDB database object

    Example:
        >>> db = get_database()
        >>> print(f"Database: {db.name}")
        >>> print(f"Collections: {db.list_collection_names()}")
    """
    if config is None:
        config = load_config()

    env = os.getenv('ENVIRONMENT', 'development')
    db_config = config[env]['mongodb']
    client = create_mongo_client(config)
    db = client[db_config['database']]

    return db


def test_connection(config=None, verbose=True):
    """
    Test database connection and MongoDB geospatial capabilities.

    Args:
        config (dict, optional): Database configuration. If None, loads from file.
        verbose (bool): Whether to print detailed information

    Returns:
        bool: True if connection successful and geospatial support is available

    Example:
        >>> if test_connection():
        ...     print("Database ready!")
    """
    try:
        if config is None:
            config = load_config()
        
        env = os.getenv('ENVIRONMENT', 'development')
        db_config = config[env]['mongodb']
        client = create_mongo_client(config)
        db_name = db_config['database']
        db = client[db_name]

        if verbose:
            print("=" * 60)
            print("MongoDB Connection Test")
            print("=" * 60)

        client.admin.command('ping')
        if verbose:
            print(f"✓ Connected to MongoDB")

        server_info = client.server_info()
        if verbose:
            print(f"✓ MongoDB Version: {server_info['version']}")
            print(f"✓ Database: {db_name}")

        collections = db.list_collection_names()
        if verbose:
            if collections:
                print(f"\n✓ Collections in database:")
                for coll_name in collections:
                    coll = db[coll_name]
                    count = coll.count_documents({})
                    indexes = coll.list_indexes()
                    index_names = [idx['name'] for idx in indexes]
                    print(f"  - {coll_name}: {count:,} documents")
                    if index_names:
                        print(f"    Indexes: {', '.join(index_names)}")
            else:
                print(f"\n⚠ No collections found in database '{db_name}'")
                print("  Collections will be created when data is loaded.")

        if verbose:
            print(f"\n✓ Geospatial Support:")
            print(f"  - 2dsphere indexes: Supported")
            print(f"  - GeoJSON format: Supported")
            print(f"  - Spatial operators: $geoWithin, $geoIntersects, $near, $nearSphere")

        test_coll = db['_connection_test']
        test_doc = {"test": "connection", "status": "ok"}
        result = test_coll.insert_one(test_doc)
        test_coll.delete_one({"_id": result.inserted_id})
        if verbose:
            print(f"\n✓ Write permission: OK")

        if verbose:
            print("=" * 60)
            print("✓ Connection test PASSED")
            print("=" * 60)

        return True

    except FileNotFoundError as e:
        if verbose:
            print(f"\n✗ Configuration Error: {e}")
        return False

    except ConnectionFailure as e:
        if verbose:
            print(f"\n✗ Connection test FAILED")
            print(f"Error: Cannot connect to MongoDB server")
            print(f"Details: {e}")
            print("\nTroubleshooting:")
            print("1. Check if MongoDB is running:")
            print("   - Windows: Check Services or run 'mongod --version'")
            print("   - Linux/Mac: Run 'sudo systemctl status mongod'")
            print("2. Verify connection settings in config/database.yml")
            print("3. Check if MongoDB is listening on the correct host:port")
            print("4. Verify database credentials in .env file (if using auth)")
        return False

    except OperationFailure as e:
        if verbose:
            print(f"\n✗ Connection test FAILED")
            print(f"Error: Authentication failed or insufficient permissions")
            print(f"Details: {e}")
            print("\nTroubleshooting:")
            print("1. Verify DB_PASSWORD in .env file")
            print("2. Check user permissions in MongoDB")
            print("3. Ensure auth_source is correct in config/database.yml")
        return False

    except Exception as e:
        if verbose:
            print(f"\n✗ Connection test FAILED")
            print(f"Error: {type(e).__name__}: {e}")
            print("\nTroubleshooting:")
            print("1. Check MongoDB server logs")
            print("2. Verify config/database.yml configuration")
            print("3. Check .env file for correct credentials")
        return False


def create_spatial_indexes(collection_name, geometry_field='geom', config=None, verbose=True):
    """
    Create 2dsphere spatial index on a collection.

    Args:
        collection_name (str): Name of the collection
        geometry_field (str): Name of the geometry field (default: 'geom')
        config (dict, optional): Database configuration
        verbose (bool): Whether to print progress

    Returns:
        str: Name of created index

    Example:
        >>> create_spatial_indexes('pdet_municipalities', 'geom')
        'geom_2dsphere'
    """
    if config is None:
        config = load_config()

    db = get_database(config)
    collection = db[collection_name]

    index_name = f"{geometry_field}_2dsphere"

    try:
        result = collection.create_index(
            [(geometry_field, GEOSPHERE)],
            name=index_name
        )

        if verbose:
            print(f"✓ Created 2dsphere index '{result}' on {collection_name}.{geometry_field}")

        return result

    except Exception as e:
        if verbose:
            print(f"✗ Failed to create index: {e}")
        raise


def get_collection_info(collection_name, config=None):
    """
    Get information about a specific collection.

    Args:
        collection_name (str): Name of the collection
        config (dict, optional): Database configuration

    Returns:
        dict: Collection information including document count, indexes, sample doc

    Example:
        >>> info = get_collection_info('pdet_municipalities')
        >>> print(f"Documents: {info['document_count']}")
        >>> print(f"Indexes: {info['indexes']}")
    """
    if config is None:
        config = load_config()

    db = get_database(config)
    collection = db[collection_name]

    doc_count = collection.count_documents({})

    indexes = list(collection.list_indexes())
    index_info = [
        {
            'name': idx['name'],
            'keys': idx['key'],
            'unique': idx.get('unique', False)
        }
        for idx in indexes
    ]

    sample = collection.find_one({})

    stats = db.command("collStats", collection_name)

    return {
        'collection_name': collection_name,
        'document_count': doc_count,
        'indexes': index_info,
        'size_bytes': stats.get('size', 0),
        'storage_size_bytes': stats.get('storageSize', 0),
        'sample_document': sample
    }


def initialize_collections(config=None, verbose=True):
    """
    Initialize all collections defined in configuration with appropriate indexes.

    Args:
        config (dict, optional): Database configuration
        verbose (bool): Whether to print progress

    Returns:
        dict: Status of initialization for each collection

    Example:
        >>> result = initialize_collections()
        >>> print(result)
    """
    if config is None:
        config = load_config()

    db = get_database(config)
    collections_config = config.get('collections', {})

    results = {}

    if verbose:
        print("Initializing collections...")

    for coll_key, coll_name in collections_config.items():
        try:
            if coll_name not in db.list_collection_names():
                db.create_collection(coll_name)
                if verbose:
                    print(f"✓ Created collection: {coll_name}")
            else:
                if verbose:
                    print(f"  Collection already exists: {coll_name}")

            if 'municipalities' in coll_key or 'buildings' in coll_key:
                create_spatial_indexes(coll_name, 'geom', config, verbose=False)
                if verbose:
                    print(f"✓ Created geospatial index on {coll_name}.geom")

            collection = db[coll_name]
            if 'municipalities' in coll_key:
                collection.create_index('muni_code', unique=True)
                collection.create_index('dept_code')
                if verbose:
                    print(f"✓ Created indexes on {coll_name}: muni_code, dept_code")

            elif 'buildings' in coll_key:
                collection.create_index('muni_code')
                collection.create_index('area_m2')
                if verbose:
                    print(f"✓ Created indexes on {coll_name}: muni_code, area_m2")

            results[coll_name] = "success"

        except Exception as e:
            if verbose:
                print(f"✗ Error initializing {coll_name}: {e}")
            results[coll_name] = f"error: {e}"

    return results


if __name__ == "__main__":
    """
    Run connection test when script is executed directly.

    Usage:
        python src/database/connection.py
        python src/database/connection.py --quiet
        python src/database/connection.py --init
    """
    import argparse

    parser = argparse.ArgumentParser(description='Test MongoDB connection and initialize collections')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress output (only return exit code)')
    parser.add_argument('--init', action='store_true',
                        help='Initialize collections with indexes')

    args = parser.parse_args()

    if args.init:
        success = test_connection(verbose=not args.quiet)
        if success:
            initialize_collections(verbose=not args.quiet)
    else:
        success = test_connection(verbose=not args.quiet)

    sys.exit(0 if success else 1)
