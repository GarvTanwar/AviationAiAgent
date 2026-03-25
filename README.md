# ✈️ Aviation AI Agent

AI-powered aviation logistics assistant for route optimization, pricing, and knowledge retrieval using open-source models.

---

## 🚀 Features

- 📦 **Smart Pricing**
  - Calculates shipment cost with full breakdown

- 🧭 **Route Optimization**
  - Finds cheapest, fastest, lowest-risk, and balanced routes

- 🤖 **Natural Language Input**
  - Convert user queries into structured shipment data

- 🧠 **AI Explanation**
  - Explains route selection and pricing decisions

- 📚 **RAG Knowledge Assistant**
  - Upload PDF/TXT files and query them using AI

---

## 🛠️ Tech Stack

- Python, Streamlit  
- Ollama (Llama 3 / Mistral)  
- FAISS + Sentence Transformers  
- NetworkX, Pandas  

---

## ⚙️ Setup

```bash
git clone <your-repo-url>
cd AviationAiAgent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3.1
streamlit run app.py