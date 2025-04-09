import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página en modo "wide"
st.set_page_config(layout="wide")

@st.cache_data
def cargar_datos():
    return pd.read_csv("models.csv", parse_dates=["Time"])

@st.cache_data
def cargar_observed():
    return pd.read_csv("observed.csv", parse_dates=["Time"])

df = cargar_datos()
df_observed = cargar_observed()

# --- SIDEBAR DE NAVEGACIÓN ---
st.sidebar.title("Navegación")
page = st.sidebar.selectbox(
    "Seleccione la sección",
    ["Dashboard", "Convergencia"]
)

# --- Función de la página principal ("Dashboard") ---
def show_dashboard():

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

    # Filtrado principal (sin variable, pues se manejarán individualmente abajo)
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
        default=modelos_disponibles[:3]
    )
    if not modelos_seleccionados:
        modelos_seleccionados = modelos_disponibles[:3]

    # Selector en el sidebar para el 2do gráfico (PIB o Consumo)
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
        var_modeled = "PIB_Semanal"     # Modelado por cada modelo
        var_observed = "PIB_Observado"           # Observado (mismo para todos)
        titulo_2 = "PIB"
    else:
        var_modeled = "Consumo_Semanal"
        var_observed = "Consumo_Observado"
        titulo_2 = "Consumo"

    st.subheader(f"Gráfico 2: {var_modeled} (modelado) vs {var_observed} (observado)")

    df_mod_modeled = df_filtrado[
        (df_filtrado["variable"] == var_modeled) & 
        (df_filtrado["modelo_id"].isin(modelos_seleccionados))
    ]
    
    df_mod_observed = df_observed[var_observed]

    # Quitamos NaN de la serie observada para evitar problemas
    # df_mod_observed = df_mod_observed.dropna(subset=["value"])

    fig2 = go.Figure()

    # Trazas para cada modelo (líneas)
    for modelo in modelos_seleccionados:
        df_tmp = df_mod_modeled[df_mod_modeled["modelo_id"] == modelo].dropna(subset=["value"])
        if not df_tmp.empty:
            fig2.add_trace(go.Scatter(
                x=df_tmp["Time"],
                y=df_tmp["value"],
                mode='lines',
                name=f"{var_modeled} - {modelo}"
            ))

    # Trazas para la serie observada (sólo marcadores)
    if not df_mod_observed.empty:
        fig2.add_trace(go.Scatter(
            x=df_mod_observed["Time"],
            y=df_mod_observed[var_observed],
            mode='markers',
            connectgaps=False,
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

    # === GRÁFICO 4: 1 - probabilities ===
    st.subheader("Gráfico 4: 1 - probabilities")

    df_prob = df_filtrado[
        (df_filtrado["variable"] == "probabilities") &
        (df_filtrado["modelo_id"].isin(modelos_seleccionados))
    ].copy()
    if not df_prob.empty:
        df_prob["value_plot"] = 1 - df_prob["value"]
        fig_prob = px.line(
            df_prob,
            x="Time", y="value_plot",
            color="modelo_id",
            title="Evolución de (1 - probabilities)"
        )
        st.plotly_chart(fig_prob, use_container_width=True)
    else:
        st.info("No hay datos para la variable 'probabilities' en los filtros seleccionados.")

    # === GRÁFICOS DESAGREGADOS (Factor y SuperFactor), pero AGRUPADOS POR VARIABLE ===
    if st.checkbox("Mostrar gráficos desagregados (Factor y SuperFactor)"):
        st.subheader("Gráficos individuales en panel (agrupados por variable)")

        variables_desagregadas = ["Factor", "SuperFactor"]
        
        for var in variables_desagregadas:
            st.markdown(f"## Variable: {var}")
            
            # Tomamos sólo filas con la variable actual
            df_var = df_filtrado[df_filtrado["variable"] == var]
            if df_var.empty:
                st.info(f"No hay datos para '{var}' con los filtros actuales.")
                continue

            # Mostramos los gráficos de esta variable en un grid de 3 columnas,
            # uno por cada modelo seleccionado.
            num_cols = 3
            for i in range(0, len(modelos_seleccionados), num_cols):
                cols = st.columns(num_cols)
                block_models = modelos_seleccionados[i : i + num_cols]
                for j, modelo in enumerate(block_models):
                    df_tmp = df_var[df_var["modelo_id"] == modelo]
                    if df_tmp.empty:
                        # El modelo no tiene datos para esta variable
                        with cols[j]:
                            st.info(f"{var} no disponible en {modelo}")
                        continue
                    
                    fig_tmp = px.line(
                        df_tmp,
                        x="Time", y="value",
                        title=f"{var} – Modelo {modelo}"
                    )
                    with cols[j]:
                        st.plotly_chart(fig_tmp, use_container_width=True)

    # === TABLA DE DATOS (opcional) ===
    if st.checkbox("Mostrar tabla de datos filtrados"):
        st.dataframe(df_observed)

# --- Función de la página "Convergencia" ---
def show_convergence():
    st.title("Sección de Convergencia")
    st.write("Pendiente añadir sección convergencia.")

# --- Lógica principal: mostrar la página elegida ---
if page == "Dashboard":
    show_dashboard()
else:
    show_convergence()
