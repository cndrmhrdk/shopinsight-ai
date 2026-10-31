"""
ShopInsight AI — Streamlit Dashboard
Run:  streamlit run app.py

No API keys or external services required.
"""

import pathlib
import streamlit as st

from agent import load_csv, SalesAnalysis, QAAgent

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShopInsight AI",
    page_icon="📊",
    layout="wide",
)

# ── Load & cache data ─────────────────────────────────────────────────────────
DATA_FILE = pathlib.Path(__file__).parent / "data" / "sales_data.csv"

@st.cache_resource
def get_analysis() -> SalesAnalysis:
    rows = load_csv(str(DATA_FILE))
    return SalesAnalysis(rows)

@st.cache_resource
def get_qa_agent(_analysis: SalesAnalysis) -> QAAgent:
    return QAAgent(_analysis)

analysis = get_analysis()
qa_agent = get_qa_agent(analysis)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 ShopInsight AI — Sales Analysis Agent")
st.caption(
    f"Dataset: **{DATA_FILE.name}** · "
    f"Period: **{analysis.date_range[0]}** → **{analysis.date_range[1]}** · "
    f"**{analysis.total_orders:,}** orders · **{analysis.unique_products}** products"
)
st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Sales Overview
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("1 · Sales Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue (IDR)",   f"{analysis.total_revenue:,.0f}")
c2.metric("Total Orders",          f"{analysis.total_orders:,}")
c3.metric("Total Units Sold",      f"{analysis.total_units:,}")
c4.metric("Avg Order Value (IDR)", f"{analysis.avg_order_value:,.0f}")

col_a, col_b = st.columns(2)
col_a.metric("Products Tracked", analysis.unique_products)
col_b.metric("Categories",       analysis.unique_categories)

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Top Product & Category Performance
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("2 · Top Product & Category Performance")

left, right = st.columns(2)

# ── Chart: Revenue by Category ──
with left:
    st.markdown("**Revenue by Category (IDR)**")
    cat_labels = [c for c, _ in analysis.categories_by_revenue]
    cat_values = [v for _, v in analysis.categories_by_revenue]
    st.bar_chart(
        data=dict(zip(cat_labels, cat_values)),
        use_container_width=True,
        height=260,
    )

# ── Chart: Top 5 Products by Revenue ──
with right:
    st.markdown("**Top 5 Products by Revenue (IDR)**")
    top_rev_labels = [p for p, _ in analysis.products_by_revenue[:5]]
    top_rev_values = [v for _, v in analysis.products_by_revenue[:5]]
    st.bar_chart(
        data=dict(zip(top_rev_labels, top_rev_values)),
        use_container_width=True,
        height=260,
    )

left2, right2 = st.columns(2)

# ── Table: Top 5 by Units ──
with left2:
    st.markdown("**Top 5 Products by Units Sold**")
    rows_qty = [
        {
            "Rank": i,
            "Product": p,
            "Units Sold": f"{q:,}",
            "Share": f"{q / analysis.total_units * 100:.1f}%",
        }
        for i, (p, q) in enumerate(analysis.products_by_qty[:5], 1)
    ]
    st.table(rows_qty)

# ── Table: Top 5 by Revenue ──
with right2:
    st.markdown("**Top 5 Products by Revenue**")
    rows_rev = [
        {
            "Rank": i,
            "Product": p,
            "Revenue (IDR)": f"{r:,.0f}",
            "Share": f"{r / analysis.total_revenue * 100:.1f}%",
        }
        for i, (p, r) in enumerate(analysis.products_by_revenue[:5], 1)
    ]
    st.table(rows_rev)

# ── Units by Category bar chart ──
st.markdown("**Units Sold by Category**")
cat_qty_labels = [c for c, _ in analysis.categories_by_qty]
cat_qty_values = [v for _, v in analysis.categories_by_qty]
st.bar_chart(
    data=dict(zip(cat_qty_labels, cat_qty_values)),
    use_container_width=True,
    height=220,
)

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Low Sales Performance
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("3 · Products with Low Sales Performance")

if analysis.low_performers:
    avg_qty = analysis.total_units / analysis.unique_products
    lp_rows = [
        {
            "Product": p,
            "Units Sold": q,
            "Revenue (IDR)": f"{analysis._revenue_by_product[p]:,.0f}",
            "vs Store Avg": f"{q - avg_qty:+.0f} units",
        }
        for p, q in analysis.low_performers
    ]
    st.table(lp_rows)
    st.caption(f"Store average: **{avg_qty:.0f} units/product**. "
               "Low performers are products in the bottom third by volume.")
