import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página en modo "wide"
st.set_page_config(layout="wide")

@st.cache_data
def cargar_datos():
    return pd.read_csv("models.csv", parse_dates=["Time"])

df = cargar_datos()

# --- SIDEBAR DE FILTROS ---
st.sidebar.header("Filtros de Modelo")

# 1) Parámetro p
p_unicos = sorted(df["p"].unique())
p_vals = st.sidebar.multiselect("Parámetro p", p_unicos, default=p_unicos)
if not p_vals:
    p_vals = p_unicos

# 2) Parámetro q
q_unicos = sorted(df["q"].unique())
q_vals = st.sidebar.multiselect("Parámetro q", q_unicos, default=q_unicos)
if not q_vals:
    q_vals = q_unicos

# 3) SVF
svf_unicos = sorted(df["SVF"].unique())
svf_vals = st.sidebar.multiselect("SVF", svf_unicos, default=svf_unicos)
if not svf_vals:
    svf_vals = svf_unicos

# 4) SVI
svi_unicos = sorted(df["SVI"].unique())
svi_vals = st.sidebar.multiselect("SVI", svi_unicos, default=svi_unicos)
if not svi_vals:
    svi_vals = svi_unicos

# Filtro principal
df_filtrado = df[
    (df["p"].isin(p_vals)) &
    (df["q"].isin(q_vals)) &
    (df["SVF"].isin(svf_vals)) &
    (df["SVI"].isin(svi_vals))
]

# Selección de modelos
modelos_disponibles = sorted(df_filtrado["modelo_id"].unique())
modelos_seleccionados = st.sidebar.multiselect(
    "Seleccionar modelos específicos (máx 10)",
    modelos_disponibles, 
    default=modelos_disponibles[:3]  # ejemplo: primeros 3
)
if not modelos_seleccionados:
    modelos_seleccionados = modelos_disponibles[:3]

# Selector en el sidebar para elegir si se graficará PIB Semanal o Consumo Semanal
st.sidebar.subheader("Segundo gráfico:")
opcion_2 = st.sidebar.radio(
    "Comparar:",
    ("PIB Semanal", "Consumo Semanal")
)

# --- CONTENIDO PRINCIPAL ---
st.title("Dashboard de Modelos DFM")

# === GRÁFICO 1: SOLO FACTOR ===
st.subheader("Gráfico 1: Variable Factor (por modelo)")
df_factor = df_filtrado[
    (df_filtrado["variable"] == "Factor") & 
    (df_filtrado["modelo_id"].isin(modelos_seleccionados))
]

if not df_factor.empty:
    fig_factor = px.line(
        df_factor,
        x="Time", y="value",
        color="modelo_id",
        title="Evolución de la Variable Factor"
    )
    st.plotly_chart(fig_factor, use_container_width=True)
else:
    st.info("No hay datos de Factor con los filtros y modelos seleccionados.")

# === GRÁFICO 2: PIB/Consumo SEMANAL (Modelado) vs Observado ===
if opcion_2 == "PIB Semanal":
    var_modeled = "PIB_Semanal"        # Modelado por cada modelo
    var_observed = "PIB"              # Observado (mismo para todos)
    titulo_2 = "PIB"
else:
    var_modeled = "Consumo_Semanal"   # Modelado por cada modelo
    var_observed = "consumo_hogares"  # Observado
    titulo_2 = "Consumo"

st.subheader(f"Gráfico 2: {var_modeled} (modelado) vs {var_observed} (observado)")

df_mod_modeled = df_filtrado[
    (df_filtrado["variable"] == var_modeled) & 
    (df_filtrado["modelo_id"].isin(modelos_seleccionados))
]

# Serie observada (quitamos duplicados para no multiplicarla por modelo)
df_mod_observed = df_filtrado[
    df_filtrado["variable"] == var_observed
].drop_duplicates(subset=["Time"], keep="first")

# Opcional: eliminar filas con NaN en 'value' para la serie observada
df_mod_observed = df_mod_observed.dropna(subset=["value"])

fig2 = go.Figure()

# Trazas para cada modelo (líneas)
for modelo in modelos_seleccionados:
    df_tmp = df_mod_modeled[df_mod_modeled["modelo_id"] == modelo]
    df_tmp = df_tmp.dropna(subset=["value"])  # por si hay NaN en los valores modelados
    if not df_tmp.empty:
        fig2.add_trace(go.Scatter(
            x=df_tmp["Time"],
            y=df_tmp["value"],
            mode='lines',
            name=f"{var_modeled} - {modelo}"
        ))

# Trazas para la serie observada (sólo marcadores, sin líneas)
if not df_mod_observed.empty:
    fig2.add_trace(go.Scatter(
        x=df_mod_observed["Time"],
        y=df_mod_observed["value"],
        mode='markers',        # sólo puntos
        connectgaps=False,     # no une los huecos
        marker_symbol='x',
        marker_color='black',
        name=f"{var_observed} (Observado)"
    ))

fig2.update_layout(title=f"Evolución de {titulo_2} modelado vs observado")
st.plotly_chart(fig2, use_container_width=True)

# === GRÁFICO 3: VolFactor_Mean (sólo si SVF=1) ===
st.subheader("Gráfico 3: VolFactor_Mean (sólo para SVF=1)")

if 1 in svf_vals:
    df_vol = df_filtrado[
        (df_filtrado["variable"] == "VolFactor_Mean") &
        (df_filtrado["SVF"] == 1) &
        (df_filtrado["modelo_id"].isin(modelos_seleccionados))
    ]
    if not df_vol.empty:
        fig_vol = px.line(
            df_vol,
            x="Time", y="value",
            color="modelo_id",
            title="Evolución de VolFactor_Mean (SVF=1)"
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.info("No hay registros de VolFactor_Mean con SVF=1 y esos filtros.")
else:
    st.info("No se muestra VolFactor_Mean porque no se eligió SVF=1 en el filtro.")

# === GRÁFICOS DESAGREGADOS (opcional) ===
if st.checkbox("Mostrar gráficos desagregados por modelo"):
    st.subheader("Gráficos individuales por modelo y variable (filtros actuales)")
    for modelo in modelos_seleccionados:
        st.markdown(f"**Modelo: {modelo}**")
        df_mod = df_filtrado[df_filtrado["modelo_id"] == modelo]
        for var in sorted(df_mod["variable"].unique()):
            df_tmp = df_mod[df_mod["variable"] == var]
            fig_tmp = px.line(
                df_tmp, x="Time", y="value",
                title=f"{var} – {modelo}"
            )
            st.plotly_chart(fig_tmp, use_container_width=True)

# === TABLA DE DATOS (opcional) ===
if st.checkbox("Mostrar tabla de datos filtrados"):
    st.dataframe(df_filtrado)
