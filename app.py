import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página en modo "wide"
st.set_page_config(layout="wide")

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("models.csv", parse_dates=["Time"])

df = cargar_datos()

# --- SIDEBAR DE FILTROS ---
st.sidebar.header("Filtros de Modelo")

# 1) Parámetro p
p_unicos = sorted(df["p"].unique())
p_vals = st.sidebar.multiselect(
    "Parámetro p", 
    options=p_unicos, 
    default=p_unicos  # por defecto, todos
)
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

# 5) Variables
var_unicas = sorted(df["variable"].unique())
variables = st.sidebar.multiselect(
    "Variable",
    options=var_unicas,
    default=["PIB_Semanal"]  # un default de ejemplo
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

modelos_disponibles = sorted(df_filtrado["modelo_id"].unique())
modelos_seleccionados = st.sidebar.multiselect(
    "Seleccionar modelos específicos (máx 10)", 
    options=modelos_disponibles, 
    default=modelos_disponibles[:3]  # primeros 3 como ejemplo
)
if not modelos_seleccionados:
    modelos_seleccionados = modelos_disponibles[:3]


# --- CONTENIDO PRINCIPAL ---

st.title("Dashboard de Modelos DFM")

# === GRÁFICO 1: SOLO FACTOR ===
st.subheader("Gráfico 1: Variable Factor")
df_factor = df_filtrado[
    (df_filtrado["variable"] == "Factor") & 
    (df_filtrado["modelo_id"].isin(modelos_seleccionados))
]
if not df_factor.empty:
    fig_factor = px.line(
        df_factor, 
        x="Time", 
        y="value", 
        color="modelo_id",
        title="Evolución de la Variable Factor"
    )
    st.plotly_chart(fig_factor, use_container_width=True)
else:
    st.info("No hay datos para la variable Factor con los filtros seleccionados.")


# === GRÁFICO 2: PIB_SEMANAL, FACTOR Y PIB ===
st.subheader("Gráfico 2: PIB_Semanal, Factor y PIB")
df_pib = df_filtrado[
    (df_filtrado["variable"].isin(["PIB_Semanal", "Factor", "PIB"])) &
    (df_filtrado["modelo_id"].isin(modelos_seleccionados))
]
if not df_pib.empty:
    fig_pib = px.line(
        df_pib,
        x="Time",
        y="value",
        color="modelo_id",
        line_dash="variable",
        title="Evolución de PIB_Semanal, Factor y PIB"
    )
    st.plotly_chart(fig_pib, use_container_width=True)
else:
    st.info("No hay datos para [PIB_Semanal, Factor, PIB] con los filtros seleccionados.")


# === GRÁFICO 3: VOLFACTOR_MEAN (SOLO CUANDO SVF=1) ===
st.subheader("Gráfico 3: VolFactor_Mean (solo para SVF=1)")
if 1 in svf_vals:
    df_vol = df_filtrado[
        (df_filtrado["variable"] == "VolFactor_Mean") &
        (df_filtrado["SVF"] == 1) &
        (df_filtrado["modelo_id"].isin(modelos_seleccionados))
    ]
    if not df_vol.empty:
        fig_vol = px.line(
            df_vol,
            x="Time",
            y="value",
            color="modelo_id",
            title="Evolución de VolFactor_Mean (SVF=1)"
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.info("No hay datos para VolFactor_Mean con SVF=1 en los filtros seleccionados.")
else:
    st.info("El gráfico de VolFactor_Mean no se muestra ya que no se eligió SVF=1.")


# === GRÁFICOS DESAGREGADOS (opcional, según el botón) ===
if st.checkbox("Mostrar gráficos desagregados por modelo"):
    st.subheader("Gráficos individuales por modelo y variable")
    for modelo in modelos_seleccionados:
        st.markdown(f"**Modelo: {modelo}**")
        df_mod = df_filtrado[df_filtrado["modelo_id"] == modelo]
        for var in df_mod["variable"].unique():
            df_tmp = df_mod[df_mod["variable"] == var]
            fig_tmp = px.line(
                df_tmp, 
                x="Time", 
                y="value", 
                title=f"{var} – {modelo}"
            )
            st.plotly_chart(fig_tmp, use_container_width=True)

# === TABLA DE DATOS FILTRADOS (opcional) ===
if st.checkbox("Mostrar tabla de datos"):
    st.dataframe(df_filtrado)
