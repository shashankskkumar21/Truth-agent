# Product Truth Agent — 3D Visual Edition

This is the full Product Truth Agent project with a new 3D-style visual interface.

The original backend is preserved:
- supplied Excel dataset
- web product retrieval
- exact product candidate selection
- real GPT-5.6 Luna CIS integration
- module classification
- characteristic coding
- taxonomy validation
- evidence and raw-result inspection

The new `app.py` is the presentation layer. It gives the application a polished 3D / layered product-analysis homepage while keeping the actual pipeline underneath.

## 1. Configure the real Luna API

Copy the environment template:

### Mac / Linux
```bash
cp .env.example .env
```

### Windows PowerShell
```powershell
Copy-Item .env.example .env
```

Open `.env` and set the real company values:

```text
CIS_LLM_ENDPOINT=https://llm-api-cis.azure-intlsd-np.nielsencsp.net/
CIS_LLM_API_KEY=Bearer YOUR_ACTUAL_KEY
CIS_LLM_MODEL=hack-fest-gpt-5.6-luna
```

Do not put the key in source code or send it in chat.

Optional web search:
```text
TAVILY_API_KEY=
```

The built-in DuckDuckGo/Bing HTML fallback remains available when Tavily is blank.

## 2. Create the environment

### Mac / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 3. Verify the API configuration without revealing the key

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Endpoint:', bool(os.getenv('CIS_LLM_ENDPOINT'))); print('API key:', bool(os.getenv('CIS_LLM_API_KEY'))); print('Model:', os.getenv('CIS_LLM_MODEL'))"
```

Expected:

```text
Endpoint: True
API key: True
Model: hack-fest-gpt-5.6-luna
```

## 4. Run the 3D visual website

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

The homepage is the new visual 3D-style experience. Select **Get Started** to open the live analysis workflow.

## 5. How the application works

```text
Excel dataset
     ↓
Product description / barcode / brand
     ↓
Web retrieval
     ↓
Candidate product pages
     ↓
GPT-5.6 Luna product matching
     ↓
Module classification
     ↓
Module characteristics + guidelines
     ↓
GPT-5.6 Luna evidence-based coding
     ↓
Taxonomy validation
     ↓
Evidence / reasoning / result
```

## Important network note

The CIS Luna endpoint is an internal company endpoint. If the machine cannot reach it, the application may show a connection timeout even when the API key is correct.

Use only the approved company VPN / Zscaler / private-access / hackathon network route. Do not bypass company security controls.

## Project structure

```text
Product_Truth_Agent_3D/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   └── product_truth_agent_dataset.xlsx
├── src/
│   ├── data_loader.py
│   ├── retrieval.py
│   ├── luna_agent.py
│   ├── pipeline.py
│   ├── validator.py
│   ├── export.py
│   └── evaluate.py
├── outputs/
└── run.sh
```
