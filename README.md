\# Āśraya AI



\### AI-Driven Community Disaster Resilience Platform



\*\*Prepare. Protect. Recover.\*\*



Āśraya AI is an AI-powered disaster resilience platform focused on helping communities understand flood risk and access practical preparedness guidance.



The current MVP focuses on \*\*Kerala, India\*\*, using historical flood events and rainfall patterns to estimate the likelihood of a \*\*recorded flood onset on the following day\*\* and provide context-aware flood preparedness guidance.



\---



\## Problem



Floods can cause severe damage to communities, infrastructure, livelihoods, and human lives.



While official warnings and emergency systems are essential, communities also need accessible information that helps them understand:



\* What the available risk information means

\* How rainfall patterns relate to historical flood events

\* What they can do before flooding

\* How to stay safer during flooding

\* What precautions to take after flooding



Āśraya AI explores how machine learning and retrieval-augmented AI can support these needs through a simple community-facing interface.



\---



\## Solution



Āśraya combines a historical flood-risk assessment model with an AI preparedness assistant.



```text

Historical Flood Data

&#x20;       +

Historical Rainfall

&#x20;       ↓

&#x20;  ML Risk Model

&#x20;       ↓

&#x20;Flood Risk Assessment

&#x20;       ↓

&#x20;District + Date + Risk Context

&#x20;       ↓

&#x20;RAG Knowledge Base

&#x20;       +

&#x20;     LLM

&#x20;       ↓

&#x20;AI Preparedness Guidance

```



The platform is designed around three stages:



\*\*Assess → Understand → Prepare\*\*



\---



\## Current MVP



The current MVP provides:



\* Kerala district selection

\* Historical rainfall information

\* Historical flood-event data

\* Next-day flood-onset classification

\* Model-derived risk score

\* Risk categories

\* Rainfall indicators

\* Context-aware AI preparedness guidance

\* Retrieval-augmented generation (RAG)

\* FastAPI backend

\* Next.js web interface



\---



\## Machine Learning



The ML component uses historical rainfall indicators to estimate whether a \*\*recorded flood onset occurred on the following day\*\*.



The model uses rainfall information available through day \*\*T\*\* to assess the target for day \*\*T+1\*\*.



\### Features



\* 1-day cumulative rainfall

\* 3-day cumulative rainfall

\* 7-day cumulative rainfall

\* 30-day cumulative rainfall

\* Maximum rainfall within the previous 3 days

\* Maximum rainfall within the previous 7 days



\### Models explored



\* Logistic Regression

\* Random Forest



A chronological train/test split is used:



```text

Training: before 2020

Testing:  2020 onward

```



Because recorded flood events are highly imbalanced relative to non-event days, model evaluation considers metrics such as:



\* Precision

\* Recall

\* F1-score

\* ROC-AUC

\* PR-AUC



Accuracy is not treated as the primary evaluation metric.



\---



\## Risk Assessment



The application converts the model output into four presentation categories:



| Risk Category | Model Score |

| ------------- | ----------: |

| LOW           |       < 10% |

| MODERATE      |      10–30% |

| HIGH          |      30–60% |

| VERY HIGH     |       ≥ 60% |



These thresholds are \*\*presentation thresholds used by the MVP\*\* and are not official government flood-warning standards.



The model score is also \*\*not a calibrated probability\*\* and should not be interpreted as an exact percentage chance of flooding.



\---



\## AI Preparedness Assistant



Āśraya uses a small trusted knowledge base containing practical flood preparedness, safety, and recovery guidance.



The system uses \*\*Retrieval-Augmented Generation (RAG)\*\* to retrieve relevant information before generating a response.



The assistant can provide guidance related to:



\### Before flooding



\* Emergency preparedness

\* Essential supplies

\* Safer locations

\* Evacuation planning

\* Protecting vehicles and valuables

\* Following official information



\### During flooding



\* Avoiding floodwater

\* Electrical safety

\* Moving to safer locations

\* Protecting children and vulnerable people

\* Using verified emergency information



\### After flooding



\* Safe return

\* Electrical safety

\* Drinking-water precautions

\* Public-health guidance

\* Reporting and documenting damage



Āśraya is an informational support system and does \*\*not\*\* issue official evacuation orders or replace emergency authorities.



\---



\## Technology Stack



\### Machine Learning



\* Python

\* Pandas

\* NumPy

