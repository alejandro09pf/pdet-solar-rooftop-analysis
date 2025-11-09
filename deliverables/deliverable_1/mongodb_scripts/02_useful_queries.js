// ============================================================================
// PDET Solar Rooftop Analysis - Useful MongoDB Queries
// ============================================================================
// Script: 02_useful_queries.js
// Purpose: Collection of useful queries for data exploration and analysis
// Database: pdet_solar_analysis
// ============================================================================

use pdet_solar_analysis;

print("=".repeat(80));
print("PDET Solar Analysis - Useful Queries");
print("=".repeat(80));

// ============================================================================
// 1. BASIC STATISTICS
// ============================================================================

print("\n1. BASIC STATISTICS\n");

// Count municipalities
print("Total PDET municipalities:");
var totalMunicipalities = db.pdet_municipalities.countDocuments();
printjson(totalMunicipalities);

// Count buildings by source
print("\nTotal buildings by source:");
print("   Microsoft: " + db.buildings_microsoft.countDocuments());
print("   Google: " + db.buildings_google.countDocuments());

// ============================================================================
// 2. MUNICIPALITY STATISTICS
// ============================================================================

print("\n2. MUNICIPALITY STATISTICS\n");

// Municipalities by department
print("Municipalities by department:");
var muniByDept = db.pdet_municipalities.aggregate([
    {
        $group: {
            _id: "$dept_name",
            count: { $sum: 1 },
            total_area_km2: { $sum: "$area_km2" }
        }
    },
    { $sort: { count: -1 } },
    { $limit: 10 }
]);
printjson(muniByDept.toArray());

// Municipalities by PDET region
print("\nMunicipalities by PDET region:");
var muniByRegion = db.pdet_municipalities.aggregate([
    {
        $group: {
            _id: "$pdet_region",
            count: { $sum: 1 },
            total_area_km2: { $sum: "$area_km2" }
        }
    },
    { $sort: { count: -1 } }
]);
printjson(muniByRegion.toArray());

// Area statistics
print("\nArea statistics (km²):");
var areaStats = db.pdet_municipalities.aggregate([
    {
        $group: {
            _id: null,
            total_area: { $sum: "$area_km2" },
            avg_area: { $avg: "$area_km2" },
            min_area: { $min: "$area_km2" },
            max_area: { $max: "$area_km2" }
        }
    }
]);
printjson(areaStats.toArray());

// ============================================================================
// 3. SPATIAL QUERIES - MUNICIPALITIES
// ============================================================================

print("\n3. SPATIAL QUERIES - MUNICIPALITIES\n");

// Find municipalities in a specific region
print("Municipalities in 'Región Pacífico' (first 5):");
var pacificoMunis = db.pdet_municipalities.find(
    { pdet_region: /Pacífico/i },
    { muni_name: 1, dept_name: 1, area_km2: 1, _id: 0 }
).limit(5);
printjson(pacificoMunis.toArray());

// Largest municipalities by area
print("\nTop 10 largest municipalities by area:");
var largestMunis = db.pdet_municipalities.find(
    {},
    { muni_name: 1, dept_name: 1, area_km2: 1, _id: 0 }
).sort({ area_km2: -1 }).limit(10);
printjson(largestMunis.toArray());

// ============================================================================
// 4. BUILDING STATISTICS (Microsoft)
// ============================================================================

print("\n4. BUILDING STATISTICS - MICROSOFT\n");

// Buildings per municipality (Microsoft)
print("Buildings per municipality (Microsoft) - Top 10:");
var buildingsPerMuni = db.buildings_microsoft.aggregate([
    {
        $group: {
            _id: "$muni_code",
            building_count: { $sum: 1 },
            total_area_m2: { $sum: "$area_m2" },
            avg_area_m2: { $avg: "$area_m2" }
        }
    },
    { $sort: { building_count: -1 } },
    { $limit: 10 },
    {
        $lookup: {
            from: "pdet_municipalities",
            localField: "_id",
            foreignField: "muni_code",
            as: "municipality"
        }
    },
    {
        $project: {
            muni_code: "$_id",
            muni_name: { $arrayElemAt: ["$municipality.muni_name", 0] },
            dept_name: { $arrayElemAt: ["$municipality.dept_name", 0] },
            building_count: 1,
            total_area_m2: 1,
            avg_area_m2: 1
        }
    }
]);
printjson(buildingsPerMuni.toArray());

// Building size distribution (Microsoft)
print("\nBuilding size distribution (Microsoft):");
var sizeDistribution = db.buildings_microsoft.aggregate([
    {
        $bucket: {
            groupBy: "$area_m2",
            boundaries: [0, 50, 100, 200, 500, 1000, 10000],
            default: "10000+",
            output: {
                count: { $sum: 1 },
                total_area: { $sum: "$area_m2" }
            }
        }
    }
]);
printjson(sizeDistribution.toArray());

// ============================================================================
// 5. BUILDING STATISTICS (Google)
// ============================================================================

print("\n5. BUILDING STATISTICS - GOOGLE\n");

