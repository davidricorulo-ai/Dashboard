"""
Dashboard Tienda Electrónica
----------------------------
App de Streamlit que lee `ventas_limpias.csv` y muestra:
  - Tab 1 · Resumen Financiero: ingresos por categoría (barras) y su distribución (%).
  - Tab 2 · Tendencia: pedidos por día con promedio móvil de 7 días y KPIs.
  - Tab 3 · Productos: top 10 productos por ventas.

Ejecutar con:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import seaborn as sns


# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =============================================================================
# set_page_config debe ser la primera llamada de Streamlit en el script.
st.set_page_config(
    page_title="Dashboard Tienda Electrónica",
    page_icon=":bar_chart:",
    layout="wide",
)
st.title("Dashboard Tienda Electrónica")
st.markdown("Visualizaciones organizadas por sección")

# Tema global de seaborn (afecta a todas las gráficas)
sns.set_theme(style="whitegrid")

# Paleta de colores usada en todo el dashboard
COLOR_PRINCIPAL = "#2E5AAC"
COLOR_SECUNDARIO = "#E07A1F"
COLOR_TEXTO = "#555555"


# =============================================================================
# 2. FUNCIONES AUXILIARES
# =============================================================================
@st.cache_data
def cargar_datos(ruta: str) -> pd.DataFrame:
    """Lee el CSV, convierte 'Fecha' a datetime y agrega la semana ISO.

    Se cachea para que el CSV no se vuelva a leer en cada interacción.
    """
    datos = pd.read_csv(ruta)
    datos["Fecha"] = pd.to_datetime(datos["Fecha"])
    datos["Semana"] = datos["Fecha"].dt.isocalendar().week
    return datos


def estilo_limpio(ax: plt.Axes) -> None:
    """Aplica un estilo minimalista: sin bordes superior/derecho y grid suave en Y."""
    for lado in ["top", "right"]:
        ax.spines[lado].set_visible(False)
    for lado in ["left", "bottom"]:
        ax.spines[lado].set_color("#CCCCCC")
    ax.grid(axis="y", color="#EEEEEE", linewidth=0.8)
    ax.grid(axis="x", visible=False)
    ax.tick_params(colors=COLOR_TEXTO, labelsize=9)


# =============================================================================
# 3. CARGA DE DATOS
# =============================================================================
df = cargar_datos("ventas_limpias.csv")

with st.expander("Ver base de datos"):
    st.dataframe(df, use_container_width=True)


# =============================================================================
# 4. PESTAÑAS
# =============================================================================
tab1, tab2, tab3 = st.tabs(["Resumen Financiero", "Tendencia", "Productos"])


# -----------------------------------------------------------------------------
# TAB 1 · RESUMEN FINANCIERO
# -----------------------------------------------------------------------------
with tab1:
    # Ingresos totales por categoría, de mayor a menor
    ingresos_cat = (
        df.groupby("Categoria")["Subtotal"].sum()
          .reset_index()
          .sort_values(by="Subtotal", ascending=False)
    )

    # Dos columnas: barras a la izquierda, dona a la derecha.
    # Así la dona no se estira a todo el ancho de la página (layout="wide").
    col_barras, col_dona = st.columns(2, gap="large")

    # --- Gráfica de barras: ingresos por categoría ---
    with col_barras:
        st.subheader("Ingresos por categoría")
        fig_barras, ax_barras = plt.subplots(figsize=(6, 4.5))
        # hue + legend=False evita el warning de 'palette' sin 'hue'
        sns.barplot(
            data=ingresos_cat, x="Categoria", y="Subtotal",
            hue="Categoria", palette="viridis", legend=False, ax=ax_barras,
        )
        ax_barras.set_xlabel("")
        ax_barras.set_ylabel("Ingresos", color=COLOR_TEXTO)
        ax_barras.yaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
        ax_barras.tick_params(axis="x", rotation=30)
        estilo_limpio(ax_barras)
        fig_barras.tight_layout()
        st.pyplot(fig_barras, use_container_width=True)
        plt.close(fig_barras)  # libera memoria en cada rerun

    # --- Gráfica de dona: distribución de ingresos (%) ---
    with col_dona:
        st.subheader("Distribución de ingresos (%)")

        total_ingresos = ingresos_cat["Subtotal"].sum()
        pct = ingresos_cat["Subtotal"] / total_ingresos * 100
        colores = sns.color_palette("pastel", len(ingresos_cat))

        fig_dona, ax_dona = plt.subplots(figsize=(6, 5))
        secciones, _, porcentajes = ax_dona.pie(
            ingresos_cat["Subtotal"],
            labels=None,                      # los nombres van en la leyenda
            # Solo mostramos el % en rebanadas >= 3% para que no se encimen
            autopct=lambda p: f"{p:.1f}%" if p >= 3 else "",
            pctdistance=0.78,
            startangle=90,
            counterclock=False,               # de mayor a menor en sentido horario
            colors=colores,
            wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 8, "color": "#333333"},
        )

        # Total al centro de la dona
        ax_dona.text(0, 0, f"${total_ingresos:,.0f}\nTotal",
                     ha="center", va="center", fontsize=9,
                     fontweight="bold", color="#333333")

        # Leyenda debajo, en 2 columnas, con nombre y % (incluye las rebanadas chicas).
        # Debajo y no a la derecha para que no se corte el texto.
        etiquetas = [f"{c}  ({p:.1f}%)"
                     for c, p in zip(ingresos_cat["Categoria"], pct)]
        ax_dona.legend(secciones, etiquetas, loc="upper center",
                       bbox_to_anchor=(0.5, 0), ncol=2,
                       frameon=False, fontsize=8)

        ax_dona.set_aspect("equal")
        fig_dona.tight_layout()
        st.pyplot(fig_dona, use_container_width=True)
        plt.close(fig_dona)


# -----------------------------------------------------------------------------
# TAB 2 · TENDENCIA DE PEDIDOS
# -----------------------------------------------------------------------------
with tab2:
    # Pedidos por día. asfreq('D') agrega los días sin pedidos con valor 0
    # para que la línea no "salte" fechas.
    pedidos_dia = (
        df.groupby("Fecha")["ID_Pedido"].count()
          .asfreq("D", fill_value=0)
          .rename("Pedidos")
          .to_frame()
    )
    # Promedio móvil de 7 días para suavizar la tendencia
    pedidos_dia["Prom_7d"] = pedidos_dia["Pedidos"].rolling(7, min_periods=1).mean()

    fecha_max = pedidos_dia["Pedidos"].idxmax()
    valor_max = pedidos_dia["Pedidos"].max()

    st.subheader("Tendencia de pedidos por día")

    # --- KPIs ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total pedidos", int(pedidos_dia["Pedidos"].sum()))
    c2.metric("Promedio diario", f"{pedidos_dia['Pedidos'].mean():.1f}")
    c3.metric("Día pico", fecha_max.strftime("%d %b"))

    # --- Gráfica de línea ---
    fig_tend, ax_tend = plt.subplots(figsize=(10, 4), dpi=150)

    ax_tend.plot(
        pedidos_dia.index, pedidos_dia["Pedidos"],
        color=COLOR_PRINCIPAL, linewidth=1.8, marker="o", markersize=3,
        label="Pedidos diarios",
    )
    ax_tend.fill_between(
        pedidos_dia.index, pedidos_dia["Pedidos"],
        color=COLOR_PRINCIPAL, alpha=0.08,
    )
    ax_tend.plot(
        pedidos_dia.index, pedidos_dia["Prom_7d"],
        color=COLOR_SECUNDARIO, linewidth=2, linestyle="--",
        label="Promedio móvil 7 días",
    )

    # Etiqueta en el día con más pedidos
    ax_tend.annotate(
        f"Pico: {valor_max}", xy=(fecha_max, valor_max),
        xytext=(10, 8), textcoords="offset points",
        fontsize=9, color="#333333", fontweight="bold",
    )

    # Ejes: Y en enteros desde 0, X con una etiqueta por semana (lunes)
    ax_tend.set_ylim(bottom=0, top=valor_max * 1.2)
    ax_tend.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax_tend.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax_tend.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    ax_tend.set_xlabel("")
    ax_tend.set_ylabel("Número de pedidos", fontsize=10, color=COLOR_TEXTO)

    estilo_limpio(ax_tend)
    ax_tend.legend(frameon=False, fontsize=9, loc="upper right")

    fig_tend.tight_layout()
    st.pyplot(fig_tend, use_container_width=True)
    plt.close(fig_tend)

    st.divider()


# -----------------------------------------------------------------------------
# TAB 3 · PRODUCTOS
# -----------------------------------------------------------------------------
with tab3:
    # Ventas totales por producto -> Top 10 de mayor a menor
    top_productos = (
        df.groupby("Producto")["Subtotal"].sum()
          .reset_index()
          .sort_values(by="Subtotal", ascending=False)
          .head(10)
    )

    st.subheader("Top 10 productos por ventas")

    # En Colab, plt dibuja solo; en Streamlit hay que crear la figura
    # explícitamente (fig, ax) y pasarla a st.pyplot()
    fig_prod, ax_prod = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=top_productos, x="Subtotal", y="Producto",
        color=COLOR_PRINCIPAL, ax=ax_prod,
    )

    # Etiqueta con el monto al final de cada barra
    ax_prod.bar_label(ax_prod.containers[0], fmt="${:,.0f}",
                      padding=4, fontsize=8, color=COLOR_TEXTO)

    ax_prod.set_xlabel("Ventas", color=COLOR_TEXTO)
    ax_prod.set_ylabel("")
    ax_prod.xaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
    estilo_limpio(ax_prod)
    # En barras horizontales la cuadrícula útil es la vertical
    ax_prod.grid(axis="y", visible=False)
    ax_prod.grid(axis="x", color="#EEEEEE", linewidth=0.8)

    fig_prod.tight_layout()
    st.pyplot(fig_prod, use_container_width=True)
    plt.close(fig_prod)

    st.divider()
