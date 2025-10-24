/*
 * PDET Solar Rooftop Analysis - Database Schema Creation
 * PostgreSQL + PostGIS
 *
 * Purpose: Create database schema for storing PDET municipalities and building footprints
 * Author: PDET Analysis Team
 * Date: October 2025
 * Deliverable: 1
 */

-- ==============================================================================
-- STEP 1: Enable PostGIS Extension
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify PostGIS installation
SELECT PostGIS_Full_Version();

-- ==============================================================================
-- STEP 2: Create Schema
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS pdet_solar;

-- Set search path for current session
SET search_path TO pdet_solar, public;

-- Make search path default for database
ALTER DATABASE pdet_solar_analysis SET search_path TO pdet_solar, public;

COMMENT ON SCHEMA pdet_solar IS 'PDET Solar Rooftop Analysis - Geospatial data for solar energy potential estimation';

-- ==============================================================================
-- STEP 3: Create PDET Municipalities Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS pdet_municipalities (
    -- Primary key
    municipality_id SERIAL PRIMARY KEY,

    -- Administrative codes (DIVIPOLA - Colombia standard)
    dept_code VARCHAR(2) NOT NULL,           -- Department code (e.g., '05' for Antioquia)
    muni_code VARCHAR(5) NOT NULL UNIQUE,    -- Municipality code (e.g., '05001' for Medellín)

    -- Names
    dept_name VARCHAR(100) NOT NULL,         -- Department name
    muni_name VARCHAR(100) NOT NULL,         -- Municipality name

    -- PDET information
    pdet_region VARCHAR(100),                -- PDET region name
    pdet_subregion VARCHAR(100),             -- PDET subregion
    is_pdet BOOLEAN DEFAULT TRUE,            -- Flag for PDET territory

    -- Geometry (administrative boundary)
    -- Using MultiPolygon to handle islands and complex boundaries
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,

    -- Calculated fields
    area_km2 NUMERIC(12, 4),                 -- Area in square kilometers
    perimeter_km NUMERIC(12, 4),             -- Perimeter in kilometers

    -- Metadata
    data_source VARCHAR(50) DEFAULT 'DANE MGN',
    data_year INTEGER DEFAULT 2024,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_geom_muni CHECK (ST_IsValid(geom)),
    CONSTRAINT positive_area_muni CHECK (area_km2 > 0 OR area_km2 IS NULL)
);

-- Comments for documentation
COMMENT ON TABLE pdet_municipalities IS 'PDET territory municipal boundaries from DANE Marco Geoestadístico Nacional';
COMMENT ON COLUMN pdet_municipalities.municipality_id IS 'Primary key - auto-incrementing ID';
COMMENT ON COLUMN pdet_municipalities.muni_code IS 'DIVIPOLA municipality code (5 digits)';
COMMENT ON COLUMN pdet_municipalities.geom IS 'Administrative boundary polygon in WGS84 (EPSG:4326)';
COMMENT ON COLUMN pdet_municipalities.area_km2 IS 'Municipality area in square kilometers (calculated)';

-- ==============================================================================
-- STEP 4: Create Indexes for PDET Municipalities
-- ==============================================================================

-- Spatial index (MOST IMPORTANT for performance)
CREATE INDEX idx_pdet_muni_geom ON pdet_municipalities USING GIST (geom);

-- Regular indexes for filtering and joins
CREATE INDEX idx_pdet_muni_code ON pdet_municipalities (muni_code);
CREATE INDEX idx_pdet_dept_code ON pdet_municipalities (dept_code);
CREATE INDEX idx_pdet_region ON pdet_municipalities (pdet_region);
CREATE INDEX idx_pdet_is_pdet ON pdet_municipalities (is_pdet) WHERE is_pdet = TRUE;

-- ==============================================================================
-- STEP 5: Create Microsoft Buildings Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS buildings_microsoft (
    -- Primary key
    building_id BIGSERIAL PRIMARY KEY,

    -- Geometry (building footprint)
    geom GEOMETRY(Polygon, 4326) NOT NULL,

    -- Location (populated during spatial join)
    municipality_id INTEGER,
    muni_code VARCHAR(5),
    dept_code VARCHAR(2),

    -- Building attributes
    area_m2 NUMERIC(10, 2),                  -- Area in square meters
    perimeter_m NUMERIC(10, 2),              -- Perimeter in meters

    -- Source metadata
    dataset_version VARCHAR(50) DEFAULT 'GlobalMLBuildingFootprints-2024',
    confidence NUMERIC(3, 2),                -- Confidence score (if available)

    -- Centroid for quick location queries
    centroid GEOMETRY(Point, 4326),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_geom_ms CHECK (ST_IsValid(geom)),
    CONSTRAINT positive_area_ms CHECK (area_m2 > 0 OR area_m2 IS NULL),
    CONSTRAINT fk_municipality_ms FOREIGN KEY (municipality_id)
        REFERENCES pdet_municipalities(municipality_id) ON DELETE SET NULL
);

