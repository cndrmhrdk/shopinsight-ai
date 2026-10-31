# ShopInsight AI — Sales Analysis Agent

A simple, fully local AI agent that analyzes e-commerce sales data and
generates clear, data-backed insights and recommendations.

**No API keys. No external services. Pure Python standard library.**

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

## Project Structure

```
shopinsight_ai/
├── data/
│   └── sales_data.csv      # ShopInsight sales dataset (448 orders, Jan-Mar 2026)
├── agent.py                # Data loading, analysis engine, Q&A agent
├── main.py                 # Entry point (run this)
├── requirements.txt        # No dependencies — standard library only
└── README.md
```

## Quick Start

```bash
# Python 3.9+ required — no pip install needed
python main.py
```

That's it.

## What the Output Looks Like

```
Section 1 — Sales Overview         (period, totals, products, categories, avg order)
Section 2 — Top Product Performance (top 5 by units and by revenue, category breakdown)
Section 3 — Low Sales Performance   (products in the bottom third by volume)
Section 4 — Key Insights            (rule-based factual observations from the data)
Section 5 — Simple Recommendations  (rule-based actionable suggestions)
             |
             v
Interactive Q&A loop
```

## Dataset

`data/sales_data.csv` — 448 orders, January to March 2026.

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
