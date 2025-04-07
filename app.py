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

df_check = df[df["modelo_id"] == "p4_q3_SVF1_SVI0"]
df_check = df_check[df['variable'] == "PIB_Semanal"]
duplicados = df_check[df_check.duplicated(subset=["Time", "variable"], keep=False)]
st.write("Duplicados exactos por fecha y variable:", duplicados)



# Sidebar de filtros
st.sidebar.header("Filtros de Modelo")

# Filtros dinámicos
p_vals = st.sidebar.multiselect("Parámetro p", sorted(df["p"].unique()), default=sorted(df["p"].unique()))
q_vals = st.sidebar.multiselect("Parámetro q", sorted(df["q"].unique()), default=sorted(df["q"].unique()))
svf_vals = st.sidebar.multiselect("SVF", sorted(df["SVF"].unique()), default=sorted(df["SVF"].unique()))
svi_vals = st.sidebar.multiselect("SVI", sorted(df["SVI"].unique()), default=sorted(df["SVI"].unique()))
variables = st.sidebar.multiselect("Variable", sorted(df["variable"].unique()), default=["PIB_Semanal"])

# Filtrar el DataFrame
df_filtrado = df[
    (df["p"].isin(p_vals)) &
    (df["q"].isin(q_vals)) &
    (df["SVF"].isin(svf_vals)) &
    (df["SVI"].isin(svi_vals)) &
    (df["variable"].isin(variables))
]

# Selector de modelos (máximo 10 para gráficas individuales)
modelos_seleccionados = st.sidebar.multiselect("Seleccionar modelos específicos (máx 10)", 
                                               sorted(df_filtrado["modelo_id"].unique()), 
                                               default=sorted(df_filtrado["modelo_id"].unique())[:3])

# === GRÁFICO AGRUPADO ===
st.subheader("Gráfico Agrupado por Modelo")

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
    
    
