import streamlit as st
import pandas as pd
import plotly.express as px

# Título del dashboard
st.title("Dashboard de Modelos DFM")

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("models.csv", parse_dates=["Time"])

df = cargar_datos()

# Sidebar de filtros

st.sidebar.header("Filtros de Modelo")

# Valores únicos
p_opciones = sorted(df["p"].unique())
q_opciones = sorted(df["q"].unique())
svf_opciones = sorted(df["SVF"].unique())
svi_opciones = sorted(df["SVI"].unique())
variables_opciones = sorted(df["variable"].unique())

# Definir valores por defecto "inteligentes"
p_vals = st.sidebar.multiselect("Parámetro p", p_opciones, default=p_opciones)
q_vals = st.sidebar.multiselect("Parámetro q", q_opciones, default=q_opciones)
svf_vals = st.sidebar.multiselect("SVF", svf_opciones, default=[0, 1] if set([0, 1]).issubset(svf_opciones) else svf_opciones)
svi_vals = st.sidebar.multiselect("SVI", svi_opciones, default=[0, 1] if set([0, 1]).issubset(svi_opciones) else svi_opciones)
variables = st.sidebar.multiselect("Variable", variables_opciones, default=["PIB_Semanal"])

# Aplicar filtros SOLO si el usuario cambia la selección
df_filtrado = df.copy()
if p_vals and set(p_vals) != set(p_opciones):
    df_filtrado = df_filtrado[df_filtrado["p"].isin(p_vals)]
if q_vals and set(q_vals) != set(q_opciones):
    df_filtrado = df_filtrado[df_filtrado["q"].isin(q_vals)]
if svf_vals and set(svf_vals) != set(svf_opciones):
    df_filtrado = df_filtrado[df_filtrado["SVF"].isin(svf_vals)]
if svi_vals and set(svi_vals) != set(svi_opciones):
    df_filtrado = df_filtrado[df_filtrado["SVI"].isin(svi_vals)]
if variables:
    df_filtrado = df_filtrado[df_filtrado["variable"].isin(variables)]

# Obtener modelos disponibles
modelos_disponibles = sorted(df_filtrado["modelo_id"].unique())

# Selector de modelos con todos los que cumplen los criterios seleccionados
modelos_seleccionados = st.sidebar.multiselect(
    "Seleccionar modelos específicos (máx 10 para vista desagregada)",
    opciones := modelos_disponibles,
    default=opciones[:10]
)


# === GRÁFICO AGRUPADO ===
st.subheader("Gráfico Agrupado por Modelo")

fig = px.line(
    df_filtrado[df_filtrado["modelo_id"].isin(modelos_seleccionados)],
    x="Time", y="value", color="modelo_id", line_dash="variable",
    title="Evolución de variables por modelo seleccionado"
)
st.plotly_chart(fig, use_container_width=True)

# === BOTÓN PARA MOSTRAR DESAGREGADO ===
st.subheader("Gráfico Agrupado por Modelo")

if modelos_seleccionados:
    fig = px.line(
        df_filtrado[df_filtrado["modelo_id"].isin(modelos_seleccionados)],
        x="Time", y="value", color="modelo_id", line_dash="variable",
        title="Evolución de variables por modelo seleccionado"
    )
    st.plotly_chart(fig, use_container_width=True)
    
       # === BOTÓN PARA MOSTRAR DESAGREGADO ===
    if st.checkbox("Mostrar gráficos desagregados por modelo"):
        st.subheader("Gráficos individuales")
        for modelo in modelos_seleccionados:
            st.markdown(f"**Modelo: {modelo}**")
            for var in variables:
                df_tmp = df_filtrado[(df_filtrado["modelo_id"] == modelo) & (df_filtrado["variable"] == var)]
                fig_tmp = px.line(df_tmp, x="Time", y="value", title=f"{var} – {modelo}")
                st.plotly_chart(fig_tmp, use_container_width=True)

    # === MOSTRAR DATOS RAW (opcional) ===
    if st.checkbox("Mostrar tabla de datos"):
        st.dataframe(df_filtrado)
        
            
    
