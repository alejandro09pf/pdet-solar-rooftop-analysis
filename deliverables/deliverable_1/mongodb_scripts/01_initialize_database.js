// ============================================================================
// PDET Solar Rooftop Analysis - MongoDB Database Initialization
// ============================================================================
// Script: 01_initialize_database.js
// Purpose: Initialize MongoDB database with collections, indexes, and validation
// Database: pdet_solar_analysis
// ============================================================================

// Connect to database
use pdet_solar_analysis;

print("=".repeat(80));
print("Initializing PDET Solar Analysis Database");
print("=".repeat(80));

// ============================================================================
// 1. CREATE COLLECTIONS
// ============================================================================

print("\n1. Creating collections...\n");

// Collection: pdet_municipalities
print("   - Creating collection: pdet_municipalities");
db.createCollection("pdet_municipalities", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["muni_code", "dept_code", "muni_name", "dept_name", "geom"],
            properties: {
                dept_code: {
                    bsonType: "string",
                    description: "Department code (2 digits)"
                },
                muni_code: {
                    bsonType: "string",
                    description: "Municipality code (5 digits DIVIPOLA)"
                },
                dept_name: {
                    bsonType: "string",
                    description: "Department name"
                },
                muni_name: {
                    bsonType: "string",
                    description: "Municipality name"
                },
                pdet_region: {
                    bsonType: "string",
                    description: "PDET region name"
                },
                pdet_subregion: {
                    bsonType: "string",
                    description: "PDET subregion name"
                },
                geom: {
                    bsonType: "object",
                    required: ["type", "coordinates"],
                    properties: {
                        type: {
                            enum: ["Polygon", "MultiPolygon"],
                            description: "GeoJSON geometry type"
                        },
                        coordinates: {
                            bsonType: "array",
                            description: "GeoJSON coordinates array"
                        }
                    }
                },
                area_km2: {
                    bsonType: "double",
                    description: "Municipality area in square kilometers"
                },
                data_source: {
                    bsonType: "string",
                    description: "Data source (e.g., DANE MGN)"
                },
                created_at: {
                    bsonType: "date",
                    description: "Document creation timestamp"
                },
                updated_at: {
                    bsonType: "date",
                    description: "Last update timestamp"
                }
            }
        }
    }
});

// Collection: buildings_microsoft
print("   - Creating collection: buildings_microsoft");
db.createCollection("buildings_microsoft", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["geom", "area_m2"],
            properties: {
                muni_code: {
                    bsonType: "string",
                    description: "Municipality code where building is located"
                },
                geom: {
                    bsonType: "object",
                    required: ["type", "coordinates"],
                    properties: {
                        type: {
                            enum: ["Polygon", "MultiPolygon"],
                            description: "GeoJSON geometry type"
                        },
                        coordinates: {
                            bsonType: "array",
                            description: "GeoJSON coordinates array"
                        }
                    }
                },
                area_m2: {
                    bsonType: "double",
                    description: "Building footprint area in square meters"
                },
                data_source: {
                    bsonType: "string",
                    description: "Data source (Microsoft Building Footprints)"
                },
                source_date: {
                    bsonType: "string",
                    description: "Date when imagery was captured"
                },
                created_at: {
                    bsonType: "date",
                    description: "Document creation timestamp"
                }
            }
        }
    }
});

// Collection: buildings_google
print("   - Creating collection: buildings_google");
db.createCollection("buildings_google", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["geom", "area_m2"],
            properties: {
                muni_code: {
                    bsonType: "string",
                    description: "Municipality code where building is located"
                },
                geom: {
                    bsonType: "object",
                    required: ["type", "coordinates"],
                    properties: {
                        type: {
                            enum: ["Polygon", "MultiPolygon"],
                            description: "GeoJSON geometry type"
                        },
                        coordinates: {
                            bsonType: "array",
                            description: "GeoJSON coordinates array"
                        }
                    }
                },
                area_m2: {
                    bsonType: "double",
                    description: "Building footprint area in square meters"
                },
                confidence: {
                    bsonType: "double",
                    description: "Confidence score (0-1)"
                },
                data_source: {
                    bsonType: "string",
                    description: "Data source (Google Open Buildings)"
                },
                created_at: {
                    bsonType: "date",
                    description: "Document creation timestamp"
                }
            }
        }
    }
});

