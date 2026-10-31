"""
ShopInsight AI — Local Analysis Agent
No API keys. No external services. Pure Python.

Workflow: Sales Data -> Data Analysis -> Key Insights -> Recommendations
"""

import csv
import textwrap
from collections import defaultdict


# ─────────────────────────────────────────────
# 1. DATA LOADING
# ─────────────────────────────────────────────

def load_csv(filepath: str) -> list[dict]:
    """Load the sales CSV and return a list of typed row dicts."""
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append({
                "order_id":      row["order_id"],
                "date":          row["date"],
                "product_name":  row["product_name"],
                "category":      row["category"],
                "quantity_sold": int(row["quantity_sold"]),
                "unit_price":    int(row["unit_price_idr"]),
                "revenue":       int(row["revenue_idr"]),
            })
    return rows


# ─────────────────────────────────────────────
# 2. DATA ANALYSIS
# ─────────────────────────────────────────────

class SalesAnalysis:
    """
    Aggregates all metrics from the raw dataset once at construction time.
    All five report sections are produced as formatted strings.
    """

    def __init__(self, rows: list[dict]):
        self.rows = rows
        self._compute()

    def _compute(self):
        qty_by_product      = defaultdict(int)
        revenue_by_product  = defaultdict(float)
        revenue_by_category = defaultdict(float)
        qty_by_category     = defaultdict(int)

        for r in self.rows:
            p = r["product_name"]
            c = r["category"]
            qty_by_product[p]      += r["quantity_sold"]
            revenue_by_product[p]  += r["revenue"]
            revenue_by_category[c] += r["revenue"]
            qty_by_category[c]     += r["quantity_sold"]

        self.total_orders      = len(self.rows)
        self.total_revenue     = sum(r["revenue"] for r in self.rows)
        self.total_units       = sum(r["quantity_sold"] for r in self.rows)
        self.unique_products   = len(qty_by_product)
        self.unique_categories = len(revenue_by_category)
        self.date_range        = (
            min(r["date"] for r in self.rows),
            max(r["date"] for r in self.rows),
        )
        self.avg_order_value   = self.total_revenue / self.total_orders

        # Sorted rankings
        self.products_by_qty      = sorted(qty_by_product.items(),     key=lambda x: x[1], reverse=True)
        self.products_by_revenue  = sorted(revenue_by_product.items(), key=lambda x: x[1], reverse=True)
        self.categories_by_revenue = sorted(revenue_by_category.items(), key=lambda x: x[1], reverse=True)
        self.categories_by_qty    = sorted(qty_by_category.items(),    key=lambda x: x[1], reverse=True)

        # Store raw dicts for insight logic
        self._qty_by_product     = dict(qty_by_product)
        self._revenue_by_product = dict(revenue_by_product)
        self._revenue_by_category = dict(revenue_by_category)

        # Low performers: bottom third by total quantity sold
        quantities = sorted(self._qty_by_product.values())
        low_threshold = quantities[len(quantities) // 3]  # 33rd-percentile value
        self.low_performers = [
            (p, q) for p, q in self.products_by_qty if q <= low_threshold
        ]

    # ─────────────────────────────────────────
    # SECTION 1 — Sales Overview
    # ─────────────────────────────────────────

    def sales_overview(self) -> str:
        return textwrap.dedent(f"""
        +- SALES OVERVIEW -----------------------------------------------+
          Period         : {self.date_range[0]}  ->  {self.date_range[1]}
          Total Orders   : {self.total_orders:,}
          Total Revenue  : IDR {self.total_revenue:,.0f}
          Total Units    : {self.total_units:,}
          Products       : {self.unique_products}
          Categories     : {self.unique_categories}
          Avg Order Value: IDR {self.avg_order_value:,.0f}
        +-----------------------------------------------------------------+
        """).strip()

    # ─────────────────────────────────────────
    # SECTION 2 — Top Product & Category Performance
    # ─────────────────────────────────────────

    def top_products_section(self, n: int = 5) -> str:
        lines = ["+- TOP PRODUCT & CATEGORY PERFORMANCE ---------------------------+"]

        lines.append("")
        lines.append("  Top Products by Units Sold:")
        for i, (p, q) in enumerate(self.products_by_qty[:n], 1):
            pct = q / self.total_units * 100
            lines.append(f"    {i}. {p:<22}  {q:>4} units  ({pct:.1f}% of total)")

        lines.append("")
        lines.append("  Top Products by Revenue:")
        for i, (p, r) in enumerate(self.products_by_revenue[:n], 1):
            pct = r / self.total_revenue * 100
            lines.append(f"    {i}. {p:<22}  IDR {r:>12,.0f}  ({pct:.1f}%)")

        lines.append("")
        lines.append("  Revenue by Category:")
        max_rev = self.categories_by_revenue[0][1]
        for cat, rev in self.categories_by_revenue:
            bar = "#" * int(rev / max_rev * 25)
            pct = rev / self.total_revenue * 100
            lines.append(f"    {cat:<15} IDR {rev:>12,.0f}  ({pct:.1f}%)  {bar}")

        lines.append("")
        lines.append("  Units Sold by Category:")
        for cat, qty in self.categories_by_qty:
            pct = qty / self.total_units * 100
            lines.append(f"    {cat:<15} {qty:>5} units  ({pct:.1f}%)")

        lines.append("")
        lines.append("+-----------------------------------------------------------------+")
        return "\n".join(lines)

    # ─────────────────────────────────────────
    # SECTION 3 — Low Sales Performance
    # ─────────────────────────────────────────

    def low_performers_section(self) -> str:
        lines = ["+- PRODUCTS WITH LOW SALES PERFORMANCE --------------------------+"]
        lines.append("")
        if self.low_performers:
            avg_qty = self.total_units / self.unique_products
            for p, q in self.low_performers:
                gap = avg_qty - q
                rev = self._revenue_by_product[p]
                lines.append(f"    * {p:<22}  {q:>4} units sold  |  IDR {rev:>10,.0f} revenue")
                lines.append(f"      -> {gap:.0f} units below the store average ({avg_qty:.0f} units/product)")
        else:
            lines.append("    All products are performing above the low-sales threshold.")
        lines.append("")
        lines.append("+-----------------------------------------------------------------+")
        return "\n".join(lines)

    # ─────────────────────────────────────────
    # SECTION 4 — Key Insights (rule-based)
    # ─────────────────────────────────────────

    def key_insights(self) -> str:
        lines = ["+- KEY INSIGHTS --------------------------------------------------+", ""]

        top_qty_product, top_qty_val   = self.products_by_qty[0]
        top_rev_product, top_rev_val   = self.products_by_revenue[0]
        top_cat, top_cat_rev           = self.categories_by_revenue[0]
        bottom_cat, bottom_cat_rev     = self.categories_by_revenue[-1]
        top_cat_pct  = top_cat_rev  / self.total_revenue * 100
        top_qty_pct  = top_qty_val  / self.total_units   * 100
        top_rev_pct  = top_rev_val  / self.total_revenue * 100

        n = 1
        lines.append(f"  {n}. Best-Selling Product by Volume:")
        lines.append(f"     '{top_qty_product}' leads with {top_qty_val:,} units sold")
        lines.append(f"     ({top_qty_pct:.1f}% of all units sold across the store).")
        n += 1; lines.append("")

        lines.append(f"  {n}. Top Revenue-Generating Product:")
        lines.append(f"     '{top_rev_product}' generated IDR {top_rev_val:,.0f}")
        lines.append(f"     ({top_rev_pct:.1f}% of total store revenue).")
        n += 1; lines.append("")

        # Highlight if top qty and top revenue are different products
        if top_qty_product != top_rev_product:
            lines.append(f"  {n}. Volume vs. Revenue Leaders Differ:")
            lines.append(f"     '{top_qty_product}' sells the most units, but '{top_rev_product}'")
            lines.append(f"     earns the most revenue - a higher unit price drives revenue")
            lines.append(f"     leadership despite lower volume.")
            n += 1; lines.append("")

        lines.append(f"  {n}. Dominant Category:")
        lines.append(f"     The '{top_cat}' category accounts for {top_cat_pct:.1f}% of")
        lines.append(f"     total revenue (IDR {top_cat_rev:,.0f}).")
        n += 1; lines.append("")

        lines.append(f"  {n}. Lowest-Revenue Category:")
        bottom_cat_pct = bottom_cat_rev / self.total_revenue * 100
        lines.append(f"     '{bottom_cat}' contributes only {bottom_cat_pct:.1f}% of total revenue")
        lines.append(f"     (IDR {bottom_cat_rev:,.0f}) - the smallest share among all categories.")
        n += 1; lines.append("")

        if self.low_performers:
            low_names = ", ".join(f"'{p}'" for p, _ in self.low_performers)
            lines.append(f"  {n}. Low-Performing Products:")
            lines.append(f"     {low_names} fall in the bottom third")
            lines.append(f"     of sales volume and may need attention.")
            lines.append("")

        lines.append("+-----------------------------------------------------------------+")
        return "\n".join(lines)

    # ─────────────────────────────────────────
    # SECTION 5 — Simple Recommendations (rule-based)
    # ─────────────────────────────────────────

    def recommendations(self) -> str:
        lines = ["+- SIMPLE RECOMMENDATIONS ----------------------------------------+", ""]

        top_qty_product, top_qty_val   = self.products_by_qty[0]
        top_rev_product, top_rev_val   = self.products_by_revenue[0]
        top_cat, _                     = self.categories_by_revenue[0]
        bottom_cat, _                  = self.categories_by_revenue[-1]

        n = 1
        lines.append(f"  {n}. Maintain stock levels for '{top_qty_product}'.")
        lines.append(f"     It is the highest-volume seller. Stockouts would directly")
        lines.append(f"     impact a significant share of total units sold.")
        n += 1; lines.append("")

        lines.append(f"  {n}. Prioritise '{top_rev_product}' in marketing campaigns.")
        lines.append(f"     It generates the most revenue. Featured promotions or")
        lines.append(f"     bundle deals can amplify its revenue contribution further.")
        n += 1; lines.append("")

        lines.append(f"  {n}. Invest in the '{top_cat}' category.")
        lines.append(f"     It is the dominant revenue driver. Expanding the product")
        lines.append(f"     range within this category may increase overall revenue.")
        n += 1; lines.append("")

        if self.low_performers:
            for p, q in self.low_performers:
                rev = self._revenue_by_product[p]
                lines.append(f"  {n}. Review '{p}' (only {q} units / IDR {rev:,.0f} revenue).")
                lines.append(f"     Consider a targeted promotion, a price adjustment,")
                lines.append(f"     or evaluating whether to continue stocking this item.")
                n += 1; lines.append("")

        lines.append(f"  {n}. Analyse the '{bottom_cat}' category further.")
        lines.append(f"     It contributes the least revenue. Investigate whether")
        lines.append(f"     pricing, visibility, or product variety can be improved.")
        lines.append("")

        lines.append("+-----------------------------------------------------------------+")
        return "\n".join(lines)


# ─────────────────────────────────────────────
# 3. INTERACTIVE Q&A (rule-based, no LLM)
# ─────────────────────────────────────────────

class QAAgent:
    """
    Answers basic natural-language questions about the sales data
    using keyword matching against pre-computed facts.
    No API keys or external services required.
    """

    def __init__(self, analysis: SalesAnalysis):
        self.a = analysis
        # Pre-build a flat fact map for fast lookup
        self._facts = self._build_facts()

    def _build_facts(self) -> dict:
        a = self.a
        return {
            "total_orders":   a.total_orders,
            "total_revenue":  a.total_revenue,
            "total_units":    a.total_units,
            "avg_order":      a.avg_order_value,
            "date_start":     a.date_range[0],
            "date_end":       a.date_range[1],
            "products":       [p for p, _ in a.products_by_qty],
            "top_qty":        a.products_by_qty[0],
            "top_revenue":    a.products_by_revenue[0],
            "top_category":   a.categories_by_revenue[0],
            "bottom_category": a.categories_by_revenue[-1],
            "low_performers": a.low_performers,
            "cat_revenue":    dict(a.categories_by_revenue),
            "prod_qty":       dict(a.products_by_qty),
            "prod_revenue":   dict(a.products_by_revenue),
        }

    def ask(self, question: str) -> str:
        q  = question.lower().strip()
        a  = self.a
        f  = self._facts

        # ── Revenue / total ──
        if any(w in q for w in ["total revenue", "how much revenue", "revenue total"]):
            return f"Total revenue is IDR {f['total_revenue']:,.0f} across {f['total_orders']:,} orders."

        if any(w in q for w in ["total orders", "how many orders", "number of orders"]):
            return f"There are {f['total_orders']:,} total orders in the dataset."

        if any(w in q for w in ["total units", "units sold", "how many units"]):
            return f"A total of {f['total_units']:,} units were sold."

        if any(w in q for w in ["average order", "avg order", "average value"]):
            return f"The average order value is IDR {f['avg_order']:,.0f}."

        if any(w in q for w in ["period", "date range", "when", "time period", "from when"]):
            return f"The dataset covers {f['date_start']} to {f['date_end']}."

        # ── Top / best ──
        if any(w in q for w in ["best sell", "top sell", "most sold", "highest quantity", "most popular", "best-sell", "sells the most", "sell the most", "which product"]):
            p, qty = f["top_qty"]
            return f"'{p}' is the best-selling product with {qty:,} units sold."

        if any(w in q for w in ["highest revenue", "most revenue", "top revenue", "best revenue"]):
            p, rev = f["top_revenue"]
            return f"'{p}' generates the highest revenue: IDR {rev:,.0f}."

        if any(w in q for w in ["top category", "best category", "highest category", "category revenue"]):
            cat, rev = f["top_category"]
            pct = rev / f["total_revenue"] * 100
            return (f"'{cat}' is the top revenue category with IDR {rev:,.0f} "
                    f"({pct:.1f}% of total revenue).")

        # ── Low performers ──
        if any(w in q for w in ["low", "worst", "poor", "underperform", "bottom"]):
            if f["low_performers"]:
                items = ", ".join(f"{p} ({q} units)" for p, q in f["low_performers"])
                return f"Low-performing products: {items}."
            return "No products are currently flagged as low performers."

        # ── Product-specific lookup ──
        for product in f["products"]:
            if product.lower() in q:
                qty = f["prod_qty"][product]
                rev = f["prod_revenue"][product]
                rank_q = [p for p, _ in a.products_by_qty].index(product) + 1
                rank_r = [p for p, _ in a.products_by_revenue].index(product) + 1
                return (f"'{product}': {qty:,} units sold (rank #{rank_q} by volume), "
                        f"IDR {rev:,.0f} revenue (rank #{rank_r} by revenue).")

        # ── Category-specific lookup ──
        for cat in f["cat_revenue"]:
            if cat.lower() in q:
                rev = f["cat_revenue"][cat]
                pct = rev / f["total_revenue"] * 100
                cat_qty = dict(a.categories_by_qty).get(cat, 0)
                return (f"'{cat}' category: IDR {rev:,.0f} revenue ({pct:.1f}% of total), "
                        f"{cat_qty:,} units sold.")

        # ── Products list ──
        if any(w in q for w in ["what products", "list product", "which product", "all product"]):
            return "Products tracked: " + ", ".join(f["products"]) + "."

        if any(w in q for w in ["what categor", "list categor", "which categor"]):
            return "Categories: " + ", ".join(f["cat_revenue"].keys()) + "."

        return ("I can answer questions about total revenue, orders, units sold, "
                "best-selling products, top categories, and low performers. "
                "Try asking about a specific product or category by name.")
