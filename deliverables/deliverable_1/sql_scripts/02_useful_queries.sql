/*
 * PDET Solar Rooftop Analysis - Useful Queries
 * Collection of common queries for analysis and debugging
 *
 * Purpose: Provide ready-to-use SQL queries for data exploration and validation
 * Author: PDET Analysis Team
 * Date: October 2025
 */

-- Set schema
SET search_path TO pdet_solar, public;

-- ==============================================================================
-- SECTION 1: Data Validation Queries
-- ==============================================================================

-- 1.1 Check record counts
SELECT 'pdet_municipalities' AS table_name, COUNT(*) AS row_count
FROM pdet_municipalities
UNION ALL
SELECT 'buildings_microsoft', COUNT(*) FROM buildings_microsoft
UNION ALL
SELECT 'buildings_google', COUNT(*) FROM buildings_google;

-- 1.2 Check for invalid geometries
SELECT 'pdet_municipalities' AS table_name,
       COUNT(*) FILTER (WHERE NOT ST_IsValid(geom)) AS invalid_geoms
FROM pdet_municipalities
UNION ALL
SELECT 'buildings_microsoft',
       COUNT(*) FILTER (WHERE NOT ST_IsValid(geom))
FROM buildings_microsoft
UNION ALL
SELECT 'buildings_google',
       COUNT(*) FILTER (WHERE NOT ST_IsValid(geom))
FROM buildings_google;

-- 1.3 Check spatial reference systems
SELECT
    'pdet_municipalities' AS table_name,
    Find_SRID('pdet_solar', 'pdet_municipalities', 'geom') AS srid
UNION ALL
SELECT 'buildings_microsoft',
       Find_SRID('pdet_solar', 'buildings_microsoft', 'geom')
UNION ALL
SELECT 'buildings_google',
       Find_SRID('pdet_solar', 'buildings_google', 'geom');

-- 1.4 Check for NULL or empty geometries
SELECT
    'pdet_municipalities' AS table_name,
    COUNT(*) FILTER (WHERE geom IS NULL) AS null_geoms,
    COUNT(*) FILTER (WHERE ST_IsEmpty(geom)) AS empty_geoms
FROM pdet_municipalities
UNION ALL
SELECT 'buildings_microsoft',
       COUNT(*) FILTER (WHERE geom IS NULL),
       COUNT(*) FILTER (WHERE ST_IsEmpty(geom))
FROM buildings_microsoft
UNION ALL
SELECT 'buildings_google',
       COUNT(*) FILTER (WHERE geom IS NULL),
       COUNT(*) FILTER (WHERE ST_IsEmpty(geom))
FROM buildings_google;

-- ==============================================================================
-- SECTION 2: Data Exploration Queries
-- ==============================================================================

-- 2.1 PDET municipalities summary
SELECT
    dept_name,
    COUNT(*) AS municipality_count,
    SUM(area_km2) AS total_area_km2,
    STRING_AGG(muni_name, ', ' ORDER BY muni_name) AS municipalities
FROM pdet_municipalities
GROUP BY dept_name
ORDER BY municipality_count DESC;

-- 2.2 Top 10 largest PDET municipalities
SELECT
    muni_name,
    dept_name,
    area_km2,
    ROUND((area_km2 * 100.0) / SUM(area_km2) OVER (), 2) AS pct_of_total
FROM pdet_municipalities
ORDER BY area_km2 DESC
LIMIT 10;

-- 2.3 Distribution of building sizes (Microsoft)
SELECT
    CASE
        WHEN area_m2 < 50 THEN '< 50 m²'
        WHEN area_m2 < 100 THEN '50-100 m²'
        WHEN area_m2 < 200 THEN '100-200 m²'
        WHEN area_m2 < 500 THEN '200-500 m²'
        WHEN area_m2 < 1000 THEN '500-1000 m²'
        ELSE '> 1000 m²'
    END AS size_category,
    COUNT(*) AS building_count,
    ROUND(AVG(area_m2), 2) AS avg_area_m2
FROM buildings_microsoft
WHERE area_m2 IS NOT NULL
GROUP BY size_category
ORDER BY MIN(area_m2);

