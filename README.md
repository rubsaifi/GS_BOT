# 🎯 GoalBot – SRBSOM Goal Sheet AI Chatbot

An intelligent AI chatbot that helps SRBSOM employees understand their Goal Sheet KPIs, scoring slabs, and provides personalized guidance to maximize quarterly scores.

---

## 🚀 Features

- **💬 Conversational Chat** — Ask anything about your Goal Sheet in natural language
- **🧮 Score Calculator** — Enter your current numbers and get gap analysis + AI advice
- **📋 KPI Reference** — Browse all parameters and scoring slabs
- **🎯 Score 100 Guide** — Ask the bot for a complete action plan to score maximum
- **⚠️ Risk Alerts** — Automatically highlights negative-scoring parameters (e.g., NI audit rating)

---

## 🛠️ Tech Stack

| Layer | Technology | Cost |
|-------|-----------|------|
| UI | **Streamlit** | Free |
| LLM | **GROQ API** (Llama 3.3 70B) | Free tier |
| Embeddings | **sentence-transformers** (local) | Free |
| Vector DB | **ChromaDB** (local, persistent) | Free |
| RAG Pipeline | Custom Python | Free |
| Data | **pandas + openpyxl** | Free |

---

## 📂 Project Structure

```
goal_chatbot/
├── app.py                    # Main Streamlit application
├── create_sample_data.py     # Generates sample Excel files for demo
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── data/                     # Excel files go here
│   ├── kpi_master.xlsx       # File 1: KPI names, max scores, weightage
│   └── parameter_scoring.xlsx # File 2: Slab-based scoring logic
├── utils/
│   ├── excel_loader.py       # Reads Excel → knowledge chunks
│   ├── vector_store.py       # ChromaDB vector store management
│   └── llm_groq.py           # GROQ LLM integration
└── chroma_db/                # Auto-created: persistent vector store
```

---

## ⚡ Setup & Run

### 1. Install Dependencies
```bash
cd goal_chatbot
pip install -r requirements.txt
```

### 2. Get GROQ API Key (Free)
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up / Log in
3. Go to API Keys → Create API Key
4. Copy the key

### 3. Set API Key
```bash
# Option A: Environment variable
export GROQ_API_KEY=your_key_here

# Option B: Create .env file
cp .env.example .env
# Edit .env and add your key
```

### 4. Prepare Excel Files
Place your 2 Excel files in the `data/` folder:

**File 1: `kpi_master.xlsx`** — Must have these columns:
| Parameter | Category | Max Score | Weightage (%) | Target (Full Score) | Negative Score Applicable | Remarks |
|-----------|----------|-----------|---------------|---------------------|--------------------------|---------|

**File 2: `parameter_scoring.xlsx`** — Must have these columns:
| Parameter | Slab Min | Slab Max | Score | Description |
|-----------|----------|----------|-------|-------------|

> **Note:** If column names differ, update `KPI_COLS` and `SCORING_COLS` dictionaries in `utils/excel_loader.py`

### 5. Run the App
```bash
streamlit run app.py
```

Open browser at: [http://localhost:8501](http://localhost:8501)

---

## 📊 Excel File Format Guide

### KPI Master File (File 1)
```
Parameter          | Category  | Max Score | Weightage | Target | Negative | Remarks
Amendments         | Operations| 10        | 6%        | 10     | No       | Monthly amendments
AOF                | Business  | 15        | 9%        | 20     | No       | New accounts
Branch Audit Rating| Compliance| -5        | 5%        | S/A    | Yes      | NI gives -5 pts
```

### Parameter Scoring File (File 2)
```
Parameter  | Slab Min | Slab Max | Score | Description
Amendments | 0        | 0        | 0     | No amendments done
Amendments | 1        | 2        | 2     | 1-2 amendments
Amendments | 3        | 5        | 5     | 3-5 amendments
Amendments | 6        | 9        | 8     | 6-9 amendments
Amendments | 10       | 999      | 10    | 10+ amendments – Full score
```

---

## 💬 Sample Questions

```
"How do I score 100 this quarter?"
"What is the scoring slab for Amendments?"
"How many AOFs do I need for full score?"
"What happens if my Branch Audit Rating is NI?"
"Which parameters carry the most weightage?"
"I did 8 AOF and 5 Amendments — what is my score?"
"What should I focus on in Q3 to maximize my score?"
"Explain the CUbe scoring slabs"
```

---

## 🔧 Customisation

### Update Column Names
If your Excel column names differ, edit `utils/excel_loader.py`:
```python
KPI_COLS = {
    "parameter": "Your Column Name",   # change these
    "max_score": "Your Max Score Col",
    ...
}
```

### Change LLM Model
In `utils/llm_groq.py`, update:
```python
GROQ_MODEL = "llama-3.3-70b-versatile"  # or "mixtral-8x7b-32768", "gemma2-9b-it"
```

### Use Local LLM (Ollama)
Replace the `ask_goalbot` function in `utils/llm_groq.py` with an Ollama call:
```python
import ollama
response = ollama.chat(model="llama3", messages=messages)
```

---

## 🔒 Data Privacy
- All embeddings are computed **locally** using sentence-transformers
- ChromaDB stores data **locally** on your machine
- Only the question + relevant context is sent to GROQ API
- Your full Excel data never leaves your machine

---

## 📞 Support
Upload your actual Excel files to the app and click **Build Knowledge Base** to get started.
For issues, check the column name mapping in `excel_loader.py`.