COMMENT ON TABLE buildings_microsoft IS 'Building footprints from Microsoft Global ML Building Footprints dataset';
COMMENT ON COLUMN buildings_microsoft.geom IS 'Building polygon footprint in WGS84 (EPSG:4326)';
COMMENT ON COLUMN buildings_microsoft.area_m2 IS 'Building rooftop area in square meters';
COMMENT ON COLUMN buildings_microsoft.centroid IS 'Building centroid for quick spatial lookups';

-- ==============================================================================
-- STEP 6: Create Indexes for Microsoft Buildings
-- ==============================================================================

-- Spatial indexes (CRITICAL for performance)
CREATE INDEX idx_buildings_ms_geom ON buildings_microsoft USING GIST (geom);
CREATE INDEX idx_buildings_ms_centroid ON buildings_microsoft USING GIST (centroid);

-- Regular indexes for filtering and joins
CREATE INDEX idx_buildings_ms_muni_id ON buildings_microsoft (municipality_id);
CREATE INDEX idx_buildings_ms_muni_code ON buildings_microsoft (muni_code);
CREATE INDEX idx_buildings_ms_area ON buildings_microsoft (area_m2);

-- Partial index for buildings not yet assigned to municipality
CREATE INDEX idx_buildings_ms_unassigned ON buildings_microsoft (building_id)
    WHERE municipality_id IS NULL;

-- ==============================================================================
-- STEP 7: Create Google Buildings Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS buildings_google (
    -- Primary key
    building_id BIGSERIAL PRIMARY KEY,

    -- Geometry (can be POINT or POLYGON in Google dataset)
    geom GEOMETRY(Geometry, 4326) NOT NULL,  -- Geometry type allows both
    geom_type VARCHAR(20),                    -- 'POINT' or 'POLYGON'

    -- Location (populated during spatial join)
    municipality_id INTEGER,
    muni_code VARCHAR(5),
    dept_code VARCHAR(2),

    -- Building attributes
    area_m2 NUMERIC(10, 2),                  -- Area in square meters
    confidence NUMERIC(3, 2),                -- ML model confidence score (0-1)

    -- Original coordinates (for point geometries)
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),

    -- Source metadata
    dataset_version VARCHAR(20) DEFAULT 'v3',

    -- Centroid (for polygon geometries)
    centroid GEOMETRY(Point, 4326),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_geom_gg CHECK (ST_IsValid(geom)),
    CONSTRAINT positive_area_gg CHECK (area_m2 > 0 OR area_m2 IS NULL),
    CONSTRAINT valid_confidence CHECK (confidence BETWEEN 0 AND 1 OR confidence IS NULL),
    CONSTRAINT fk_municipality_gg FOREIGN KEY (municipality_id)
        REFERENCES pdet_municipalities(municipality_id) ON DELETE SET NULL
);

COMMENT ON TABLE buildings_google IS 'Building footprints from Google Open Buildings v3 dataset';
COMMENT ON COLUMN buildings_google.geom IS 'Building geometry (point or polygon) in WGS84 (EPSG:4326)';
COMMENT ON COLUMN buildings_google.geom_type IS 'Geometry type: POINT or POLYGON';
COMMENT ON COLUMN buildings_google.confidence IS 'ML model confidence score (0-1)';

-- ==============================================================================
-- STEP 8: Create Indexes for Google Buildings
-- ==============================================================================

-- Spatial indexes
CREATE INDEX idx_buildings_gg_geom ON buildings_google USING GIST (geom);
CREATE INDEX idx_buildings_gg_centroid ON buildings_google USING GIST (centroid)
    WHERE centroid IS NOT NULL;

-- Regular indexes
CREATE INDEX idx_buildings_gg_muni_id ON buildings_google (municipality_id);
CREATE INDEX idx_buildings_gg_muni_code ON buildings_google (muni_code);
CREATE INDEX idx_buildings_gg_area ON buildings_google (area_m2);
CREATE INDEX idx_buildings_gg_conf ON buildings_google (confidence);
CREATE INDEX idx_buildings_gg_type ON buildings_google (geom_type);