-- 2.4 Google buildings: Polygon vs Point distribution
SELECT
    geom_type,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(AVG(confidence), 3) AS avg_confidence
FROM buildings_google
WHERE geom_type IS NOT NULL
GROUP BY geom_type;

-- ==============================================================================
-- SECTION 3: Spatial Join Queries
-- ==============================================================================

-- 3.1 Count buildings per municipality (Microsoft) - SLOW on large datasets
-- Use materialized view mv_municipality_stats_microsoft instead for production
SELECT
    m.muni_name,
    m.dept_name,
    COUNT(b.building_id) AS building_count
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b ON ST_Contains(m.geom, b.geom)
GROUP BY m.municipality_id, m.muni_name, m.dept_name
ORDER BY building_count DESC
LIMIT 10;

-- 3.2 Total rooftop area per municipality (Microsoft)
SELECT
    m.muni_name,
    m.dept_name,
    COUNT(b.building_id) AS building_count,
    COALESCE(SUM(b.area_m2), 0) AS total_area_m2,
    COALESCE(SUM(b.area_m2), 0) / 1000000 AS total_area_km2
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b ON ST_Contains(m.geom, b.geom)
GROUP BY m.municipality_id, m.muni_name, m.dept_name
ORDER BY total_area_m2 DESC
LIMIT 10;

-- ==============================================================================
-- SECTION 4: Materialized View Queries (FAST!)
-- ==============================================================================

-- 4.1 Top 20 municipalities by building count (Microsoft)
SELECT
    muni_name,
    dept_name,
    pdet_region,
    building_count,
    ROUND(total_rooftop_area_km2, 4) AS total_area_km2,
    ROUND(avg_building_area_m2, 2) AS avg_building_m2
FROM mv_municipality_stats_microsoft
ORDER BY building_count DESC
LIMIT 20;

-- 4.2 Top 20 municipalities by total rooftop area (Google)
SELECT
    muni_name,
    dept_name,
    pdet_region,
    building_count,
    ROUND(total_rooftop_area_km2, 4) AS total_area_km2,
    ROUND(avg_confidence, 3) AS avg_confidence,
    polygon_count,
    point_count
FROM mv_municipality_stats_google
ORDER BY total_rooftop_area_m2 DESC
LIMIT 20;

-- 4.3 Dataset comparison - Top differences
SELECT
    muni_name,
    dept_name,
    ms_building_count AS microsoft_count,
    gg_building_count AS google_count,
    count_difference,
    more_buildings_source,
    ROUND(ms_total_area_m2 / 1000000, 4) AS ms_area_km2,
    ROUND(gg_total_area_m2 / 1000000, 4) AS gg_area_km2
FROM mv_dataset_comparison
ORDER BY count_difference DESC
LIMIT 20;

-- 4.4 Municipalities with highest solar potential (estimated usable area)
SELECT
    muni_name,
    dept_name,
    pdet_region,
    building_count,
    ROUND(estimated_usable_area_m2 / 1000000, 4) AS usable_area_km2,
    ROUND(total_rooftop_area_km2, 4) AS total_area_km2
FROM mv_municipality_stats_microsoft
WHERE building_count > 0
ORDER BY estimated_usable_area_m2 DESC
LIMIT 20;

-- ==============================================================================
-- SECTION 5: Performance Analysis Queries
-- ==============================================================================

-- 5.1 Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS times_used,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'pdet_solar'
ORDER BY idx_scan DESC;

-- 5.2 Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) -
                   pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'pdet_solar'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 5.3 Check for missing spatial assignments
SELECT
    'buildings_microsoft' AS table_name,
    COUNT(*) AS total,
    COUNT(municipality_id) AS assigned,
    COUNT(*) - COUNT(municipality_id) AS unassigned,
    ROUND((COUNT(*) - COUNT(municipality_id)) * 100.0 / COUNT(*), 2) AS pct_unassigned
FROM buildings_microsoft
UNION ALL
SELECT
    'buildings_google',
    COUNT(*),
    COUNT(municipality_id),
    COUNT(*) - COUNT(municipality_id),
    ROUND((COUNT(*) - COUNT(municipality_id)) * 100.0 / COUNT(*), 2)
