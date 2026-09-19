# Āśraya AI

## An AI-Driven Community Disaster Resilience Platform

**Prepare. Protect. Recover.**

Āśraya AI is an AI-powered disaster resilience platform designed to help communities better understand flood risk and access practical preparedness guidance.

The current MVP focuses on **district-level flood risk assessment in Kerala, India**, using historical flood records and rainfall patterns. It combines a machine learning model with a retrieval-augmented AI guidance system to provide both risk context and actionable preparedness information.

> **Important:** Āśraya AI is a research and decision-support prototype. It does not replace official weather alerts, flood warnings, evacuation orders, emergency services, or government authorities.

---

## Problem

Floods can cause significant loss of life, infrastructure damage, displacement, and disruption to communities.

Although weather information and disaster alerts are increasingly available, people may still struggle to understand:

* How their local conditions relate to historical flood patterns
* Whether current rainfall conditions indicate elevated historical risk
* What practical steps they should take before, during, and after a flood
* Where to find reliable preparedness information

This challenge can be particularly significant for rural and resource-constrained communities.

---

## Solution

Āśraya AI combines historical data, machine learning, and an AI preparedness assistant into a single platform.

The current system:

1. Allows a user to select a Kerala district and date
2. Retrieves historical rainfall information
3. Estimates the likelihood of a recorded flood onset on the following day based on historical patterns
4. Converts the model score into an interpretable risk category
5. Provides rainfall-based context
6. Uses a retrieval-augmented AI assistant to provide preparedness guidance from a trusted knowledge base

The goal is not to replace official disaster-management systems, but to make existing information easier to understand and act upon.

---

## System Architecture

```text
                         ĀŚRAYA AI
                             |
             +---------------+---------------+
             |                               |
             v                               v
       Flood Risk ML                    AI Guidance
             |                               |
       Rainfall Features                RAG Knowledge
             |                               |
             +---------------+---------------+
                             |
                             v
                     Web Interface
```

---

## Current MVP

The current MVP includes:

* Kerala district selection
* Historical rainfall data
* Historical flood-event data
* Flood-onset classification model
* Risk score and risk category
* Rainfall-based contextual information
* AI preparedness assistant
* Retrieval-augmented generation (RAG)
* Trusted flood preparedness knowledge base
* Web-based dashboard
* Safety and limitation disclaimers

---

## Machine Learning Approach

The model is designed around the following prediction task:

```text
Information available on Day T
            |
            v
     Rainfall up to T
            |
            v
      ML Risk Model
            |
            v
Flood onset recorded on Day T+1
```

The model does not use rainfall from the prediction day or future dates when generating the prediction.

### Input Features

The current model uses rainfall indicators calculated from historical rainfall data:

* 1-day cumulative rainfall
* 3-day cumulative rainfall
* 7-day cumulative rainfall
* 30-day cumulative rainfall
* Maximum rainfall within the previous 3 days
* Maximum rainfall within the previous 7 days

### Models Evaluated

Two models were evaluated:

* Logistic Regression
* Random Forest

A chronological train/test split was used:

```text
Training period: Before 2020
Testing period:  2020 onwards
```

This approach avoids randomly mixing future observations into the training data.

### Model Evaluation

Because recorded flood-onset events are rare compared with non-flood days, accuracy alone is not an appropriate measure of performance.

The evaluation therefore considers:

* Precision
* Recall
* F1-score
* ROC-AUC
* Precision-Recall AUC
* Confusion matrix

The model demonstrates useful predictive signal, but it also produces false positives. The current system should therefore be treated as a **risk-assessment and research prototype**, not an operational flood-warning system.

---

## Risk Assessment

The model produces a continuous risk score which is converted into four presentation categories:

| Risk Score  | Category  |
| ----------- | --------- |
| < 0.10      | Low       |
| 0.10 - 0.30 | Moderate  |
| 0.30 - 0.60 | High      |
| >= 0.60     | Very High |

These thresholds are **presentation thresholds created for the prototype**. They are not official flood-warning thresholds.

The displayed score should not be interpreted as a calibrated probability of a flood occurring.

For example, a score of `0.58` means that the model produced a relatively elevated risk score for that historical situation. It does not mean there is exactly a 58% chance of flooding.

---

## AI Preparedness Assistant

Āśraya AI includes an AI guidance layer designed to answer questions related to flood preparedness.

The system uses Retrieval-Augmented Generation (RAG):

```text
User Question
      |
      v
Semantic Retrieval
      |
      v
Trusted Preparedness Knowledge
      |
      v
Relevant Context
      |
      v
LLM
      |
      v
Preparedness Guidance
```

The knowledge base contains guidance covering:

### Before a Flood

* Monitoring official information
* Preparing emergency supplies
* Protecting important documents
* Charging phones and power banks
* Identifying safer locations and routes
* Moving vehicles and equipment to safer areas

### During a Flood

* Following official instructions
* Moving to safer or higher locations when instructed
* Avoiding floodwater
* Avoiding flooded roads
* Taking additional care of children and vulnerable people
* Following reliable official information

### After a Flood

* Returning only when authorities indicate that it is safe
* Avoiding contaminated or standing water
* Taking electrical safety precautions
* Following public-health guidance regarding drinking water
* Documenting damage and contacting appropriate authorities

The AI assistant is intended to make preparedness information easier to access and understand.

---

## Data Sources

### Flood Data

The project uses the:

**India Flood Inventory-Impacts (IFI-Impacts) [1967-2023]**

