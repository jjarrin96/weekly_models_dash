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

# --- Sidebar de filtros ---
st.sidebar.header("Filtros de Modelo")

# 1) Parámetro p
p_unicos = sorted(df["p"].unique())
p_vals = st.sidebar.multiselect(
    "Parámetro p", 
    options=p_unicos, 
    default=p_unicos  # si queremos que inicie marcado todo
)
# Si el usuario desmarca todo, forzamos a que la lista sea completa
if not p_vals:
    p_vals = p_unicos

# 2) Parámetro q
q_unicos = sorted(df["q"].unique())
q_vals = st.sidebar.multiselect(
    "Parámetro q", 
    options=q_unicos, 
    default=q_unicos
)
if not q_vals:
    q_vals = q_unicos

# 3) SVF
svf_unicos = sorted(df["SVF"].unique())
svf_vals = st.sidebar.multiselect(
    "SVF", 
    options=svf_unicos, 
    default=svf_unicos
)
if not svf_vals:
    svf_vals = svf_unicos

# 4) SVI
svi_unicos = sorted(df["SVI"].unique())
svi_vals = st.sidebar.multiselect(
    "SVI", 
    options=svi_unicos, 
    default=svi_unicos
)
if not svi_vals:
    svi_vals = svi_unicos

# 5) Variable
var_unicas = sorted(df["variable"].unique())
variables = st.sidebar.multiselect(
    "Variable", 
    options=var_unicas,
    default=["PIB_Semanal"]  # ejemplo de un default particular
)
if not variables:
    variables = var_unicas

# Filtrar el DataFrame
df_filtrado = df[
    (df["p"].isin(p_vals)) &
    (df["q"].isin(q_vals)) &
    (df["SVF"].isin(svf_vals)) &
    (df["SVI"].isin(svi_vals)) &
    (df["variable"].isin(variables))
]

# Modelos disponibles tras esos filtros
modelos_disponibles = sorted(df_filtrado["modelo_id"].unique())

# Selector de modelos (máximo 10 para gráficas individuales)
modelos_seleccionados = st.sidebar.multiselect(
    "Seleccionar modelos específicos (máx 10)", 
    options=modelos_disponibles,
    default=modelos_disponibles[:3]  # por ejemplo, los primeros 3
)
# Si el usuario desmarca todo, también podemos forzar algún valor por default
if not modelos_seleccionados:
    modelos_seleccionados = modelos_disponibles[:3]

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
            df_tmp = df_filtrado[
                (df_filtrado["modelo_id"] == modelo) &
                (df_filtrado["variable"] == var)
            ]
            fig_tmp = px.line(
                df_tmp, x="Time", y="value", 
                title=f"{var} – {modelo}"
            )
            st.plotly_chart(fig_tmp, use_container_width=True)

# === MOSTRAR DATOS RAW (opcional) ===
if st.checkbox("Mostrar tabla de datos"):
    st.dataframe(df_filtrado)

    