\* Scikit-learn



\### Data



\* India Flood Inventory

\* Historical rainfall data

\* Kerala district boundaries

\* Open/public data sources



\### AI



\* Sentence Transformers

\* Retrieval-Augmented Generation

\* OpenRouter-compatible LLM API



\### Backend



\* FastAPI

\* Uvicorn

\* Python



\### Frontend



\* Next.js

\* React

\* TypeScript

\* Tailwind CSS

\* React Markdown



\---



\## Project Structure



```text

asraya-ai/

│

├── backend/

│   └── main.py

│

├── data/

│   ├── India\_Flood\_Inventory\_v3.csv

│   ├── district\_nwic.GeoJSON

│   ├── kerala\_district\_boundaries.geojson

│   ├── kerala\_district\_flood\_events.csv

│   ├── kerala\_flood\_events.csv

│   ├── kerala\_flood\_targets.csv

│   └── knowledge\_base/

│       └── flood\_preparedness.txt

│

├── frontend/

│   ├── app/

│   ├── public/

│   ├── package.json

│   └── ...

│

├── notebooks/

│   ├── 01\_explore\_flood\_data.py

│   ├── 02\_prepare\_kerala\_data.py

│   ├── ...

│   ├── 17\_train\_flood\_models.py

│   ├── 20\_build\_rag.py

│   ├── 22\_ai\_guidance\_engine.py

│   └── 24\_generate\_ai\_guidance.py

│

├── .gitignore

└── README.md

```



Generated datasets and model/RAG artifacts are intentionally excluded from the repository and can be recreated using the processing scripts.



\---



\## Running Locally



\### 1. Clone the repository



```bash

git clone https://github.com/YOUR\_USERNAME/asraya-ai.git

cd asraya-ai

```



\### 2. Create the Python environment



```powershell

python -m venv .venv

```



Activate it on Windows:



```powershell

.venv\\Scripts\\Activate.ps1

```



\### 3. Install backend dependencies



```powershell

pip install pandas numpy scikit-learn fastapi uvicorn python-dotenv openai sentence-transformers

```



\### 4. Configure environment variables



Create a `.env` file in the project root:



```env

OPENROUTER\_API\_KEY=your\_api\_key\_here

```



\*\*Never commit `.env` to GitHub.\*\*



\### 5. Start the backend



```powershell

uvicorn backend.main:app --reload

```



The backend will run at:



```text

http://127.0.0.1:8000

```



\### 6. Start the frontend



Open another terminal:



```powershell

cd frontend

npm install

npm run dev

```



Open:



```text

http://localhost:3000

```



\---



\## Important Limitations



Āśraya AI is currently a research/project MVP.



The system:



\* Uses historical data rather than real-time flood monitoring

\* Focuses on Kerala

\* Uses historical rainfall patterns as the primary ML input

\* Predicts recorded flood onset rather than exact flood depth, location, or severity

\* Does not provide official warnings

\* Does not replace government disaster-management systems

\* May produce false positives and false negatives

\* Uses a model score that has not been probability-calibrated



For real emergencies, users should follow official government and emergency-service instructions.



\---



\## Future Scope



Potential future improvements include:



\* Real-time rainfall and weather integration

\* Elevation and slope features

\* Satellite imagery

\* River and reservoir information

\* Community flood reporting

\* Multilingual guidance

\* Localized emergency information

\* Notifications and alerts

\* More extensive geographical coverage

\* Improved model calibration

\* Larger and more diverse training datasets



\---



\## SDG Alignment



Āśraya AI primarily supports:



\*\*SDG 13 — Climate Action\*\*



and contributes to:



\*\*SDG 11 — Sustainable Cities and Communities\*\*



The project focuses on improving community preparedness and resilience to climate-related disaster risks.



\---



\## Project Status



\*\*Current status: Working MVP\*\*



The complete local pipeline is operational:



```text

Data → Feature Engineering → ML → Risk Assessment

&#x20;                                     ↓

&#x20;                             RAG + LLM Guidance

&#x20;                                     ↓

&#x20;                              Web Interface

```



\---



\## Disclaimer



Āśraya AI provides model-derived historical risk information and general preparedness guidance for educational and research purposes.



It is \*\*not an official flood-warning system\*\*, emergency-management authority, or evacuation service.



For active emergencies, always follow instructions from local authorities and official emergency services.



