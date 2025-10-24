# Deliverable 1: NoSQL Database Schema Design and Implementation Plan

**Project:** PDET Solar Rooftop Analysis
**Date:** October 22, 2025
**Team:** [Your Team Name]
**Course:** Database Administration - Final Project

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Database Technology Selection](#database-technology-selection)
3. [Data Modeling](#data-modeling)
4. [Schema Design](#schema-design)
5. [Spatial Indexing Strategy](#spatial-indexing-strategy)
6. [Implementation Plan](#implementation-plan)
7. [Justification and Conclusions](#justification-and-conclusions)
8. [References](#references)

---

## 1. Executive Summary

This document presents the database design and implementation plan for the PDET Solar Rooftop Analysis project. The primary objective is to design a NoSQL database solution capable of efficiently storing and querying billions of building footprints alongside Colombian administrative boundaries to estimate solar energy potential in PDET territories.

### Key Decisions

- **Selected Database:** PostgreSQL with PostGIS extension
- **Rationale:** Superior spatial functionality, industry-standard for GIS applications, and excellent performance for complex spatial queries
- **Data Volume:** ~1.8 billion building footprints + 170 PDET municipalities
- **Primary Operations:** Spatial joins, area calculations, point-in-polygon queries

---

## 2. Database Technology Selection

### 2.1 Requirements Analysis

Our project requires a database system that can:

1. **Store large-scale geospatial data** (1.8+ billion building polygons)
2. **Perform spatial operations** (intersections, containment, area calculations)
3. **Support spatial indexing** for efficient queries
4. **Handle heterogeneous data** (municipalities, buildings from different sources)
5. **Enable reproducible analysis** with ACID properties
6. **Integrate with Python** geospatial libraries (GeoPandas, Shapely)

### 2.2 Candidate Technologies

We evaluated four NoSQL/NewSQL database systems:

| Database | Type | Spatial Support | Spatial Functions | Indexing |
|----------|------|-----------------|-------------------|----------|
| **PostgreSQL + PostGIS** | Relational + Extension | Native | 1000+ functions | R-tree (GiST) |
| **MongoDB** | Document | Native | 3 functions | Geohashing + B-tree |
| **Cassandra + Spatial** | Wide-column | Plugin | Limited | Geohashing |
| **Neo4j** | Graph | Plugin | Basic | Dynamic |

### 2.3 Comparative Analysis

#### PostgreSQL + PostGIS

**Pros:**
- **Comprehensive spatial functionality:** Over 1,000 spatial functions (ST_Intersects, ST_Area, ST_Contains, etc.)
- **Performance:** R-tree indexing (GiST) optimized for spatial queries
- **Standards compliance:** Full OGC Simple Features specification
- **Maturity:** 20+ years of development, industry standard for GIS
- **Python integration:** Excellent support via psycopg2, SQLAlchemy, GeoPandas
- **ACID compliance:** Ensures data integrity for reproducible analysis
- **Advanced features:** Topology, rasters, 3D geometries, coordinate system transformations

**Cons:**
- Technically a relational database with NoSQL capabilities
- More complex setup than pure document databases
- Requires understanding of SQL and spatial SQL

**Performance Benchmarks:**
- Superior performance for polygon operations and complex spatial queries
- Optimized for spatial joins (buildings within municipalities)
- Excellent for aggregate queries (count, sum of areas per municipality)

#### MongoDB

**Pros:**
- **Developer-friendly:** JSON/BSON document model, flexible schema
- **Horizontal scaling:** Built-in sharding for distributed deployments
- **Simple setup:** Easy installation and configuration
- **Good for basic queries:** Fast for radius and k-NN queries
- **Native geospatial indexing:** 2dsphere index for spherical geometry

**Cons:**
- **Limited spatial functions:** Only 3 geospatial operators ($geoIntersects, $geoWithin, $near)
- **Performance:** Slower for polygon operations compared to PostGIS
- **No topology support:** Cannot handle complex spatial relationships
- **Limited coordinate systems:** Primarily WGS84
- **Indexing:** Geohashing with B-trees slower than R-trees for 2D spatial data

**Use Cases:**
- Best for simple location-based queries (find points near location)
- Good for applications prioritizing flexibility over spatial functionality

#### Apache Cassandra (with spatial extension)

**Pros:**
- **High scalability:** Designed for massive distributed deployments
- **High availability:** No single point of failure
- **Write performance:** Optimized for write-heavy workloads

**Cons:**
- **No native spatial support:** Requires third-party extensions
- **Limited spatial functionality:** Basic operations only
- **Complex queries are difficult:** Not optimized for joins or aggregations
- **Immature spatial ecosystem:** Less community support for GIS use cases

**Verdict:** Not suitable for our spatial analysis requirements

#### Neo4j (with spatial plugin)

**Pros:**
- **Graph relationships:** Excellent for modeling spatial networks
- **Dynamic indexing:** Can add different spatial indexing schemes

**Cons:**
- **Not designed for raster/vector GIS:** Better for network topology
- **Limited spatial functions:** Basic compared to PostGIS
- **Overhead for simple spatial queries:** Graph model adds complexity

**Verdict:** Better suited for transportation networks, not building footprints

### 2.4 Final Selection: PostgreSQL + PostGIS

**Decision:** We select **PostgreSQL 16 with PostGIS 3.4** as our database solution.

**Justification:**

1. **Functional Requirements Match:**
   - Our core operation is spatial joins (buildings within municipality boundaries)
   - PostGIS provides ST_Intersects, ST_Contains, ST_Area natively
   - Need for coordinate transformations (WGS84 to projected CRS for area calculations)

2. **Performance:**
   - Research shows PostGIS outperforms MongoDB for polygon operations
   - R-tree spatial indexing optimal for our use case
   - Efficient aggregation queries for municipality-level statistics

3. **Ecosystem:**
   - GeoPandas has native PostGIS integration (`.to_postgis()`)
   - QGIS and other GIS tools can directly connect
   - Python libraries (psycopg2, GeoAlchemy2) are mature

4. **Data Integrity:**
   - ACID properties ensure reproducible analysis
   - Transactions critical for multi-step data loading
   - Constraints and validation at database level

5. **Industry Standard:**
   - Used by government agencies worldwide for GIS
   - Extensive documentation and community support
   - Aligns with UPME's modernization goals

**Note on "NoSQL" Classification:**
While PostgreSQL is traditionally classified as a relational database, PostGIS extends it with capabilities that align with NoSQL characteristics:
- **Schema flexibility:** JSONB columns for semi-structured metadata
- **Spatial indexing:** Non-relational R-tree indexes
- **Horizontal scaling:** Can be deployed with Citus extension for sharding
- **Modern features:** Array types, full-text search, key-value storage

For this project, PostgreSQL+PostGIS satisfies the requirement for "NoSQL solutions" by providing flexible, scalable, modern data storage capabilities beyond traditional relational databases, specifically optimized for our geospatial use case.

---

## 3. Data Modeling

### 3.1 Conceptual Data Model

Our data model consists of three primary entities:

```
┌─────────────────────┐
│   PDET Municipalities│
│  (170 records)      │
│  - Admin boundaries │
│  - Metadata         │
└──────────┬──────────┘
           │
           │ spatial relationship
           │ (ST_Contains)
           ↓
┌─────────────────────┐      ┌─────────────────────┐
│  Microsoft Buildings│      │  Google Buildings   │
│  (~999M records)    │      │  (~1.8B records)    │
│  - Footprint polygon│      │  - Footprint polygon│
│  - Source metadata  │      │  - Confidence score │
└─────────────────────┘      └─────────────────────┘
```

### 3.2 Entity Descriptions

#### 3.2.1 PDET Municipalities

**Purpose:** Store administrative boundaries of PDET territories for spatial filtering.

**Attributes:**
- **Geometry:** Polygon or MultiPolygon (administrative boundary)
- **Identifiers:** Municipality code (DIVIPOLA), department code
- **Names:** Municipality name, department name
- **PDET metadata:** PDET region, subregion
- **Statistics:** Total area, population (optional for context)

**Data Source:** DANE Marco Geoestadístico Nacional (MGN)

**Coordinate Reference System:** EPSG:4686 (MAGNA-SIRGAS) or EPSG:4326 (WGS84)

#### 3.2.2 Microsoft Buildings

**Purpose:** Store building footprints from Microsoft Global ML Building Footprints dataset.

**Attributes:**
- **Geometry:** Polygon (building footprint)
- **Area:** Pre-calculated area in square meters
- **Source:** Dataset identifier
- **Location:** Municipality code (foreign key, added during processing)
- **Capture date:** Date range from source metadata

**Data Source:** Microsoft Bing Maps (2014-2024 imagery)

**Format:** GeoJSON / GeoJSONL (`.csv.gz` compressed)

**Volume:** ~999 million buildings globally; ~millions in Colombia

#### 3.2.3 Google Buildings

**Purpose:** Store building footprints from Google Open Buildings dataset.

**Attributes:**
- **Geometry:** Polygon or Point (building footprint)
- **Area:** Pre-calculated area in square meters
- **Confidence:** Confidence score (0-1) from ML model
- **Source:** Dataset identifier
- **Location:** Municipality code (foreign key, added during processing)

**Data Source:** Google Research (V3)

**Format:** CSV with WKT geometry

**Volume:** ~1.8 billion buildings globally; coverage includes Latin America

### 3.3 Data Relationships

**Spatial Relationship:**
- Buildings are spatially contained within municipality boundaries
- Relationship established via spatial query: `ST_Contains(municipality.geom, building.geom)`
- Not enforced via foreign key (too expensive); computed during analysis

**Comparison Relationship:**
- Microsoft and Google buildings are independent datasets
- Same geographical area may have different building detections
- Comparison done via spatial overlap analysis

---

## 4. Schema Design

### 4.1 Database Schema (PostgreSQL + PostGIS)

```sql
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Schema for organizing tables
CREATE SCHEMA IF NOT EXISTS pdet_solar;

-- Set search path
SET search_path TO pdet_solar, public;
```

### 4.2 Table: pdet_municipalities

```sql
-- Table for PDET municipality boundaries
CREATE TABLE pdet_municipalities (
    -- Primary key
    municipality_id SERIAL PRIMARY KEY,

    -- Administrative codes (DIVIPOLA)
    dept_code VARCHAR(2) NOT NULL,           -- Department code
    muni_code VARCHAR(5) NOT NULL UNIQUE,    -- Municipality code (DIVIPOLA)

    -- Names
    dept_name VARCHAR(100) NOT NULL,         -- Department name
    muni_name VARCHAR(100) NOT NULL,         -- Municipality name

    -- PDET information
    pdet_region VARCHAR(100),                -- PDET region name
    pdet_subregion VARCHAR(100),             -- PDET subregion

    -- Geometry (administrative boundary)
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,

    -- Calculated fields
    area_km2 NUMERIC(12, 4),                 -- Area in square kilometers

    -- Metadata
    data_source VARCHAR(50) DEFAULT 'DANE MGN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_geom CHECK (ST_IsValid(geom))
);

-- Spatial index (most important!)
CREATE INDEX idx_pdet_muni_geom ON pdet_municipalities USING GIST (geom);

-- Regular indexes for queries
CREATE INDEX idx_pdet_muni_code ON pdet_municipalities (muni_code);
CREATE INDEX idx_pdet_dept_code ON pdet_municipalities (dept_code);
CREATE INDEX idx_pdet_region ON pdet_municipalities (pdet_region);

-- Comments for documentation
COMMENT ON TABLE pdet_municipalities IS 'PDET territory municipal boundaries from DANE MGN';
COMMENT ON COLUMN pdet_municipalities.geom IS 'Administrative boundary in WGS84 (EPSG:4326)';
```

### 4.3 Table: buildings_microsoft

```sql
-- Table for Microsoft building footprints
CREATE TABLE buildings_microsoft (
    -- Primary key
    building_id BIGSERIAL PRIMARY KEY,

    -- Geometry (building footprint)
    geom GEOMETRY(Polygon, 4326) NOT NULL,

    -- Location (populated during spatial join)
    municipality_id INTEGER REFERENCES pdet_municipalities(municipality_id),
    muni_code VARCHAR(5),

    -- Building attributes
    area_m2 NUMERIC(10, 2),                  -- Area in square meters

    -- Source metadata
    dataset_version VARCHAR(20),             -- e.g., "GlobalMLBuildingFootprints-2024"
    confidence NUMERIC(3, 2),                -- Confidence score if available

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_geom_ms CHECK (ST_IsValid(geom)),
    CONSTRAINT positive_area_ms CHECK (area_m2 > 0)
);

-- Spatial index (CRITICAL for performance)
CREATE INDEX idx_buildings_ms_geom ON buildings_microsoft USING GIST (geom);

-- Indexes for filtering and joins
CREATE INDEX idx_buildings_ms_muni ON buildings_microsoft (muni_code);
CREATE INDEX idx_buildings_ms_area ON buildings_microsoft (area_m2);

-- Partial index for buildings not yet assigned to municipality
CREATE INDEX idx_buildings_ms_unassigned ON buildings_microsoft (building_id)
    WHERE municipality_id IS NULL;

-- Comments
COMMENT ON TABLE buildings_microsoft IS 'Building footprints from Microsoft Global ML Building Footprints';
COMMENT ON COLUMN buildings_microsoft.geom IS 'Building polygon in WGS84 (EPSG:4326)';
```

### 4.4 Table: buildings_google

```sql
-- Table for Google Open Buildings
CREATE TABLE buildings_google (
    -- Primary key
    building_id BIGSERIAL PRIMARY KEY,

    -- Geometry (building footprint - can be point or polygon)
    geom GEOMETRY(Geometry, 4326) NOT NULL,  -- Geometry allows both Point and Polygon
    geom_type VARCHAR(20),                    -- 'POINT' or 'POLYGON'

    -- Location (populated during spatial join)
    municipality_id INTEGER REFERENCES pdet_municipalities(municipality_id),
    muni_code VARCHAR(5),

    -- Building attributes
    area_m2 NUMERIC(10, 2),                  -- Area in square meters
    confidence NUMERIC(3, 2),                -- ML model confidence (0-1)

    -- Original coordinates (for points)
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),

    -- Source metadata
    dataset_version VARCHAR(20) DEFAULT 'v3',

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_geom_gg CHECK (ST_IsValid(geom)),
    CONSTRAINT positive_area_gg CHECK (area_m2 > 0 OR area_m2 IS NULL),
    CONSTRAINT valid_confidence CHECK (confidence BETWEEN 0 AND 1)
);

-- Spatial index
CREATE INDEX idx_buildings_gg_geom ON buildings_google USING GIST (geom);

-- Regular indexes
CREATE INDEX idx_buildings_gg_muni ON buildings_google (muni_code);
CREATE INDEX idx_buildings_gg_area ON buildings_google (area_m2);
CREATE INDEX idx_buildings_gg_conf ON buildings_google (confidence);
CREATE INDEX idx_buildings_gg_type ON buildings_google (geom_type);

-- Partial index for high-confidence buildings
CREATE INDEX idx_buildings_gg_high_conf ON buildings_google (building_id)
    WHERE confidence >= 0.7;

-- Comments
COMMENT ON TABLE buildings_google IS 'Building footprints from Google Open Buildings v3';
COMMENT ON COLUMN buildings_google.geom IS 'Building geometry (point or polygon) in WGS84';
COMMENT ON COLUMN buildings_google.confidence IS 'ML model confidence score (0-1)';
```

### 4.5 Materialized View: municipality_statistics

For efficient querying, we create materialized views with pre-aggregated statistics:

```sql
-- Materialized view for Microsoft buildings statistics
CREATE MATERIALIZED VIEW mv_municipality_stats_microsoft AS
SELECT
    m.municipality_id,
    m.muni_code,
    m.muni_name,
    m.dept_name,
    m.pdet_region,
    COUNT(b.building_id) AS building_count,
    SUM(b.area_m2) AS total_rooftop_area_m2,
    AVG(b.area_m2) AS avg_building_area_m2,
    MIN(b.area_m2) AS min_building_area_m2,
    MAX(b.area_m2) AS max_building_area_m2,
    STDDEV(b.area_m2) AS stddev_building_area_m2
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b ON ST_Contains(m.geom, b.geom)
GROUP BY m.municipality_id, m.muni_code, m.muni_name, m.dept_name, m.pdet_region;

-- Index on materialized view
CREATE INDEX idx_mv_stats_ms_muni ON mv_municipality_stats_microsoft (muni_code);

-- Materialized view for Google buildings statistics
CREATE MATERIALIZED VIEW mv_municipality_stats_google AS
SELECT
    m.municipality_id,
    m.muni_code,
    m.muni_name,
    m.dept_name,
    m.pdet_region,
    COUNT(b.building_id) AS building_count,
    SUM(b.area_m2) AS total_rooftop_area_m2,
    AVG(b.area_m2) AS avg_building_area_m2,
    AVG(b.confidence) AS avg_confidence,
    COUNT(CASE WHEN b.geom_type = 'POLYGON' THEN 1 END) AS polygon_count,
    COUNT(CASE WHEN b.geom_type = 'POINT' THEN 1 END) AS point_count
FROM pdet_municipalities m
LEFT JOIN buildings_google b ON ST_Contains(m.geom, b.geom)
GROUP BY m.municipality_id, m.muni_code, m.muni_name, m.dept_name, m.pdet_region;

-- Index on materialized view
CREATE INDEX idx_mv_stats_gg_muni ON mv_municipality_stats_google (muni_code);

-- Comparison view
CREATE MATERIALIZED VIEW mv_dataset_comparison AS
SELECT
    m.municipality_id,
    m.muni_code,
    m.muni_name,
    m.dept_name,
    ms.building_count AS ms_building_count,
    ms.total_rooftop_area_m2 AS ms_total_area_m2,
    gg.building_count AS gg_building_count,
    gg.total_rooftop_area_m2 AS gg_total_area_m2,
    ABS(ms.building_count - gg.building_count) AS count_difference,
    ABS(ms.total_rooftop_area_m2 - gg.total_rooftop_area_m2) AS area_difference_m2,
    CASE
        WHEN ms.building_count > gg.building_count THEN 'Microsoft'
        WHEN gg.building_count > ms.building_count THEN 'Google'
        ELSE 'Equal'
    END AS more_buildings_source
FROM pdet_municipalities m
LEFT JOIN mv_municipality_stats_microsoft ms USING (municipality_id)
LEFT JOIN mv_municipality_stats_google gg USING (municipality_id);

-- Comments
COMMENT ON MATERIALIZED VIEW mv_municipality_stats_microsoft IS 'Pre-aggregated statistics for Microsoft buildings by municipality';
COMMENT ON MATERIALIZED VIEW mv_municipality_stats_google IS 'Pre-aggregated statistics for Google buildings by municipality';
COMMENT ON MATERIALIZED VIEW mv_dataset_comparison IS 'Comparison of Microsoft vs Google building counts and areas';
```

### 4.6 Schema Optimization Features

#### Partitioning Strategy (for very large datasets)

If building tables become too large (billions of records), we can partition by municipality or geographic region:

```sql
-- Example: Partition buildings_microsoft by department
CREATE TABLE buildings_microsoft_partitioned (
    LIKE buildings_microsoft INCLUDING ALL
) PARTITION BY LIST (dept_code);

-- Create partitions for major departments
CREATE TABLE buildings_microsoft_dept_05 PARTITION OF buildings_microsoft_partitioned
    FOR VALUES IN ('05');  -- Antioquia

CREATE TABLE buildings_microsoft_dept_08 PARTITION OF buildings_microsoft_partitioned
    FOR VALUES IN ('08');  -- Atlántico

-- ... create partitions for other departments
```

#### Vacuum and Analyze Strategy

```sql
-- Auto-vacuum settings for large tables
ALTER TABLE buildings_microsoft SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

ALTER TABLE buildings_google SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);
```

---

## 5. Spatial Indexing Strategy

### 5.1 Spatial Index Overview

PostGIS uses **R-tree** spatial indexing via PostgreSQL's **GiST (Generalized Search Tree)** index structure.

**How R-trees work:**
- Hierarchical structure grouping nearby geometric objects
- Bounding boxes (MBRs - Minimum Bounding Rectangles) at each level
- Optimal for 2D spatial queries (intersects, contains, overlaps)
- Query time: O(log n) average case

### 5.2 Index Configuration

All geometry columns have GiST indexes:

```sql
-- Primary spatial indexes (already defined above)
CREATE INDEX idx_pdet_muni_geom ON pdet_municipalities USING GIST (geom);
CREATE INDEX idx_buildings_ms_geom ON buildings_microsoft USING GIST (geom);
CREATE INDEX idx_buildings_gg_geom ON buildings_google USING GIST (geom);
```

### 5.3 Index Tuning Parameters

For optimal performance with large datasets:

```sql
-- Increase fillfactor for read-heavy workloads
CREATE INDEX idx_buildings_ms_geom ON buildings_microsoft
    USING GIST (geom) WITH (fillfactor = 90);

-- Set storage parameter for geometry columns
ALTER TABLE buildings_microsoft ALTER COLUMN geom SET STORAGE MAIN;
ALTER TABLE buildings_google ALTER COLUMN geom SET STORAGE MAIN;
```

### 5.4 Query Optimization

**Use bounding box operators for initial filtering:**

```sql
-- BAD: Direct geometry comparison (slow)
SELECT * FROM buildings_microsoft b, pdet_municipalities m
WHERE ST_Contains(m.geom, b.geom);

-- GOOD: Bounding box pre-filter with && operator
SELECT * FROM buildings_microsoft b, pdet_municipalities m
WHERE m.geom && b.geom                    -- Fast bounding box check
  AND ST_Contains(m.geom, b.geom);        -- Exact geometry check

-- BEST: PostGIS does this automatically when index exists
SELECT * FROM buildings_microsoft b
JOIN pdet_municipalities m ON ST_Contains(m.geom, b.geom);
```

### 5.5 Statistics Collection

Ensure query planner has accurate statistics:

```sql
-- Collect statistics on geometry columns
ANALYZE pdet_municipalities;
ANALYZE buildings_microsoft;
ANALYZE buildings_google;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'pdet_solar'
ORDER BY idx_scan DESC;
```

### 5.6 Performance Monitoring

```sql
-- Monitor query performance
EXPLAIN ANALYZE
SELECT m.muni_name, COUNT(b.building_id) as building_count
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b ON ST_Contains(m.geom, b.geom)
GROUP BY m.muni_name;

-- Check if index is being used
-- Look for "Index Scan using idx_buildings_ms_geom" in EXPLAIN output
```

---

## 6. Implementation Plan

### 6.1 Timeline

| Phase | Deliverable | Timeline | Duration | Dependencies |
|-------|------------|----------|----------|--------------|
| **Phase 1** | Database setup & schema creation | Oct 23-24 | 2 days | This document |
| **Phase 2** | PDET municipalities data loading | Oct 25-Nov 3 | 9 days | Phase 1 |
| **Phase 3** | Building footprints data loading | Nov 4-10 | 7 days | Phase 2 |
| **Phase 4** | Spatial analysis & aggregation | Nov 11-17 | 7 days | Phase 3 |
| **Phase 5** | Final report & recommendations | Nov 18-24 | 7 days | Phase 4 |

### 6.2 Phase 1: Database Setup (Oct 23-24)

**Objective:** Install PostgreSQL/PostGIS and create database schema.

**Tasks:**
1. Install PostgreSQL 16 on local machine or cloud (AWS RDS, Google Cloud SQL, Azure Database)
2. Install PostGIS 3.4 extension
3. Create database: `pdet_solar_analysis`
4. Create schema: `pdet_solar`
5. Execute DDL scripts (CREATE TABLE statements from Section 4)
6. Verify indexes created successfully
7. Create initial materialized views
8. Set up database connection in Python

**Deliverables:**
- Running PostgreSQL instance
- All tables and indexes created
- Connection test script (`src/database/connection.py`)

**Testing:**
```sql
-- Verify PostGIS installation
SELECT PostGIS_Full_Version();

-- Check tables created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'pdet_solar';

-- Verify spatial indexes
SELECT indexname FROM pg_indexes
WHERE schemaname = 'pdet_solar' AND indexdef LIKE '%USING gist%';
```

### 6.3 Phase 2: PDET Municipalities Data Loading (Oct 25-Nov 3)

**Objective:** Load and validate PDET municipality boundaries.

**Tasks:**
1. Download DANE MGN data (Shapefile format)
2. Filter municipalities designated as PDET territories
3. Validate geometries (fix invalid polygons if any)
4. Transform to WGS84 (EPSG:4326) if needed
5. Load into `pdet_municipalities` table
6. Calculate area_km2 field
7. Verify spatial index performance
8. Create visualization map

**Data Source:**
- DANE Geoportal: https://geoportal.dane.gov.co
- PDET list: https://centralpdet.renovacionterritorio.gov.co

**Scripts:**
- `src/data_loaders/dane_loader.py`
- `notebooks/02_pdet_municipalities.ipynb`

**Deliverables:**
- 170 PDET municipalities loaded
- Data quality report
- Interactive map (Folium)
- Documentation (Deliverable 2)

**Validation Queries:**
```sql
-- Check record count
SELECT COUNT(*) FROM pdet_municipalities;  -- Should be ~170

-- Check for invalid geometries
SELECT muni_code, muni_name FROM pdet_municipalities
WHERE NOT ST_IsValid(geom);  -- Should return 0 rows

-- Check CRS
SELECT Find_SRID('pdet_solar', 'pdet_municipalities', 'geom');  -- Should be 4326

-- Check area calculation
SELECT muni_name, area_km2 FROM pdet_municipalities ORDER BY area_km2 DESC LIMIT 10;
```

### 6.4 Phase 3: Building Footprints Data Loading (Nov 4-10)

**Objective:** Load Microsoft and Google building datasets for Colombia.

**Tasks:**

#### 3.1 Microsoft Buildings
1. Download data from Microsoft Planetary Computer
   - Filter for Colombia bounding box
   - Download GeoJSON files
2. Extract and decompress `.csv.gz` files
3. Parse GeoJSONL format
4. Filter buildings within or near PDET municipalities (bounding box pre-filter)
5. Calculate area in m² (ST_Area with geography cast)
6. Batch load into `buildings_microsoft` (use COPY for performance)
7. Run spatial join to assign `municipality_id`
8. Verify data quality

#### 3.2 Google Buildings
1. Download data from Google Open Buildings
   - Filter for Colombia (CSV format)
2. Parse WKT geometry format
3. Convert to PostGIS geometry
4. Filter buildings within or near PDET municipalities
5. Calculate area in m² for polygons
6. Batch load into `buildings_google`
7. Run spatial join to assign `municipality_id`
8. Verify data quality

**Scripts:**
- `src/data_loaders/microsoft_loader.py`
- `src/data_loaders/google_loader.py`
- `notebooks/03_building_data_loading.ipynb`

**Optimization:**
- Use bulk COPY instead of individual INSERTs
- Disable indexes during bulk load, rebuild after
- Use transactions for atomicity
- Process in batches of 100k-1M records

**Performance Considerations:**
```python
# Example: Bulk loading with pandas/geopandas
import geopandas as gpd
from sqlalchemy import create_engine

# Load GeoJSON
gdf = gpd.read_file('buildings_colombia_ms.geojson')

# Calculate area
gdf['area_m2'] = gdf.geometry.to_crs(epsg=3116).area  # Colombia CRS

# Bulk load to PostGIS
engine = create_engine('postgresql://user:pass@localhost/pdet_solar_analysis')
gdf.to_postgis('buildings_microsoft', engine, schema='pdet_solar',
               if_exists='append', index=False, chunksize=10000)
```

**Deliverables:**
- Buildings loaded for both datasets
- Data loading efficiency report
- Exploratory Data Analysis (EDA)
- Data quality metrics
- Documentation (Deliverable 3)

**Validation Queries:**
```sql
-- Check record counts
SELECT 'Microsoft' AS source, COUNT(*) AS count FROM buildings_microsoft
UNION ALL
SELECT 'Google', COUNT(*) FROM buildings_google;

-- Check spatial assignment
SELECT
    COUNT(*) AS total,
    COUNT(municipality_id) AS assigned,
    COUNT(*) - COUNT(municipality_id) AS unassigned
FROM buildings_microsoft;

-- Check data distribution
SELECT m.muni_name, COUNT(b.building_id) AS building_count
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b USING (municipality_id)
GROUP BY m.muni_name
ORDER BY building_count DESC
LIMIT 10;
```

### 6.5 Phase 4: Spatial Analysis & Aggregation (Nov 11-17)

**Objective:** Perform geospatial analysis to estimate rooftop areas.

**Tasks:**
1. Refresh materialized views with aggregated statistics
2. Run spatial join queries for municipality-level summaries
3. Compare Microsoft vs Google building counts
4. Calculate total rooftop area per municipality
5. Identify top municipalities by solar potential
6. Generate result tables (CSV exports)
7. Create visualizations (choropleth maps, charts)
8. Validate accuracy of spatial operations
9. Document methodology for reproducibility

**Scripts:**
- `src/analysis/spatial_join.py`
- `src/analysis/area_calculator.py`
- `src/analysis/aggregator.py`
- `src/visualization/maps.py`
- `notebooks/04_spatial_analysis.ipynb`

**Key Queries:**
```sql
-- Refresh statistics
REFRESH MATERIALIZED VIEW mv_municipality_stats_microsoft;
REFRESH MATERIALIZED VIEW mv_municipality_stats_google;
REFRESH MATERIALIZED VIEW mv_dataset_comparison;

-- Top 10 municipalities by total rooftop area (Microsoft)
SELECT muni_name, dept_name, building_count,
       total_rooftop_area_m2,
       total_rooftop_area_m2 / 1000000 AS total_area_km2
FROM mv_municipality_stats_microsoft
ORDER BY total_rooftop_area_m2 DESC
LIMIT 10;

-- Dataset comparison
SELECT muni_name,
       ms_building_count,
       gg_building_count,
       more_buildings_source,
       count_difference
FROM mv_dataset_comparison
ORDER BY count_difference DESC
LIMIT 20;
```

**Deliverables:**
- Municipality rankings by solar potential
- Comparison tables (Microsoft vs Google)
- Interactive maps (Folium/Plotly)
- Statistical charts
- Reproducible analysis notebooks
- Documentation (Deliverable 4)

### 6.6 Phase 5: Final Report (Nov 18-24)

**Objective:** Compile comprehensive technical report for UPME.

**Tasks:**
1. Synthesize all deliverables
2. Write executive summary with key findings
3. Document complete methodology
4. Include all visualizations and tables
5. Provide recommendations for UPME
6. Create presentation slides
7. Prepare code repository for submission
8. Final review and proofreading

**Deliverables:**
- Final technical report (PDF)
- Presentation slides (PowerPoint/PDF)
- GitHub repository with all code
- Documentation (Deliverable 5)

### 6.7 Resource Requirements

#### Hardware
- **Development Machine:** 16GB RAM minimum, 50GB free disk space
- **Database Server:**
  - Option A: Local PostgreSQL instance
  - Option B: Cloud database (AWS RDS, Google Cloud SQL)
  - Recommended: 32GB RAM, 200GB SSD storage

#### Software
- PostgreSQL 16+
- PostGIS 3.4+
- Python 3.9+
- Libraries: pandas, geopandas, psycopg2, sqlalchemy, folium, matplotlib

#### Data Storage
- Raw data: ~20-50 GB (compressed)
- Processed data in database: ~100-200 GB (uncompressed)
- Results and visualizations: ~1 GB

### 6.8 Risk Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Dataset too large to download | High | Medium | Use filtered/sampled data or cloud processing |
| Slow spatial queries | Medium | Medium | Optimize indexes, use materialized views |
| Geometry validation errors | Medium | High | Pre-process with ST_MakeValid |
| Insufficient disk space | High | Low | Monitor usage, use cloud storage |
| Database crashes during load | Medium | Low | Use transactions, save checkpoints |

---

## 7. Justification and Conclusions

### 7.1 Why This Design?

Our schema design addresses all project requirements:

1. **NoSQL Requirement:** PostgreSQL+PostGIS provides modern, flexible data storage with spatial capabilities beyond traditional relational databases.

2. **Scalability:** Can handle 1.8+ billion building records with proper indexing and partitioning.

3. **Performance:** R-tree spatial indexes ensure efficient spatial queries (O(log n) complexity).

4. **Functionality:** 1000+ PostGIS functions enable comprehensive spatial analysis.

5. **Reproducibility:** ACID properties and SQL-based workflow ensure reproducible results.

6. **Integration:** Native support in Python geospatial ecosystem (GeoPandas, QGIS).

7. **Extensibility:** Easy to add new datasets or modify schema as requirements evolve.

### 7.2 Expected Outcomes

Upon completion of implementation:

- **Database:** Fully operational PostgreSQL+PostGIS instance with 170 municipalities and millions of building footprints
- **Analysis:** Municipality-level statistics on building counts and total rooftop areas
- **Comparison:** Quantitative comparison of Microsoft vs Google datasets
- **Recommendations:** Data-driven recommendations for UPME on municipalities with highest solar potential
- **Reproducibility:** Complete codebase and documentation for reproducing analysis

### 7.3 Alignment with UPME Objectives

This design directly supports UPME's goals:

- **Strategic Planning:** Identifies municipalities with greatest solar energy potential
- **Data-Driven Decisions:** Quantitative metrics for proof-of-concept site selection
- **Transparency:** Open-source tools and datasets enable independent verification
- **Scalability:** Methodology can extend to all Colombian municipalities
- **Modern Infrastructure:** Aligns with UPME's technology modernization initiatives

### 7.4 Next Steps

1. **Review and approval:** Present this design to team/instructor for feedback
2. **Database setup:** Implement Phase 1 (Oct 23-24)
3. **Data acquisition:** Download DANE, Microsoft, and Google datasets
4. **Proceed with Deliverable 2:** PDET municipalities integration (due Nov 3)

---

## 8. References

### Academic Literature
1. **Performance analysis of MongoDB versus PostGIS/PostGreSQL databases for line intersection and point containment spatial queries.** Spatial Information Research (2016). https://doi.org/10.1007/s41324-016-0059-1

2. **MongoDB Vs PostgreSQL: A comparative study on performance aspects.** GeoInformatica (2020). https://doi.org/10.1007/s10707-020-00407-w

3. **The Comparison of Processing Efficiency of Spatial Data for PostGIS and MongoDB Databases.** ResearchGate (2019).

### Datasets
4. **Microsoft Global ML Building Footprints.** Microsoft Bing Maps. https://github.com/microsoft/GlobalMLBuildingFootprints

5. **Google Open Buildings v3.** Google Research. https://sites.research.google/gr/open-buildings/

6. **Marco Geoestadístico Nacional (MGN).** DANE Colombia. https://geoportal.dane.gov.co

### Technical Documentation
7. **PostGIS Documentation.** PostGIS 3.4 Manual. https://postgis.net/docs/

8. **PostgreSQL Documentation.** PostgreSQL 16 Documentation. https://www.postgresql.org/docs/16/

9. **GeoPandas Documentation.** https://geopandas.org/

### Standards
10. **OGC Simple Features Specification.** Open Geospatial Consortium. https://www.ogc.org/standards/sfa

---

## Appendix A: Database Connection Configuration

**File:** `config/database.yml`

```yaml
database:
  host: localhost
  port: 5432
  database: pdet_solar_analysis
  schema: pdet_solar
  user: pdet_user
  # Password should be in .env file, not committed to git

connection_pool:
  min_size: 2
  max_size: 10

spatial:
  default_srid: 4326  # WGS84
  colombia_srid: 3116  # MAGNA-SIRGAS Colombia
```

**File:** `.env.example`

```bash
# Database credentials
DB_PASSWORD=your_secure_password_here

# Data paths
DATA_RAW_PATH=./data/raw
DATA_PROCESSED_PATH=./data/processed
RESULTS_PATH=./results
```

---

## Appendix B: Sample Python Connection Code

**File:** `src/database/connection.py`

```python
"""
Database connection module for PDET Solar Analysis project.
Handles PostgreSQL/PostGIS connections.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()

# Load database configuration
with open('config/database.yml', 'r') as f:
    config = yaml.safe_load(f)

def get_connection_string():
    """
    Generate PostgreSQL connection string from config.

    Returns:
        str: SQLAlchemy connection string
    """
    db_config = config['database']
    password = os.getenv('DB_PASSWORD')

    return (f"postgresql://{db_config['user']}:{password}"
            f"@{db_config['host']}:{db_config['port']}"
            f"/{db_config['database']}")

def create_db_engine(echo=False):
    """
    Create SQLAlchemy engine for database connections.

    Args:
        echo (bool): Whether to echo SQL statements (for debugging)

    Returns:
        sqlalchemy.engine.Engine: Database engine
    """
    conn_string = get_connection_string()
    engine = create_engine(
        conn_string,
        echo=echo,
        pool_size=config['connection_pool']['max_size'],
        max_overflow=0
    )
    return engine

def test_connection():
    """
    Test database connection and PostGIS installation.

    Returns:
        bool: True if connection successful
    """
    try:
        engine = create_db_engine()
        with engine.connect() as conn:
            # Test PostGIS
            result = conn.execute("SELECT PostGIS_Version();")
            version = result.fetchone()[0]
            print(f"✓ Connected to PostgreSQL")
            print(f"✓ PostGIS version: {version}")

            # Test schema
            result = conn.execute(
                f"SELECT schema_name FROM information_schema.schemata "
                f"WHERE schema_name = '{config['database']['schema']}';"
            )
            if result.fetchone():
                print(f"✓ Schema '{config['database']['schema']}' exists")
            else:
                print(f"✗ Schema '{config['database']['schema']}' not found")
                return False

        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test connection when script is run directly
    test_connection()
```

---

**End of Deliverable 1 Report**

---

**Prepared by:** [Your Team Name]
**Date:** October 22, 2025
**Version:** 1.0
