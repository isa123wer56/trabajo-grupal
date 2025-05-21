import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos con caché
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data.csv")
    df["Fecha"] = pd.to_datetime(df["Date"])
    df["Hora"] = pd.to_datetime(df["Time"], format="%H:%M").dt.hour
    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.month
    df["Día"] = df["Fecha"].dt.day
    df["Día_Semana"] = df["Fecha"].dt.day_name()
    df["Día_Semana"] = pd.Categorical(df["Día_Semana"],
        categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], ordered=True)
    return df

df = cargar_datos()

if df.empty:
    st.error("⚠ No se encontraron datos en 'data.csv'. Verifica el archivo.")
    st.stop()

# 🧭 Barra lateral de filtros
st.sidebar.header("📌 Filtros del Dashboard")
anio = st.sidebar.selectbox("Selecciona el año:", sorted(df["Año"].unique()), key="select_anio")

meses_nombres = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

mes = st.sidebar.selectbox(
    "Selecciona el mes:",
    sorted(df[df["Año"] == anio]["Mes"].unique()),
    format_func=lambda x: meses_nombres[x],
    key="select_mes"
)

# Filtros adicionales
categorias = st.sidebar.multiselect("Filtrar por categoría de producto:", options=df["Product line"].unique(), default=df["Product line"].unique())
clientes = st.sidebar.multiselect("Filtrar por tipo de cliente:", options=df["Customer type"].unique(), default=df["Customer type"].unique())
pagos = st.sidebar.multiselect("Filtrar por método de pago:", options=df["Payment"].unique(), default=df["Payment"].unique())

# Filtrar datos
df_filtrado = df[(df["Año"] == anio) & 
                 (df["Mes"] == mes) &
                 (df["Product line"].isin(categorias)) &
                 (df["Customer type"].isin(clientes)) &
                 (df["Payment"].isin(pagos))]

# 🏆 Título
st.title(f"📊 Dashboard de Ventas - {meses_nombres[mes]} {anio}")

# 📈 Métricas
col1, col2, col3 = st.columns(3)
col1.metric("💰 Ingreso Bruto Total", f"${df_filtrado['gross income'].sum():,.2f}")
col2.metric("🛒 Transacciones", f"{df_filtrado.shape[0]}")
col3.metric("🔻 Ingreso Promedio", f"${df_filtrado['gross income'].mean():,.2f}")

# 🔹 Gráfico de Ingresos por Categoría
st.subheader("🔹 Ingresos por Categoría de Producto")
tipo_grafico = st.selectbox("Elige tipo de gráfico:", ["Barra", "Boxplot"])
if tipo_grafico == "Barra":
    fig = px.bar(df_filtrado, x="Product line", y="gross income", color="Product line", title="Ingresos por Categoría")
else:
    fig = px.box(df_filtrado, x="Product line", y="gross income", color="Product line", title="Distribución de Ingresos")
st.plotly_chart(fig)

# 💳 Gráfico de Método de Pago
st.subheader("💳 Métodos de Pago")
fig_pago = px.pie(df_filtrado, names="Payment", values="Total", title="Método de Pago")
st.plotly_chart(fig_pago)

# 👥 Tipo de Cliente
st.subheader("👥 Tipo de Cliente")
fig_clientes = px.pie(df_filtrado, names="Customer type", values="Total", title="Tipo de Cliente")
st.plotly_chart(fig_clientes)

# 📅 Ingresos por Día de la Semana
st.subheader("📅 Ingresos por Día de la Semana")
fig_dias = px.bar(df_filtrado, x="Día_Semana", y="gross income", color="Día_Semana", title="Ingresos por Día")
st.plotly_chart(fig_dias)

# 📆 Serie temporal diaria
st.subheader("📆 Ingresos diarios")
ingresos_dia = df_filtrado.groupby("Día")["gross income"].sum().reset_index()
fig_dia = px.line(ingresos_dia, x="Día", y="gross income", markers=True, title="Ingreso Diario")
st.plotly_chart(fig_dia)

# 🔥 Mapa de calor: Día vs Hora
st.subheader("⏰ Mapa de Calor de Ventas por Día y Hora")
heatmap_data = df_filtrado.groupby(["Día_Semana", "Hora"])["gross income"].sum().reset_index()
fig_heatmap = px.density_heatmap(heatmap_data, x="Hora", y="Día_Semana", z="gross income", 
                                 color_continuous_scale="Viridis", title="Ingresos por Día y Hora")
st.plotly_chart(fig_heatmap)

# 🌀 Dispersión de Total vs Ingreso Bruto
st.subheader("📌 Relación entre Total e Ingreso Bruto")
fig_scatter = px.scatter(df_filtrado, x="Total", y="gross income", color="Product line", size="Quantity",
                         title="Dispersión Total vs Ingreso Bruto", labels={"Total": "Total Compra", "gross income": "Ingreso Bruto"})
st.plotly_chart(fig_scatter)

# 💾 Exportación
st.download_button(
    label="📥 Descargar datos filtrados",
    data=df_filtrado.to_csv(index=False),
    file_name=f"ventas_{anio}_{mes}.csv",
    mime="text/csv"
)

# 🔍 Conclusión
st.markdown("""
---
✅ **Nuevas interacciones:** Ahora puedes filtrar por categoría, cliente y forma de pago.  
✅ **Más gráficos:** Incluye mapas de calor, series temporales, boxplots y scatter plots.  
✅ **Explora patrones ocultos:** Detecta horas pico, productos variables, y relaciones entre variables.  
""")