-- Partial index for high-confidence buildings
CREATE INDEX idx_buildings_gg_high_conf ON buildings_google (building_id)
    WHERE confidence >= 0.7;

-- Partial index for polygon geometries
CREATE INDEX idx_buildings_gg_polygons ON buildings_google (building_id)
    WHERE geom_type = 'POLYGON';

-- ==============================================================================
-- STEP 9: Create Materialized Views for Statistics
-- ==============================================================================

-- Materialized view for Microsoft buildings statistics by municipality
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_municipality_stats_microsoft AS
SELECT
    m.municipality_id,
    m.muni_code,
    m.muni_name,
    m.dept_code,
    m.dept_name,
    m.pdet_region,
    m.pdet_subregion,
    COUNT(b.building_id) AS building_count,
    COALESCE(SUM(b.area_m2), 0) AS total_rooftop_area_m2,
    COALESCE(SUM(b.area_m2), 0) / 1000000 AS total_rooftop_area_km2,
    COALESCE(AVG(b.area_m2), 0) AS avg_building_area_m2,
    COALESCE(MIN(b.area_m2), 0) AS min_building_area_m2,
    COALESCE(MAX(b.area_m2), 0) AS max_building_area_m2,
    COALESCE(STDDEV(b.area_m2), 0) AS stddev_building_area_m2,
    -- Solar potential estimate (assuming 70% usable rooftop)
    COALESCE(SUM(b.area_m2), 0) * 0.7 AS estimated_usable_area_m2
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b ON m.municipality_id = b.municipality_id
GROUP BY m.municipality_id, m.muni_code, m.muni_name, m.dept_code,
         m.dept_name, m.pdet_region, m.pdet_subregion;

-- Index on materialized view
CREATE UNIQUE INDEX idx_mv_stats_ms_muni_id ON mv_municipality_stats_microsoft (municipality_id);
CREATE INDEX idx_mv_stats_ms_muni_code ON mv_municipality_stats_microsoft (muni_code);
CREATE INDEX idx_mv_stats_ms_area ON mv_municipality_stats_microsoft (total_rooftop_area_m2);

COMMENT ON MATERIALIZED VIEW mv_municipality_stats_microsoft IS
    'Pre-aggregated statistics for Microsoft buildings by PDET municipality';

-- Materialized view for Google buildings statistics by municipality
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_municipality_stats_google AS
SELECT
    m.municipality_id,
    m.muni_code,
    m.muni_name,
    m.dept_code,
    m.dept_name,
    m.pdet_region,
    m.pdet_subregion,
    COUNT(b.building_id) AS building_count,
    COALESCE(SUM(b.area_m2), 0) AS total_rooftop_area_m2,
    COALESCE(SUM(b.area_m2), 0) / 1000000 AS total_rooftop_area_km2,
    COALESCE(AVG(b.area_m2), 0) AS avg_building_area_m2,
    COALESCE(AVG(b.confidence), 0) AS avg_confidence,
    COUNT(CASE WHEN b.geom_type = 'POLYGON' THEN 1 END) AS polygon_count,
    COUNT(CASE WHEN b.geom_type = 'POINT' THEN 1 END) AS point_count,
    COUNT(CASE WHEN b.confidence >= 0.7 THEN 1 END) AS high_confidence_count,
    -- Solar potential estimate
    COALESCE(SUM(b.area_m2), 0) * 0.7 AS estimated_usable_area_m2
FROM pdet_municipalities m
LEFT JOIN buildings_google b ON m.municipality_id = b.municipality_id
GROUP BY m.municipality_id, m.muni_code, m.muni_name, m.dept_code,
         m.dept_name, m.pdet_region, m.pdet_subregion;

-- Index on materialized view
CREATE UNIQUE INDEX idx_mv_stats_gg_muni_id ON mv_municipality_stats_google (municipality_id);
CREATE INDEX idx_mv_stats_gg_muni_code ON mv_municipality_stats_google (muni_code);
CREATE INDEX idx_mv_stats_gg_area ON mv_municipality_stats_google (total_rooftop_area_m2);

COMMENT ON MATERIALIZED VIEW mv_municipality_stats_google IS
    'Pre-aggregated statistics for Google buildings by PDET municipality';

