from __future__ import annotations

import pandas as pd
import streamlit as st

from simulacion_envase.exportar_excel import construir_excel_en_memoria
from simulacion_envase.parametros import ParametrosSimulacion
from simulacion_envase.simulador import SimuladorEnvase


st.set_page_config(
    page_title="TP3 Montecarlo - Envaso",
    page_icon="📦",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 3rem;
            padding-bottom: 2rem;
        }
        .main-title {
            font-size: 2.1rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }
        div[data-testid="stMetric"] {
            background: var(--background-color, transparent);
            border: 1px solid var(--secondary-background-color, #e5e7eb);
            padding: 0.4rem 0.6rem;
            border-radius: 0.6rem;
            box-shadow: 0 1px 3px rgba(16,24,40,.08);
        }
        div[data-testid="stMetricValue"] {
            font-size: 1rem;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.75rem;
        }
        .notice {
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 1rem;
            padding: .9rem 1rem;
        }
        section[data-testid="stSidebar"] {
            width: 600px !important;
        }
        section[data-testid="stSidebar"] > div:first-child {
            width: 600px !important;
        }
        .sidebar-label {
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 0.5rem;
            margin-bottom: 0.15rem;
            color: #6B7280;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] {
            width: 0px !important;
            min-width: 0px !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 0px !important;
            min-width: 0px !important;
            padding: 0px !important;
        }
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
            align-items: flex-start !important;
        }
        div[data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
        }
        .sidebar-label {
            margin-bottom: 0.5rem !important;
        }
        div[data-testid="stNumberInput"] {
            margin-top: 0rem !important;
        }
        .metric-gris + div[data-testid="stMetric"] {
            background: #f3f4f6 !important;
        }
        section[data-testid="stSidebar"] > div > div:first-child {
            position: sticky !important;
            top: 0 !important;
            z-index: 999 !important;
            background: var(--background-color) !important;
        }
        section[data-testid="stSidebar"] button[kind="headerNoPadding"],
        section[data-testid="stSidebar"] button[aria-label*="Close"],
        section[data-testid="stSidebar"] button[aria-label*="Open"] {
            position: fixed !important;
            top: 0.5rem !important;
            left: 560px !important;
            z-index: 999 !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] button[aria-label*="Open"] {
            left: 0.5rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">Simulación Montecarlo - Sistema de Envaso</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Parámetros")

    col_izq, col_der = st.columns(2)
    with col_izq:
        cantidad_jornadas = st.number_input("Cantidad total de jornadas N", min_value=1, value=100_000, step=1)
        fila_inicial = st.number_input("Fila inicial a mostrar", min_value=1, value=1, step=1)
    with col_der:
        st.markdown('<div class="sidebar-label" style="visibility: hidden;">.</div>', unsafe_allow_html=True)
        usar_semilla = st.checkbox("Usar semilla fija", value=True)
        semilla = st.number_input("Semilla", min_value=0, value=12345, step=1, disabled=not usar_semilla)

    st.divider()
    st.subheader("Probabilidades")

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown('<div class="sidebar-label">Sectores</div>', unsafe_allow_html=True)
        prob_circuito_2 = st.number_input("P(circuito 2 sectores)", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    with col_der:
        st.markdown('<div class="sidebar-label" style="visibility: hidden;">Sectores</div>', unsafe_allow_html=True)
        prob_circuito_4 = st.number_input("P(circuito 4 sectores)", min_value=0.0, max_value=1.0, value=0.50, step=0.01)

    col_izq, col_der = st.columns(2)
    with col_izq:
        prob_circuito_5 = st.number_input("P(circuito 5 sectores)", min_value=0.0, max_value=1.0, value=0.25, step=0.01)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown('<div class="sidebar-label">Escaneo</div>', unsafe_allow_html=True)
        prob_parada_escaneo = st.number_input("P(parada por escaneo)", min_value=0.0, max_value=1.0, value=0.55, step=0.01)
    with col_der:
        st.markdown('<div class="sidebar-label">Congestión</div>', unsafe_allow_html=True)
        prob_congestion = st.number_input("P(congestión en 2 o 5 sectores)", min_value=0.0, max_value=1.0, value=0.35, step=0.01)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown('<div class="sidebar-label">Auditoría</div>', unsafe_allow_html=True)
        prob_auditoria = st.number_input("P(auditoría)", min_value=0.0, max_value=1.0, value=40 / 180, step=0.001, format="%.6f")

    st.divider()
    st.subheader("Tiempos")

    col_izq, col_der = st.columns(2)
    with col_izq:
        media_demora_escaneo = st.number_input("Media demora escaneo", min_value=0.0, value=4.0, step=0.1)
        media_demora_auditoria = st.number_input("Media demora auditoría", min_value=0.0, value=5.0, step=0.1)
    with col_der:
        media_tiempo_sector = st.number_input("Media tiempo por sector", min_value=0.0, value=4.0, step=0.1)
        desviacion_tiempo_sector = st.number_input("Desvío tiempo por sector", min_value=0.0, value=85 / 60, step=0.01, format="%.6f")
        aumento_congestion = st.number_input("Aumento por congestión", min_value=0.0, value=0.60, step=0.05)

    simular = st.button("Simular", type="primary", use_container_width=True)

if not simular:
    st.markdown(
        '<div class="notice">Configurá los parámetros en el panel lateral y presioná <b>Simular</b>.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

try:
    parametros = ParametrosSimulacion(
        cantidad_jornadas=int(cantidad_jornadas),
        fila_inicial=int(fila_inicial),
        semilla=int(semilla) if usar_semilla else None,
        prob_circuito_2=float(prob_circuito_2),
        prob_circuito_4=float(prob_circuito_4),
        prob_circuito_5=float(prob_circuito_5),
        prob_parada_escaneo=float(prob_parada_escaneo),
        prob_congestion=float(prob_congestion),
        prob_auditoria=float(prob_auditoria),
        media_demora_escaneo=float(media_demora_escaneo),
        media_demora_auditoria=float(media_demora_auditoria),
        media_tiempo_sector=float(media_tiempo_sector),
        desviacion_tiempo_sector=float(desviacion_tiempo_sector),
        aumento_congestion=float(aumento_congestion),
    )

    simulador = SimuladorEnvase(parametros)
    resultado = simulador.simular()

except Exception as error:
    st.error(f"No se pudo ejecutar la simulación: {error}")
    st.stop()

resultados = resultado.resultados_solicitados()

st.subheader("Resultados")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Promedio traslado", f"{resultados['Tiempo promedio de traslado']:.4f} min")
c2.metric("% parada + auditoría", f"{resultados['Porcentaje con parada y auditoría']:.2f}%")
c3.metric("Sin parada ni auditoría", f"{resultados['Cantidad sin parada ni auditoría']}")
c4.metric("Máximo", f"{resultados['Tiempo máximo de traslado']:.4f} min")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Mínimo", f"{resultados['Tiempo mínimo de traslado']:.4f} min")
c6.markdown(
    f"""<div style="background: #f3f4f6; border: 1px solid #e5e7eb; padding: 0.4rem 0.6rem; border-radius: 0.6rem; box-shadow: 0 1px 3px rgba(16,24,40,.08);">
        <div style="font-size: 0.75rem; color: rgb(49,51,63);">% con congestión</div>
        <div style="font-size: 1rem; font-weight: 600; color: rgb(49,51,63);">{resultados['Variable adicional 1 - Porcentaje con congestión']:.2f}%</div>
    </div>""",
    unsafe_allow_html=True,
)
c7.markdown(
    f"""<div style="background: #f3f4f6; border: 1px solid #e5e7eb; padding: 0.4rem 0.6rem; border-radius: 0.6rem; box-shadow: 0 1px 3px rgba(16,24,40,.08);">
        <div style="font-size: 0.75rem; color: rgb(49,51,63);">Prom. demora escaneo</div>
        <div style="font-size: 1rem; font-weight: 600; color: rgb(49,51,63);">{resultados['Variable adicional 2 - Promedio demora escaneo cuando hubo parada']:.4f} min</div>
    </div>""",
    unsafe_allow_html=True,
)
c8.markdown(
    f"""<div style="background: #f3f4f6; border: 1px solid #e5e7eb; padding: 0.4rem 0.6rem; border-radius: 0.6rem; box-shadow: 0 1px 3px rgba(16,24,40,.08);">
        <div style="font-size: 0.75rem; color: rgb(49,51,63);">Prom. demora auditoría</div>
        <div style="font-size: 1rem; font-weight: 600; color: rgb(49,51,63);">{resultados['Variable adicional 3 - Promedio demora auditoría cuando hubo auditoría']:.4f} min</div>
    </div>""",
    unsafe_allow_html=True,
)

vector_visible = pd.DataFrame([fila.a_diccionario_visible() for fila in resultado.filas_seleccionadas])
fila_n = pd.DataFrame([resultado.fila_final.a_diccionario_visible()])

fin_visible = min(parametros.cantidad_jornadas, parametros.fila_inicial + parametros.filas_extra_visibles)
st.subheader(f"Vector de estado visible: filas {parametros.fila_inicial} a {fin_visible}")
st.dataframe(vector_visible, use_container_width=True, hide_index=True)

st.subheader(f"Fila N: jornada {parametros.cantidad_jornadas}")
st.dataframe(fila_n, use_container_width=True, hide_index=True)

excel_en_memoria = construir_excel_en_memoria(resultado)
st.download_button(
    label="Descargar Excel con resultados",
    data=excel_en_memoria,
    file_name="simulacion_envase_resultados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
