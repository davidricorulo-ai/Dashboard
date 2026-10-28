# Electronics Store Sales Dashboard

Interactive sales dashboard built with **Python + Streamlit** to analyze revenue, order trends and top products for an electronics store.

## Preview

**Financial Summary** — revenue by category and revenue share
![Financial Summary tab](docs/tab1-resumen.png)

**Trend** — daily orders, 7-day moving average and KPIs
![Trend tab](docs/tab2-tendencia.png)

**Products** — top products by sales
![Products tab](docs/tab3-productos.png)

## What it shows

| Tab | Visualization | Business question |
|---|---|---|
| **Financial Summary** | Revenue by category (bar) + revenue share (donut) | Which categories drive the business? |
| **Trend** | Daily orders with 7-day moving average, peak-day annotation and KPI cards | How is order volume evolving? |
| **Products** | Top 3 products by sales (horizontal bar) + price vs. quantity scatter by category | Which products should we prioritize, and how does price relate to volume? |

## Highlights

- **Clean data pipeline:** dates parsed once, cached loading with `@st.cache_data`.
- **Accurate time series:** days with zero orders are filled (`asfreq('D')`) so the trend line doesn't skip dates.
- **Consistent design:** shared color palette and a reusable `estilo_limpio()` helper for minimalist axes.
- **Readable charts:** integer axes for counts, currency formatting, value labels and legends instead of overlapping text.

## Tech stack

Python · pandas · matplotlib · seaborn · Streamlit

## Run it locally

```bash
git clone https://github.com/davidricorulo-ai/Dashboard.git
cd Dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Data

`docs/ventas_limpias.csv` contains the clean sales dataset (one row per order line) with the columns:
`ID_Pedido`, `Fecha`, `Producto`, `Categoria`, `Precio`, `Cantidad`, `Subtotal`.

The raw data was cleaned beforehand in Google Colab (pandas).

## Project structure

```
├── app.py                     # Streamlit app
├── requirements.txt
└── docs/
    ├── ventas_limpias.csv     # Cleaned dataset
    ├── tab1-resumen.png       # Screenshots used in this README
    ├── tab2-tendencia.png
    └── tab3-productos.png
```

---

**Author:** David Rico · Business Analyst — Finance Operations & Automation