print("\n✓ Collections created successfully\n");

// ============================================================================
// 2. CREATE SPATIAL INDEXES (2dsphere)
// ============================================================================

print("2. Creating spatial indexes (2dsphere)...\n");

print("   - Creating 2dsphere index on pdet_municipalities.geom");
db.pdet_municipalities.createIndex(
    { geom: "2dsphere" },
    { name: "geom_2dsphere" }
);

print("   - Creating 2dsphere index on buildings_microsoft.geom");
db.buildings_microsoft.createIndex(
    { geom: "2dsphere" },
    { name: "geom_2dsphere" }
);

print("   - Creating 2dsphere index on buildings_google.geom");
db.buildings_google.createIndex(
    { geom: "2dsphere" },
    { name: "geom_2dsphere" }
);

print("\n✓ Spatial indexes created successfully\n");

// ============================================================================
// 3. CREATE ADDITIONAL INDEXES
// ============================================================================

print("3. Creating additional indexes for performance...\n");

// Indexes for pdet_municipalities
print("   - Indexes for pdet_municipalities:");
db.pdet_municipalities.createIndex(
    { muni_code: 1 },
    { unique: true, name: "muni_code_unique" }
);
print("     ✓ muni_code (unique)");

db.pdet_municipalities.createIndex(
    { dept_code: 1 },
    { name: "dept_code_idx" }
);
print("     ✓ dept_code");

db.pdet_municipalities.createIndex(
    { pdet_region: 1 },
    { name: "pdet_region_idx" }
);
print("     ✓ pdet_region");

db.pdet_municipalities.createIndex(
    { pdet_subregion: 1 },
    { name: "pdet_subregion_idx" }
);
print("     ✓ pdet_subregion");

// Indexes for buildings_microsoft
print("\n   - Indexes for buildings_microsoft:");
db.buildings_microsoft.createIndex(
    { muni_code: 1 },
    { name: "muni_code_idx" }
);
print("     ✓ muni_code");

db.buildings_microsoft.createIndex(
    { area_m2: 1 },
    { name: "area_m2_idx" }
);
print("     ✓ area_m2");

db.buildings_microsoft.createIndex(
    { muni_code: 1, area_m2: -1 },
    { name: "muni_code_area_idx" }
);
print("     ✓ muni_code + area_m2 (compound)");

// Indexes for buildings_google
print("\n   - Indexes for buildings_google:");
db.buildings_google.createIndex(
    { muni_code: 1 },
    { name: "muni_code_idx" }
);
print("     ✓ muni_code");

db.buildings_google.createIndex(
    { area_m2: 1 },
    { name: "area_m2_idx" }
);
print("     ✓ area_m2");

db.buildings_google.createIndex(
    { confidence: 1 },
    { name: "confidence_idx" }
);
print("     ✓ confidence");

db.buildings_google.createIndex(
    { muni_code: 1, area_m2: -1 },
    { name: "muni_code_area_idx" }
);
print("     ✓ muni_code + area_m2 (compound)");

print("\n✓ Additional indexes created successfully\n");

// ============================================================================
// 4. DATABASE STATUS
// ============================================================================

print("=".repeat(80));
print("Database Initialization Complete!");
print("=".repeat(80));

print("\nDatabase Status:");
print("   Database: " + db.getName());
print("   Collections: " + db.getCollectionNames().length);

print("\nCollections:");
db.getCollectionNames().forEach(function(collName) {
    var count = db.getCollection(collName).countDocuments();
    var indexes = db.getCollection(collName).getIndexes();
    print("   - " + collName + ": " + count + " documents, " + indexes.length + " indexes");
});

print("\n" + "=".repeat(80));
print("Ready to load data!");
print("=".repeat(80));
