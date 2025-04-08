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

# === FUNCIÓN DE MULTISELECT CON 'SELECCIONAR TODO' ===
def multiselect_con_todo(label, opciones, seleccionadas_por_defecto=None):
    seleccionar_todo = "Seleccionar todo"
    opciones_modificadas = [seleccionar_todo] + opciones
    default = [seleccionar_todo] + (seleccionadas_por_defecto or opciones)

    seleccion = st.sidebar.multiselect(label, opciones_modificadas, default=default)

    if seleccionar_todo in seleccion:
        return opciones, True
    else:
        return seleccion, set(seleccion) == set(opciones)

# === Sidebar de filtros ===
st.sidebar.header("Filtros de Modelo")

# Valores únicos
p_opciones = sorted(df["p"].unique())
q_opciones = sorted(df["q"].unique())
svf_opciones = sorted(df["SVF"].unique())
svi_opciones = sorted(df["SVI"].unique())
variables_opciones = sorted(df["variable"].unique())

# Aplicar filtros con opción "Seleccionar todo" y check para saber si hay que filtrar
p_vals, p_all = multiselect_con_todo("Parámetro p", p_opciones)
q_vals, q_all = multiselect_con_todo("Parámetro q", q_opciones)
svf_vals, svf_all = multiselect_con_todo("SVF", svf_opciones)
svi_vals, svi_all = multiselect_con_todo("SVI", svi_opciones)
variables, _ = multiselect_con_todo("Variable", variables_opciones, seleccionadas_por_defecto=["PIB_Semanal"])

# Filtrado condicional del DataFrame
df_filtrado = df.copy()
if not p_all:
    df_filtrado = df_filtrado[df_filtrado["p"].isin(p_vals)]
if not q_all:
    df_filtrado = df_filtrado[df_filtrado["q"].isin(q_vals)]
if not svf_all:
    df_filtrado = df_filtrado[df_filtrado["SVF"].isin(svf_vals)]
if not svi_all:
    df_filtrado = df_filtrado[df_filtrado["SVI"].isin(svi_vals)]
if variables:
    df_filtrado = df_filtrado[df_filtrado["variable"].isin(variables)]

# Obtener modelos disponibles
modelos_disponibles = sorted(df_filtrado["modelo_id"].unique())

# Selector de modelos
modelos_seleccionados = st.sidebar.multiselect(
    "Seleccionar modelos específicos (máx 10 para vista desagregada)",
    opciones := modelos_disponibles,
    default=opciones[:10]
)

# === GRÁFICO AGRUPADO ===
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
else:
    st.warning("No hay modelos disponibles con los filtros seleccionados.")