FROM buildings_google;

-- ==============================================================================
-- SECTION 6: Data Quality Queries
-- ==============================================================================

-- 6.1 Buildings with suspicious areas (too small or too large)
SELECT
    'Microsoft' AS source,
    COUNT(*) FILTER (WHERE area_m2 < 10) AS too_small,
    COUNT(*) FILTER (WHERE area_m2 > 10000) AS too_large,
    MIN(area_m2) AS min_area,
    MAX(area_m2) AS max_area
FROM buildings_microsoft
WHERE area_m2 IS NOT NULL
UNION ALL
SELECT
    'Google',
    COUNT(*) FILTER (WHERE area_m2 < 10),
    COUNT(*) FILTER (WHERE area_m2 > 10000),
    MIN(area_m2),
    MAX(area_m2)
FROM buildings_google
WHERE area_m2 IS NOT NULL;

-- 6.2 Google buildings confidence distribution
SELECT
    CASE
        WHEN confidence < 0.3 THEN 'Low (< 0.3)'
        WHEN confidence < 0.5 THEN 'Medium-Low (0.3-0.5)'
        WHEN confidence < 0.7 THEN 'Medium (0.5-0.7)'
        WHEN confidence < 0.9 THEN 'High (0.7-0.9)'
        ELSE 'Very High (>= 0.9)'
    END AS confidence_category,
    COUNT(*) AS building_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM buildings_google
WHERE confidence IS NOT NULL
GROUP BY confidence_category
ORDER BY MIN(confidence);

-- ==============================================================================
-- SECTION 7: Geographic Analysis Queries
-- ==============================================================================

-- 7.1 Find buildings within a specific municipality
SELECT
    b.building_id,
    b.area_m2,
    ST_AsText(b.geom) AS wkt_geometry
FROM buildings_microsoft b
JOIN pdet_municipalities m ON ST_Contains(m.geom, b.geom)
WHERE m.muni_code = '05001'  -- Example: Medellín
LIMIT 10;

-- 7.2 Calculate density (buildings per km²) by municipality
SELECT
    m.muni_name,
    m.dept_name,
    m.area_km2,
    COUNT(b.building_id) AS building_count,
    ROUND(COUNT(b.building_id)::numeric / NULLIF(m.area_km2, 0), 2) AS buildings_per_km2
FROM pdet_municipalities m
LEFT JOIN buildings_microsoft b ON ST_Contains(m.geom, b.geom)
GROUP BY m.municipality_id, m.muni_name, m.dept_name, m.area_km2
HAVING COUNT(b.building_id) > 0
ORDER BY buildings_per_km2 DESC
LIMIT 20;

-- 7.3 Find neighboring municipalities (municipalities that share a border)
SELECT
    a.muni_name AS municipality_1,
    b.muni_name AS municipality_2,
    a.dept_name AS dept_1,
    b.dept_name AS dept_2
FROM pdet_municipalities a
JOIN pdet_municipalities b ON a.municipality_id < b.municipality_id
WHERE ST_Touches(a.geom, b.geom)
ORDER BY a.muni_name, b.muni_name;

-- ==============================================================================
-- SECTION 8: Refresh and Maintenance
-- ==============================================================================

-- 8.1 Refresh all materialized views
-- This should be run after data loading or updates
SELECT refresh_all_stats();

-- 8.2 Assign buildings to municipalities
-- Run this after loading building data
-- SELECT assign_buildings_to_municipalities('buildings_microsoft');
-- SELECT assign_buildings_to_municipalities('buildings_google');

-- 8.3 Analyze tables to update statistics
ANALYZE pdet_municipalities;
ANALYZE buildings_microsoft;
ANALYZE buildings_google;

-- 8.4 Vacuum tables (cleanup and optimization)
-- VACUUM ANALYZE pdet_municipalities;
-- VACUUM ANALYZE buildings_microsoft;
-- VACUUM ANALYZE buildings_google;

-- ==============================================================================
-- END OF USEFUL QUERIES
-- ==============================================================================

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'Useful queries script loaded successfully!';
    RAISE NOTICE 'Modify queries as needed for your analysis.';
END $$;