else:
    st.info("All products are performing above the low-sales threshold.")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Key Insights
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("4 · Key Insights")

top_qty_product, top_qty_val   = analysis.products_by_qty[0]
top_rev_product, top_rev_val   = analysis.products_by_revenue[0]
top_cat, top_cat_rev           = analysis.categories_by_revenue[0]
bottom_cat, bottom_cat_rev     = analysis.categories_by_revenue[-1]
top_qty_pct  = top_qty_val / analysis.total_units   * 100
top_rev_pct  = top_rev_val / analysis.total_revenue * 100
top_cat_pct  = top_cat_rev / analysis.total_revenue * 100
bot_cat_pct  = bottom_cat_rev / analysis.total_revenue * 100

st.info(f"**Best-Selling Product by Volume:** '{top_qty_product}' leads with "
        f"{top_qty_val:,} units sold ({top_qty_pct:.1f}% of all units).")

st.info(f"**Top Revenue-Generating Product:** '{top_rev_product}' generated "
        f"IDR {top_rev_val:,.0f} ({top_rev_pct:.1f}% of total revenue).")

if top_qty_product != top_rev_product:
    st.info(f"**Volume vs. Revenue Leaders Differ:** '{top_qty_product}' sells the "
            f"most units, but '{top_rev_product}' earns the most revenue — its higher "
            f"unit price drives revenue leadership despite lower volume.")

st.info(f"**Dominant Category:** '{top_cat}' accounts for {top_cat_pct:.1f}% of "
        f"total revenue (IDR {top_cat_rev:,.0f}).")

st.info(f"**Lowest-Revenue Category:** '{bottom_cat}' contributes only "
        f"{bot_cat_pct:.1f}% of total revenue (IDR {bottom_cat_rev:,.0f}) — "
        f"the smallest share among all categories.")

if analysis.low_performers:
    low_names = ", ".join(f"'{p}'" for p, _ in analysis.low_performers)
    st.warning(f"**Low-Performing Products:** {low_names} are in the bottom third "
               f"of sales volume and may need attention.")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Simple Recommendations
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("5 · Simple Recommendations")

st.success(f"✔ **Maintain stock levels for '{top_qty_product}'** — it is the "
           f"highest-volume seller. Stockouts would directly impact a significant "
           f"share of total units sold.")

st.success(f"✔ **Prioritise '{top_rev_product}' in marketing campaigns** — it "
           f"generates the most revenue. Featured promotions or bundle deals can "
           f"amplify its revenue contribution further.")

st.success(f"✔ **Invest in the '{top_cat}' category** — it is the dominant revenue "
           f"driver. Expanding the product range within this category may increase "
           f"overall revenue.")

for p, q in analysis.low_performers:
    rev = analysis._revenue_by_product[p]
    st.warning(f"⚠ **Review '{p}'** (only {q} units / IDR {rev:,.0f} revenue) — "
               f"consider a targeted promotion, a price adjustment, or evaluating "
               f"whether to continue stocking this item.")

st.success(f"✔ **Analyse the '{bottom_cat}' category further** — it contributes the "
           f"least revenue. Investigate whether pricing, visibility, or product "
           f"variety can be improved.")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Interactive Q&A
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("6 · Ask About Your Sales Data")
st.caption("Type a question below. Answers are generated directly from the dataset — no AI API required.")

SAMPLE_QUESTIONS = [
    "What is the total revenue?",
    "Which product sells the most?",
    "What are the low-performing products?",
    "Tell me about the Electronics category.",
    "Tell me about Sneakers.",
    "What is the date range of the data?",
    "How many orders are there?",
]

with st.expander("Sample questions you can ask"):
    for q in SAMPLE_QUESTIONS:
        st.markdown(f"- {q}")

question = st.text_input(
    label="Your question",
    placeholder="e.g. Which product sells the most?",
    label_visibility="collapsed",
)

if question:
    answer = qa_agent.ask(question)
    st.markdown(f"**Answer:** {answer}")

st.divider()
st.caption("ShopInsight AI · Course Capstone Project · Local analysis only · No API keys required")