// Buildings per municipality (Google)
print("Buildings per municipality (Google) - Top 10:");
var buildingsPerMuniGoogle = db.buildings_google.aggregate([
    {
        $group: {
            _id: "$muni_code",
            building_count: { $sum: 1 },
            total_area_m2: { $sum: "$area_m2" },
            avg_area_m2: { $avg: "$area_m2" },
            avg_confidence: { $avg: "$confidence" }
        }
    },
    { $sort: { building_count: -1 } },
    { $limit: 10 },
    {
        $lookup: {
            from: "pdet_municipalities",
            localField: "_id",
            foreignField: "muni_code",
            as: "municipality"
        }
    },
    {
        $project: {
            muni_code: "$_id",
            muni_name: { $arrayElemAt: ["$municipality.muni_name", 0] },
            dept_name: { $arrayElemAt: ["$municipality.dept_name", 0] },
            building_count: 1,
            total_area_m2: 1,
            avg_area_m2: 1,
            avg_confidence: 1
        }
    }
]);
printjson(buildingsPerMuniGoogle.toArray());

// Confidence score distribution (Google)
print("\nConfidence score distribution (Google):");
var confidenceDistribution = db.buildings_google.aggregate([
    {
        $bucket: {
            groupBy: "$confidence",
            boundaries: [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            default: "other",
            output: {
                count: { $sum: 1 }
            }
        }
    }
]);
printjson(confidenceDistribution.toArray());

// ============================================================================
// 6. SPATIAL QUERIES - BUILDINGS
// ============================================================================

print("\n6. SPATIAL QUERIES - BUILDINGS\n");

// Find buildings within a specific municipality (example with first municipality)
var sampleMuni = db.pdet_municipalities.findOne();
if (sampleMuni) {
    print("Buildings in " + sampleMuni.muni_name + " (Microsoft - first 5):");
    var buildingsInMuni = db.buildings_microsoft.find(
        {
            geom: {
                $geoWithin: {
                    $geometry: sampleMuni.geom
                }
            }
        },
        { area_m2: 1, muni_code: 1, _id: 0 }
    ).limit(5);
    printjson(buildingsInMuni.toArray());
}

// ============================================================================
// 7. COMPARISON QUERIES (Microsoft vs Google)
// ============================================================================

print("\n7. COMPARISON - MICROSOFT VS GOOGLE\n");

// Compare building counts by municipality
print("Building count comparison (first 5 municipalities):");
var comparison = db.pdet_municipalities.aggregate([
    { $limit: 5 },
    {
        $lookup: {
            from: "buildings_microsoft",
            let: { muniCode: "$muni_code" },
            pipeline: [
                { $match: { $expr: { $eq: ["$muni_code", "$$muniCode"] } } },
                { $count: "count" }
            ],
            as: "ms_count"
        }
    },
    {
        $lookup: {
            from: "buildings_google",
            let: { muniCode: "$muni_code" },
            pipeline: [
                { $match: { $expr: { $eq: ["$muni_code", "$$muniCode"] } } },
                { $count: "count" }
            ],
            as: "google_count"
        }
    },
    {
        $project: {
            muni_name: 1,
            dept_name: 1,
            microsoft_buildings: { $ifNull: [{ $arrayElemAt: ["$ms_count.count", 0] }, 0] },
            google_buildings: { $ifNull: [{ $arrayElemAt: ["$google_count.count", 0] }, 0] }
        }
    }
]);
printjson(comparison.toArray());

// ============================================================================
// 8. DATA QUALITY CHECKS
// ============================================================================

print("\n8. DATA QUALITY CHECKS\n");

// Check for municipalities without PDET region
print("Municipalities without PDET region:");
var noRegion = db.pdet_municipalities.countDocuments({
    $or: [
        { pdet_region: { $exists: false } },
        { pdet_region: null },
        { pdet_region: "" }
    ]
});
print("   Count: " + noRegion);

// Check for buildings without municipality code
print("\nBuildings without municipality code:");
print("   Microsoft: " + db.buildings_microsoft.countDocuments({ muni_code: { $exists: false } }));
print("   Google: " + db.buildings_google.countDocuments({ muni_code: { $exists: false } }));

// Check for invalid areas
print("\nBuildings with invalid areas (< 0 or > 100000 m²):");
print("   Microsoft: " + db.buildings_microsoft.countDocuments({
    $or: [{ area_m2: { $lt: 0 } }, { area_m2: { $gt: 100000 } }]
}));
print("   Google: " + db.buildings_google.countDocuments({
    $or: [{ area_m2: { $lt: 0 } }, { area_m2: { $gt: 100000 } }]
}));

// ============================================================================
// 9. AGGREGATION FOR REPORTING
// ============================================================================

print("\n9. AGGREGATION FOR REPORTING\n");

// Summary by PDET region (Microsoft buildings)
print("Summary by PDET region (Microsoft buildings):");
var regionSummary = db.pdet_municipalities.aggregate([
    {
        $lookup: {
            from: "buildings_microsoft",
            localField: "muni_code",
            foreignField: "muni_code",
            as: "buildings"
        }
    },
    {
        $group: {
            _id: "$pdet_region",
            municipality_count: { $sum: 1 },
            total_building_count: { $sum: { $size: "$buildings" } },
            total_muni_area_km2: { $sum: "$area_km2" }
        }
    },
    { $sort: { total_building_count: -1 } }
]);
printjson(regionSummary.toArray());

// ============================================================================
// 10. INDEX INFORMATION
// ============================================================================

print("\n10. INDEX INFORMATION\n");

print("Indexes on pdet_municipalities:");
printjson(db.pdet_municipalities.getIndexes());

print("\nIndexes on buildings_microsoft:");
printjson(db.buildings_microsoft.getIndexes());

print("\nIndexes on buildings_google:");
printjson(db.buildings_google.getIndexes());

print("\n" + "=".repeat(80));
print("Query exploration complete!");
print("=".repeat(80));
