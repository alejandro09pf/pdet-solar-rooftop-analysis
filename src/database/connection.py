"""
Database connection module for PDET Solar Analysis project.
Handles PostgreSQL/PostGIS connections using SQLAlchemy.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import yaml

# Load environment variables from .env file
load_dotenv()

# Get project root directory
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
            f"Please create config/database.yml based on config/database.yml.example"
        )

    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_connection_string(config=None, include_password=True):
    """
    Generate PostgreSQL connection string from configuration.

    Args:
        config (dict, optional): Database configuration. If None, loads from file.
        include_password (bool): Whether to include password in connection string

    Returns:
        str: SQLAlchemy connection string

    Raises:
        ValueError: If DB_PASSWORD environment variable is not set
    """
    if config is None:
        config = load_config()

    db_config = config['database']

    # Get password from environment variable
    password = os.getenv('DB_PASSWORD')
    if not password and include_password:
        raise ValueError(
            "DB_PASSWORD environment variable not set.\n"
            "Please set it in your .env file or environment."
        )

    # Build connection string
    if include_password:
        conn_string = (
            f"postgresql://{db_config['user']}:{password}"
            f"@{db_config['host']}:{db_config['port']}"
            f"/{db_config['database']}"
        )
    else:
        conn_string = (
            f"postgresql://{db_config['user']}:****"
            f"@{db_config['host']}:{db_config['port']}"
            f"/{db_config['database']}"
        )

    return conn_string


def create_db_engine(echo=False, config=None):
    """
    Create SQLAlchemy engine for database connections.

    Args:
        echo (bool): Whether to echo SQL statements (for debugging)
        config (dict, optional): Database configuration. If None, loads from file.

    Returns:
        sqlalchemy.engine.Engine: Database engine with connection pooling

    Example:
        >>> engine = create_db_engine(echo=True)
        >>> with engine.connect() as conn:
        ...     result = conn.execute(text("SELECT PostGIS_Version();"))
        ...     print(result.fetchone())
    """
    if config is None:
        config = load_config()

    conn_string = get_connection_string(config, include_password=True)
    pool_config = config.get('connection_pool', {})

    engine = create_engine(
        conn_string,
        echo=echo,
        poolclass=QueuePool,
        pool_size=pool_config.get('max_size', 10),
        max_overflow=pool_config.get('overflow', 5),
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600    # Recycle connections after 1 hour
    )

    return engine


def test_connection(config=None, verbose=True):
    """
    Test database connection and PostGIS installation.

    Args:
        config (dict, optional): Database configuration. If None, loads from file.
        verbose (bool): Whether to print detailed information

    Returns:
        bool: True if connection successful and PostGIS is available

    Example:
        >>> if test_connection():
        ...     print("Database ready!")
    """
    try:
        if config is None:
            config = load_config()

        engine = create_db_engine(config=config)
        schema = config['database']['schema']

        with engine.connect() as conn:
            # Test basic connection
            if verbose:
                print("=" * 60)
                print("Database Connection Test")
                print("=" * 60)

            # Test PostgreSQL version
            result = conn.execute(text("SELECT version();"))
            pg_version = result.fetchone()[0]
            if verbose:
                print(f"✓ PostgreSQL: {pg_version.split(',')[0]}")

            # Test PostGIS version
            result = conn.execute(text("SELECT PostGIS_Version();"))
            postgis_version = result.fetchone()[0]
            if verbose:
                print(f"✓ PostGIS Version: {postgis_version}")

            # Test PostGIS full info
            result = conn.execute(text("SELECT PostGIS_Full_Version();"))
            postgis_full = result.fetchone()[0]
            if verbose:
                print(f"✓ PostGIS Full Info:")
                for line in postgis_full.split():
                    if line.strip():
                        print(f"  {line}")

            # Test schema existence
            result = conn.execute(text(
                f"SELECT schema_name FROM information_schema.schemata "
                f"WHERE schema_name = :schema;"
            ), {"schema": schema})

            if result.fetchone():
                if verbose:
                    print(f"✓ Schema '{schema}' exists")

                # Check tables in schema
                result = conn.execute(text(
                    f"SELECT table_name FROM information_schema.tables "
                    f"WHERE table_schema = :schema "
                    f"ORDER BY table_name;"
                ), {"schema": schema})

                tables = [row[0] for row in result.fetchall()]
                if tables:
                    if verbose:
                        print(f"✓ Tables in schema '{schema}':")
                        for table in tables:
                            print(f"  - {table}")
                else:
                    if verbose:
                        print(f"⚠ No tables found in schema '{schema}'")
                        print("  Run SQL scripts to create tables.")

            else:
                if verbose:
                    print(f"✗ Schema '{schema}' not found")
                    print(f"  Please create schema by running:")
                    print(f"  psql -d {config['database']['database']} -f deliverables/deliverable_1/sql_scripts/01_create_schema.sql")
                return False

            # Test spatial reference systems
            result = conn.execute(text(
                "SELECT srid, auth_name, auth_srid, srtext "
                "FROM spatial_ref_sys "
                "WHERE srid IN (4326, 3116) "
                "ORDER BY srid;"
            ))
            if verbose:
                print("\n✓ Available Spatial Reference Systems:")
                for row in result.fetchall():
                    print(f"  SRID {row[0]}: {row[1]}:{row[2]}")

            if verbose:
                print("=" * 60)
                print("✓ Connection test PASSED")
                print("=" * 60)

        return True

    except FileNotFoundError as e:
        if verbose:
            print(f"\n✗ Configuration Error: {e}")
        return False

    except Exception as e:
        if verbose:
            print(f"\n✗ Connection test FAILED")
            print(f"Error: {type(e).__name__}: {e}")
            print("\nTroubleshooting:")
            print("1. Check if PostgreSQL is running")
            print("2. Verify database credentials in .env file")
            print("3. Ensure PostGIS extension is installed")
            print("4. Check config/database.yml configuration")
        return False


def get_table_info(table_name, schema='pdet_solar'):
    """
    Get information about a specific table.

    Args:
        table_name (str): Name of the table
        schema (str): Schema name (default: 'pdet_solar')

    Returns:
        dict: Table information including row count, columns, indexes

    Example:
        >>> info = get_table_info('pdet_municipalities')
        >>> print(f"Rows: {info['row_count']}")
    """
    engine = create_db_engine()

    with engine.connect() as conn:
        # Get row count
        result = conn.execute(text(
            f"SELECT COUNT(*) FROM {schema}.{table_name};"
        ))
        row_count = result.fetchone()[0]

        # Get column info
        result = conn.execute(text(
            f"SELECT column_name, data_type, character_maximum_length "
            f"FROM information_schema.columns "
            f"WHERE table_schema = :schema AND table_name = :table "
            f"ORDER BY ordinal_position;"
        ), {"schema": schema, "table": table_name})

        columns = [
            {
                'name': row[0],
                'type': row[1],
                'max_length': row[2]
            }
            for row in result.fetchall()
        ]

        # Get indexes
        result = conn.execute(text(
            f"SELECT indexname, indexdef "
            f"FROM pg_indexes "
            f"WHERE schemaname = :schema AND tablename = :table "
            f"ORDER BY indexname;"
        ), {"schema": schema, "table": table_name})

        indexes = [
            {'name': row[0], 'definition': row[1]}
            for row in result.fetchall()
        ]

    return {
        'table_name': table_name,
        'schema': schema,
        'row_count': row_count,
        'columns': columns,
        'indexes': indexes
    }


def execute_sql_file(sql_file_path, verbose=True):
    """
    Execute SQL commands from a file.

    Args:
        sql_file_path (str or Path): Path to SQL file
        verbose (bool): Whether to print execution details

    Returns:
        bool: True if execution successful

    Example:
        >>> execute_sql_file('deliverables/deliverable_1/sql_scripts/01_create_schema.sql')
    """
    sql_file = Path(sql_file_path)

    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    engine = create_db_engine()

    try:
        with engine.connect() as conn:
            if verbose:
                print(f"Executing SQL file: {sql_file}")

            # Execute SQL (note: some statements may need to be split)
            conn.execute(text(sql_content))
            conn.commit()

            if verbose:
                print(f"✓ SQL file executed successfully")

        return True

    except Exception as e:
        if verbose:
            print(f"✗ Error executing SQL file: {e}")
        return False


if __name__ == "__main__":
    """
    Run connection test when script is executed directly.

    Usage:
        python src/database/connection.py
    """
    import argparse

    parser = argparse.ArgumentParser(description='Test database connection')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress output (only return exit code)')

    args = parser.parse_args()

    success = test_connection(verbose=not args.quiet)

    # Exit with appropriate code
    sys.exit(0 if success else 1)