Developed by the HydroSense Lab at IIT Delhi and published through Zenodo.

The project uses historical flood-event information for Kerala to construct district-level flood-event records and prediction targets.

### Rainfall Data

The MVP uses historical rainfall data from **ERA5 through the Open-Meteo API**.

Rainfall indicators are aggregated at the Kerala district level for the modeling workflow.

---

## Technology Stack

### Machine Learning

* Python
* Pandas
* NumPy
* Scikit-learn
* Random Forest
* Logistic Regression

### AI / RAG

* Sentence Transformers
* `all-MiniLM-L6-v2`
* Retrieval-Augmented Generation
* OpenRouter API
* Large Language Model

### Backend

* Python
* FastAPI
* Uvicorn

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* React Markdown

### Data Processing

* GeoPandas
* Shapely
* Rasterio
* Open-Meteo historical weather data

---

## Project Structure

```text
Asraya AI/
|
├── backend/
│   └── main.py
|
├── data/
│   ├── India_Flood_Inventory_v3.csv
│   ├── district_nwic.GeoJSON
│   ├── kerala_district_boundaries.geojson
│   ├── kerala_district_flood_events.csv
│   ├── kerala_flood_events.csv
│   ├── kerala_flood_targets.csv
│   └── knowledge_base/
│       └── flood_preparedness.txt
|
├── frontend/
│   ├── app/
│   ├── public/
│   ├── package.json
│   └── ...
|
├── notebooks/
│   ├── 01_explore_flood_data.py
│   ├── 02_prepare_kerala_data.py
│   ├── 03_create_district_events.py
│   ├── ...
│   └── 24_generate_ai_guidance.py
|
├── deployment_data/
│   └── ...
|
├── models/
│   └── ...
|
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Running Locally

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/asraya-ai.git
cd asraya-ai
```

### 2. Create a Python Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Never commit the `.env` file to GitHub.

### 5. Start the Backend

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 6. Start the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:3000
```

---

## API Endpoints

### Health Check

```text
GET /
```

### District List

```text
GET /districts
```

### Historical Risk Assessment

```text
GET /risk?district=Kottayam&date=2021-11-10
```

### AI Guidance

```text
POST /guidance
```

Example request:

```json
{
  "question": "What should I do if heavy rainfall is expected?",
  "district": "Kottayam",
  "date": "2021-11-10"
}
```

---

## Example Risk Assessment

Example historical assessment:

```text
District: Kottayam
Date: 2021-11-10
Risk Category: HIGH
Risk Score: 0.582

Rainfall:
1 day: 8.7 mm
3 days: 17.7 mm
7 days: 57.6 mm
30 days: 350.0 mm
```

This represents a **model-derived historical assessment** and should not be interpreted as an official warning.

---

## Limitations

The current MVP has several limitations.

### Historical Data

The model learns from recorded historical flood events. A value of zero means that a flood onset was not recorded in the dataset; it does not prove that flooding did not occur.

### Class Imbalance

Flood-onset events are much less frequent than non-flood days. This creates a significant class-imbalance problem and contributes to false positives.

### Rainfall-Only Modeling

The current model primarily uses rainfall-derived features.

Important factors such as:

* Elevation
* Slope
* River levels
* Soil moisture
* Drainage
* Land use
* Satellite observations
* Dam operations
* Real-time hydrological conditions

are not currently included.

### Geographic Scope

The current MVP focuses on Kerala, India.

### Not an Official Warning System

Āśraya AI does not issue official flood warnings or evacuation orders.

Users should follow instructions from relevant government authorities and emergency services during real-world emergencies.

---

## Future Scope

Planned future improvements include:

* Real-time rainfall monitoring
* Satellite-based flood detection
* Elevation and slope features
* River and reservoir information
* More advanced hydrological features
* Community flood reporting
* Multilingual support
* Localized voice assistance
* Notification systems
* Mobile application
* Improved model calibration
* Broader geographic coverage
* Integration with additional official disaster-management data sources

---

## SDG Alignment

Āśraya AI primarily supports:

### SDG 13 — Climate Action

The platform focuses on climate-related disaster preparedness, risk awareness, and community resilience.

### SDG 11 — Sustainable Cities and Communities

The project also contributes to disaster resilience and safer communities by improving access to local risk information and preparedness guidance.

---

## Project Status

**Current Status: MVP / Research Prototype**

The current system includes:

* Historical flood data processing
* Kerala district-level dataset creation
* Rainfall feature engineering
* Flood-onset ML modeling
* Risk assessment
* RAG knowledge retrieval
* AI preparedness guidance
* FastAPI backend
* Next.js web interface

The project is currently being prepared for deployment and further evaluation.

---

## Responsible Use

Āśraya AI is designed as an educational and research-oriented disaster resilience tool.

It should not be used as the sole basis for:

* Emergency evacuation decisions
* Medical decisions
* Disaster-response decisions
* Infrastructure safety decisions
* Government emergency management

During an actual emergency, always follow current instructions from official authorities and emergency services.

---

## License

This project is currently intended for educational, research, and demonstration purposes.

A formal open-source license may be added in a future release.

---

## Author

**Anjana S V**



---

## Acknowledgements

This project makes use of publicly available datasets, open-source software, and publicly accessible AI and weather-data services.

The project is intended to demonstrate how machine learning, retrieval-augmented generation, and accessible web technologies can be combined to support community disaster resilience.

---

**Āśraya AI — Prepare. Protect. Recover.**
