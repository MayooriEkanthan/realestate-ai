# 🏡 RealEstate AI: Smart Property Valuation & Real Estate Advisory Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.146+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini_API-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-EB6324?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-2094f3?style=for-the-badge&logo=uvicorn&logoColor=white)](https://www.uvicorn.org/)

**RealEstate AI** is an intelligent property intelligence, automated valuation, and advisory platform built specifically for the **Sri Lankan real estate market** (covering Colombo prime zones, growing suburbs, and regional districts). The system integrates machine learning price prediction, multimodal property image assessment, and conversational AI guidance powered by Google Gemini to assist buyers, sellers, and property investors in making data-driven decisions.

---

## 🏗️ Architecture Overview

The platform uses a decoupled **client-server architecture** with a FastAPI backend orchestrating predictive ML models and Gemini generative AI services, ready to integrate with a modern web or mobile frontend:

```text
realestate-ai/
├── backend/
│   ├── data/                 # Datasets and market trend historical records
│   ├── models/               # Trained ML estimators (XGBoost, Regressors, Scalers)
│   ├── routers/              # Modular FastAPI route handlers
│   ├── scripts/              # Verification, data prep, and model test scripts
│   ├── services/
│   │   ├── __init__.py
│   │   └── llm.py            # Gemini AI client (advisory, descriptions, analysis)
│   ├── venv/                 # Python virtual environment (ignored in git)
│   ├── .env                  # Environment configuration & API credentials
│   ├── main.py               # FastAPI application entry point & CORS configuration
│   └── requirements.txt      # Pinned Python package dependencies
├── frontend/                 # Client web application (React / Vite)
├── .gitignore                # Git exclusions
└── README.md                 # Project documentation
```

---

## ✨ Key Capabilities

### 🤖 Intelligent Sri Lanka Real Estate Advisor
- **Context-Aware Assistance:** Answers queries on prime Colombo neighborhoods (Colombo 3, 5, 7), suburban hubs (Rajagiriya, Battaramulla, Nawala), and emerging investment corridors.
- **Mortgage & Legal Clarity:** Explains typical purchasing workflows, deed verification advice, and bank financing guidelines in Sri Lanka.
- **Natural Language Inquiry:** Conversational assistance for buyers, tenants, and overseas diaspora investors.

### 📈 Predictive Property Valuation
- **Machine Learning Regressors:** Predicts estimated property market values based on location, land extent (in perches), square footage, bedrooms, bathrooms, and floor levels.
- **Market Comparison:** Compares properties against prevailing neighborhood per-perch and square-foot averages.

### ✍️ Automated Listing Description Generator
- **Compelling Marketing Copy:** Generates professional, SEO-tailored listing summaries, highlight bullet points, and lifestyle highlights in seconds.
- **Tone Flexibility:** Produces copy tailored for luxury villas, commercial spaces, or family suburban homes.

### 📊 Investment & Yield Analysis
- **ROI & Rental Yield Insights:** Evaluates expected monthly rental yield against acquisition cost.
- **Growth Projections:** Highlights appreciation potential, infrastructure catalysts (e.g., highway access, urban development), and investment risk factors.

### 📸 Visual Property & Condition Assessment
- **Multimodal Evaluation:** Analyzes interior and exterior property photos using Gemini's visual models to evaluate finishes, structural condition, natural lighting, and recommend value-boosting renovations.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend & APIs** | FastAPI, Python 3.10+, Uvicorn, Pydantic, Python-Multipart |
| **AI & Generative Language** | Google GenAI SDK (`google-genai`), Gemini 2.5 Flash / Flash Latest |
| **Machine Learning & Analytics** | Scikit-Learn, XGBoost, Joblib, NumPy, Pandas |
| **Image Processing** | Pillow (PIL) |
| **Environment Management** | Python-Dotenv, Python Virtual Environment (`venv`) |
| **Frontend Integration** | React / Vite (configured with CORS on `http://localhost:5173`) |
| **Testing & Scripting** | Python TestClient, Pytest, Custom Test Scripts |
| **Version Control** | Git, GitHub |

---

## 🎨 Design System & Palette

| Role | Colour Name | HEX | Description |
| :--- | :--- | :---: | :--- |
| **Primary** | Deep Slate | `#0F172A` | Sleek modern foundation & typography |
| **Secondary / Accent** | Warm Emerald | `#059669` | Trust, property growth & value |
| **Highlight** | Champagne Gold | `#D97706` | Luxury listings & premium metrics |
| **Surface** | Soft Pearl | `#F8FAFC` | Clean cards & readability |

**Brand:** RealEstate AI · **Focus:** Sri Lanka Property Intelligence · **Tagline:** *"Data-Driven Real Estate, Powered by AI"*

---

## 🚀 Getting Started

### Prerequisites

* [Python 3.10+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/)
* A [Google AI Studio API Key](https://aistudio.google.com/) for Gemini

---

### 1. Clone the Repository

```bash
git clone https://github.com/MayooriEkanthan/realestate-ai.git
cd realestate-ai
```

### 2. Navigate to Backend & Set Up Environment

```powershell
cd backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file inside the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

### 5. Verify the AI Service

Run the standalone verification script to test Gemini integration:

```powershell
python scripts/test_llm.py
```

*Expected output: Ayubowan greeting and real estate assistance confirmation.*

---

### 6. Start the Backend Server

```powershell
uvicorn main:app --reload --port 8000
```

* The API server will launch at: `http://127.0.0.1:8000`
* **Health Check**: `http://127.0.0.1:8000/api/health`
* **Interactive Swagger Documentation**: `http://127.0.0.1:8000/docs`
* **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## 🔐 Security & Best Practices

* Sensitive keys (`GEMINI_API_KEY`) and credentials must remain in `.env` and **never** be committed to Git.
* The `.gitignore` file is pre-configured to exclude all virtual environments (`venv/`), Python caches (`__pycache__/`), secrets (`.env`), and node packages (`node_modules/`).

---

## 🤝 Branching & Commit Guidelines

To maintain clean and trackable development standards:

* **Branch format:** `feature/<feature-name>`, `fix/<bug-name>`, `chore/<task-name>`
* **Commit convention:** `[REALESTATE-AI] YYYY-MM-DD | <Type>: <Description>`

*Example:* `[REALESTATE-AI] 2026-10-19 | Feat: Implement Gemini LLM real estate advisory service`

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
