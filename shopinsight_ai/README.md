# ShopInsight AI — Sales Analysis Agent

A simple, fully local AI agent that analyzes e-commerce sales data and
generates clear, data-backed insights and recommendations.

**No API keys. No external services. Pure Python.**

---

## Quick Start

### Option A — Web Dashboard (Streamlit) ⭐ Recommended for demo

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Open **http://localhost:8501** in your browser.

> **Windows tip:** If `streamlit` is not found on PATH, use `python -m streamlit run app.py` instead.

### Option B — Terminal (no install needed)

```bash
python main.py
```

---

## Workflow

```
Sales Data (CSV)
     |
     v
Data Analysis  (aggregation, rankings, low-performer detection)
     |
     v
Key Insights   (rule-based observations from the data)
     |
     v
Recommendations  (rule-based actionable suggestions)
     |
     v
Interactive Q&A  (keyword-based questions about the dataset)
```

---

## Project Structure

```
shopinsight_ai/
├── data/
│   └── sales_data.csv      # ShopInsight dataset (447 orders, Jan–Mar 2026)
├── agent.py                # Data loading, analysis engine, Q&A agent
├── app.py                  # Streamlit web dashboard  ← GUI entry point
├── main.py                 # Terminal entry point
├── requirements.txt        # streamlit only
└── README.md
```

---

## Dashboard Sections

| # | Section | What it shows |
|---|---|---|
| 1 | Sales Overview | Key metrics as cards (revenue, orders, units, avg order) |
| 2 | Top Product & Category Performance | Bar charts + ranked tables |
| 3 | Low Sales Performance | Table of products in the bottom third by volume |
| 4 | Key Insights | Rule-based factual observations from the data |
| 5 | Simple Recommendations | Rule-based actionable suggestions |
| 6 | Interactive Q&A | Ask any question; answered from the dataset |

---

## Dataset

`data/sales_data.csv` — 447 orders, January to March 2026.

| Column | Description |
|---|---|
| `order_id` | Unique order identifier |
| `date` | Order date (YYYY-MM-DD) |
| `product_name` | Product sold |
| `category` | Product category |
| `quantity_sold` | Units sold in this order |
| `unit_price_idr` | Unit price in IDR |
| `revenue_idr` | Total revenue for this order (IDR) |

**Products:** Wireless Mouse, Mechanical Keyboard, USB-C Charger,
Sneakers, Hoodie, T-Shirt, Backpack, Water Bottle

**Categories:** Electronics, Fashion, Lifestyle

---

## Sample Q&A Questions

```
What is the total revenue?
Which product sells the most?
What are the low-performing products?
Tell me about the Electronics category.
How many orders are there?
What is the date range of the data?
Tell me about Sneakers.
```
