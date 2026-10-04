# 🌬️ AirAware — AI Air Quality Assistant

100% local, zero API keys, multi-agent AI system for air quality monitoring and health advisory.

## 🌟 Features

- 📊 **Live AQI Dashboard** — Real-time (mock) AQI with pollutant breakdown
- 🩺 **Personalized Health Advisory** — RAG-based advice for asthma, heart, pregnancy, etc.
- 🗺️ **Smart Route Planner** — Least polluted routes with Folium maps
- 📈 **Trends & Forecast** — 7/30 day history + 3-day prediction
- 🏫 **Community Alerts** — School closures, office advisories, user reports

## 🛠️ Tech Stack (Zero API Keys!)

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Charts | Plotly |
| Maps | Folium + OpenStreetMap |
| Embeddings | sentence-transformers (local) |
| Vector Search | FAISS (local) |
| AI Logic | Multi-Agent + RAG (pure Python) |
| Database | SQLite |
| Data | Mock generator (realistic patterns) |

## 🚀 Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/airaware.git
cd airaware
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
streamlit run app.py