-- Materialized view for dataset comparison
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_dataset_comparison AS
SELECT
    m.municipality_id,
    m.muni_code,
    m.muni_name,
    m.dept_name,
    m.pdet_region,
    COALESCE(ms.building_count, 0) AS ms_building_count,
    COALESCE(ms.total_rooftop_area_m2, 0) AS ms_total_area_m2,
    COALESCE(gg.building_count, 0) AS gg_building_count,
    COALESCE(gg.total_rooftop_area_m2, 0) AS gg_total_area_m2,
    ABS(COALESCE(ms.building_count, 0) - COALESCE(gg.building_count, 0)) AS count_difference,
    ABS(COALESCE(ms.total_rooftop_area_m2, 0) - COALESCE(gg.total_rooftop_area_m2, 0)) AS area_difference_m2,
    CASE
        WHEN COALESCE(ms.building_count, 0) > COALESCE(gg.building_count, 0) THEN 'Microsoft'
        WHEN COALESCE(gg.building_count, 0) > COALESCE(ms.building_count, 0) THEN 'Google'
        ELSE 'Equal'
    END AS more_buildings_source,
    CASE
        WHEN COALESCE(ms.total_rooftop_area_m2, 0) > COALESCE(gg.total_rooftop_area_m2, 0) THEN 'Microsoft'
        WHEN COALESCE(gg.total_rooftop_area_m2, 0) > COALESCE(ms.total_rooftop_area_m2, 0) THEN 'Google'
        ELSE 'Equal'
    END AS more_area_source
FROM pdet_municipalities m
LEFT JOIN mv_municipality_stats_microsoft ms USING (municipality_id)
LEFT JOIN mv_municipality_stats_google gg USING (municipality_id);

-- Index on comparison view
CREATE UNIQUE INDEX idx_mv_comparison_muni_id ON mv_dataset_comparison (municipality_id);
CREATE INDEX idx_mv_comparison_diff ON mv_dataset_comparison (count_difference);

COMMENT ON MATERIALIZED VIEW mv_dataset_comparison IS
    'Comparison of Microsoft vs Google building counts and areas by municipality';

-- ==============================================================================
-- STEP 10: Create Helper Functions
-- ==============================================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_municipality_stats_microsoft;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_municipality_stats_google;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dataset_comparison;
    RAISE NOTICE 'All materialized views refreshed successfully';
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_all_stats() IS 'Refresh all materialized views for municipality statistics';

-- Function to assign buildings to municipalities (spatial join)
CREATE OR REPLACE FUNCTION assign_buildings_to_municipalities(
    source_table TEXT  -- 'buildings_microsoft' or 'buildings_google'
)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    EXECUTE format(
        'UPDATE %I b
         SET municipality_id = m.municipality_id,
             muni_code = m.muni_code,
             dept_code = m.dept_code
         FROM pdet_municipalities m
         WHERE ST_Contains(m.geom, b.centroid)
           AND b.municipality_id IS NULL',
        source_table
    );

    GET DIAGNOSTICS updated_count = ROW_COUNT;

    RAISE NOTICE 'Updated % buildings in %', updated_count, source_table;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION assign_buildings_to_municipalities(TEXT) IS
    'Assign buildings to municipalities via spatial join (ST_Contains)';

-- ==============================================================================
-- STEP 11: Grant Permissions (if using specific user roles)
-- ==============================================================================

-- Example permissions (uncomment and modify as needed)
-- CREATE ROLE pdet_analyst;
-- GRANT USAGE ON SCHEMA pdet_solar TO pdet_analyst;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA pdet_solar TO pdet_analyst;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA pdet_solar TO pdet_analyst;

-- ==============================================================================
-- STEP 12: Verification Queries
-- ==============================================================================

-- Check tables created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'pdet_solar'
ORDER BY table_name;

-- Check spatial indexes
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'pdet_solar'
  AND indexdef LIKE '%gist%'
ORDER BY tablename, indexname;

-- Check materialized views
SELECT
    schemaname,
    matviewname,
    ispopulated
FROM pg_matviews
WHERE schemaname = 'pdet_solar';

-- ==============================================================================
-- END OF SCHEMA CREATION SCRIPT
-- ==============================================================================

-- Final message
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'PDET Solar Analysis Schema Created!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Schema: pdet_solar';
    RAISE NOTICE 'Tables: pdet_municipalities, buildings_microsoft, buildings_google';
    RAISE NOTICE 'Materialized Views: mv_municipality_stats_*, mv_dataset_comparison';
    RAISE NOTICE 'Functions: refresh_all_stats(), assign_buildings_to_municipalities()';
    RAISE NOTICE '========================================';
END $$;
