"""
Join espacial entre edificaciones y municipios PDET en MongoDB
"""
import sys
import csv
from pathlib import Path
from pymongo import MongoClient

DB_NAME = "pdet_solar_analysis"
MUNI_COLL = "pdet_municipalities"
MS_COLL = "microsoft_buildings"
GOOGLE_COLL = "google_buildings"
CSV_OUT = Path(__file__).parent.parent / "results" / "conteos_edificios_por_muni.csv"
CSV_OUT.parent.mkdir(parents=True, exist_ok=True)

def spatial_join_counts():
    client = MongoClient()
    db = client[DB_NAME]
    ms = db[MS_COLL]
    gg = db[GOOGLE_COLL]
    muni = db[MUNI_COLL]

    rows = [("muni_code","muni_name","ms_count","ggl_count")]
    for m in muni.find({}, {"muni_code":1, "muni_name":1, "geom":1}):
        code = m.get("muni_code", "NA")
        name = m.get("muni_name", "NA")
        geom = m.get("geom")
        if not geom:
            print(f"[!] Municipio {code} sin geom, skip")
            continue
        ms_count = ms.count_documents({"geometry": {"$geoWithin": {"$geometry": geom}}})
        ggl_count = gg.count_documents({"geometry": {"$geoWithin": {"$geometry": geom}}, "properties.confidence": {"$gte": 0.80}})
        print(f"{code} ({name}): MS={ms_count} GOOGLE>0.8={ggl_count}")
        rows.append((code, name, ms_count, ggl_count))
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"Conteos por municipio exportados a {CSV_OUT}")

if __name__ == "__main__":
    spatial_join_counts()
