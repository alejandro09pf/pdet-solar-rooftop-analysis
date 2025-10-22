# PDET Solar Rooftop Analysis

## Database Administration - Final Project

**Analyzing Solar Energy Potential on Building Rooftops in PDET Territories, Colombia**

## Introduction

This project supports UPME's (Unidad de Planeación Minero Energética) objective of evaluating the feasibility of solar energy in selected territories across Colombia. The project designs and implements a reproducible geospatial analysis workflow to estimate the solar energy potential of building rooftops across prioritized municipalities, particularly in PDET (Programas de Desarrollo con Enfoque Territorial) territories.

PDET territories represent key focus areas for post-conflict development and infrastructure enhancement in Colombia. By leveraging openly available geospatial datasets containing billions of building outlines derived from high-resolution satellite imagery, this project aims to quantify potential energy-harvesting surfaces in urban and rural contexts.

## Objectives

The primary goals of this project are:

1. **Count buildings** within each PDET municipality
2. **Estimate total rooftop area** suitable for solar panel installation
3. **Compare outputs** from different open building datasets
4. **Implement NoSQL solutions** for scalable storage and efficient spatial operations
5. **Provide strategic recommendations** for proof-of-concept solar farm locations

## Datasets

### Building Footprints

1. **Microsoft Building Footprints**
   - Over 999 million building detections from Bing Maps imagery (2014-2021)
   - Sources: Maxar and Airbus
   - License: Open Data Commons Open Database License (ODbL)
   - [Dataset Information](https://planetarycomputer.microsoft.com/dataset/ms-buildings)

2. **Google Open Buildings**
   - 1.8 billion building detections
   - Coverage: 58 million km² (Africa, South Asia, Southeast Asia, Latin America, Caribbean)
   - Version: 3
   - License: CC BY-4.0 and ODbL v1.0
   - [Dataset Information](https://sites.research.google/gr/open-buildings/)

### Administrative Boundaries

- **DANE Marco Geoestadístico Nacional (MGN)**
  - Colombian administrative boundaries at municipal level
  - Focus on PDET-designated municipalities
  - [DANE Geoportal](https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/datos-geoestadisticos/?cod=111)

## Project Structure

```
pdet-solar-rooftop-analysis/
├── data/
│   ├── raw/              # Original datasets (not tracked in git)
│   └── processed/        # Cleaned and processed data
├── src/                  # Source code and scripts
├── notebooks/            # Jupyter notebooks for analysis
├── docs/                 # Project documentation
├── deliverables/         # Project deliverables by week
├── results/              # Analysis results and visualizations
├── config/               # Configuration files
└── README.md
```

## Deliverables Schedule

### Deliverable 1 - October 27, 2:00 PM
**NoSQL Database Schema Design and Implementation Plan**
- Implementation Plan
- Data Modeling
- Schema Design & Appropriateness

### Deliverable 2 - November 3, 2:00 PM
**PDET Municipality Boundaries Dataset Integration**
- Data Acquisition & Verification
- Data Integrity & Format
- NoSQL Spatial Integration
- Documentation of Process

### Deliverable 3 - November 10, 2:00 PM
**Building Footprint Data Loading and Integration Report**
- Microsoft & Google Datasets Integration
- Spatial Indexing
- Data Loading Efficiency
- Initial Data Audit (EDA)

### Deliverable 4 - November 17, 2:00 PM
**Reproducible Geospatial Analysis Workflow**
- Rooftop Count and Area Estimation
- Reproducibility & Methodology
- Accuracy of Spatial Operations
- Output Data Structure (tables and maps)

### Deliverable 5 - November 24, 2:00 PM
**Final Technical Report and Recommendations**
- Complete Documentation
- Results and Visualizations
- Content & Completeness
- Clarity of Recommendations
- Alignment with UPME Objectives

## Technology Stack

- **NoSQL Database**: TBD (MongoDB/PostgreSQL+PostGIS/etc.)
- **Programming Language**: Python
- **Geospatial Libraries**: GeoPandas, Shapely, Fiona, PyGEOS
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Folium, Plotly

## Getting Started

### Prerequisites

```bash
# Python 3.8+
# Git
# NoSQL Database (to be determined in Deliverable 1)
```

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd pdet-solar-rooftop-analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (to be added)
pip install -r requirements.txt
```

## License

This project is developed as part of an academic assignment for Database Administration course.

## Contributors

- [Team Members TBD]

## Contact

For questions regarding this project, please contact the project team or refer to the course instructor.

---

**Note**: This project integrates modern data science tools with real-world energy policy needs, bridging technical innovation and strategic planning in support of Colombia's energy transition and territorial equity.
