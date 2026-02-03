import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

# --- 1. DATOS HISTÓRICOS REALES S&P 500 (1974 - 2024) ---
hist_data = {
    "Año": list(range(1974, 2025)),
    "Rent": [
        -26.47, 37.20, 23.84, -7.18, 6.56, 18.44, 32.42, -4.91, 21.55, 22.56, 6.27, 31.73, 18.67, 5.25, 16.61, 31.69,
        -3.10, 30.47, 7.62, 10.08, 1.32, 37.58, 22.96, 33.36, 28.58, 21.04, -9.10, -11.89, -22.10, 28.68, 10.88, 4.91,
        15.79, 5.49, -37.00, 26.46, 15.06, 2.11, 16.00, 32.39, 13.69, 1.38, 11.96, 21.83, -4.38, 31.49, 18.40, 28.71,
        -18.11, 26.29, 25.02
    ]
}
df_hist = pd.DataFrame(hist_data)

st.set_page_config(page_title="Simulador Financiero Pro V5", layout="wide")
st.title("🚀 Simulador Integral de Inversiones - Versión Mejorada")

# --- 2. SIDEBAR: PARÁMETROS GLOBALES ---
with st.sidebar:
    st.header("👤 Perfil y Fiscalidad")
    salario_bruto = st.number_input("Salario Bruto Anual (€)", value=40000, min_value=0)
    irpf_actual = st.slider("Tu IRPF hoy (%)", 19, 47, 30)
    años = st.slider("Plazo de inversión (años)", 1, 40, 25)
    irpf_jubilacion = st.slider("Tipo IRPF al jubilarte (%)", 19, 47, 25)
    edad_actual = st.number_input("Edad actual", value=35, min_value=18, max_value=100)
    
    st.header("💸 Comisiones (Gastos)")
    com_gestion = st.slider("Gestión anual (TER) %", 0.0, 2.0, 0.15, step=0.01) / 100
    com_compra = st.slider("Comisión por cada Aportación %", 0.0, 2.0, 0.0, step=0.05) / 100
    com_venta = st.slider("Comisión por Venta (Broker) %", 0.0, 2.0, 0.10, step=0.05) / 100
    com_custodia = st.slider("Custodia anual %", 0.0, 0.5, 0.0, step=0.01) / 100
    
    st.header("📉 Inflación (IPC)")
    tasa_inflacion_pct = st.slider("Inflación anual estimada (%)", 0.0, 8.0, 2.5)
    tasa_inflacion = tasa_inflacion_pct / 100
    ajustar_ipc_aportes = st.checkbox("Indexar APORTACIONES al IPC", value=True)
    ajustar_ipc_valor_real = st.checkbox("Ver resultados en PODER ADQUISITIVO", value=True)
    
    if ajustar_ipc_valor_real:
        st.warning(f"⚠️ Mostrando en PODER ADQUISITIVO. Con inflación {tasa_inflacion_pct}% durante {años} años, 1€ de hoy = {(1+tasa_inflacion)**años:.2f}€ futuros")

    st.header("🛒 S&P 500")
    ini_sp = st.number_input("Inversión Inicial S&P (€)", value=5000, min_value=0)
    m_sp_ini = st.number_input("Aportación Mensual S&P (€/mes)", value=200, min_value=0)

    st.header("🏢 Plan de Empleo (PE)")
    ini_pe = st.number_input("Capital Inicial PE (€)", value=0, min_value=0)
    pct_empleado = st.slider("Tu aportación PE (% bruto)", 0.0, 10.0, 2.5) / 100
    pct_empresa = st.slider("Empresa PE (% bruto)", 0.0, 15.0, 5.5) / 100
    rent_pe_estimada = st.slider("Rentabilidad PE (%)", 0.0, 15.0, 4.5) / 100
    limite_fiscal_pe = st.number_input("Límite deducción fiscal PE (€/año)", value=8500, min_value=0)

    st.header("👴 Plan Individual (PP)")
    ini_pp = st.number_input("Capital Inicial PP (€)", value=0, min_value=0)
    m_pp_ini = st.number_input("Aportación PP (€/mes)", value=125, min_value=0)
    rent_pp_estimada = st.slider("Rentabilidad PP (%)", 0.0, 15.0, 6.0) / 100
    limite_fiscal_pp = st.number_input("Límite deducción fiscal PP (€/año)", value=1500, min_value=0)

    st.header("🛡️ Renta Fija")
    ini_rf = st.number_input("Inversión Inicial RF (€)", value=10000, min_value=0)
    m_rf_ini = st.number_input("Aportación RF (€/mes)", value=200, min_value=0)
    interes_fijo = st.slider("Interés Renta Fija (%)", 0.0, 10.0, 3.5) / 100

# --- 3. SECCIÓN HISTÓRICA ---
st.subheader("📊 Referencia Histórica S&P 500 (1974 - 2024)")
with st.expander("Ver estadísticas de los últimos 50 años", expanded=False):
    col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
    with col_h1:
        fig_hist = px.bar(df_hist, x="Año", y="Rent", color="Rent", 
                         color_continuous_scale="RdYlGn", 
                         title="Rentabilidad Anual S&P 500")
        fig_hist.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig_hist, use_container_width=True)
    with col_h2:
        st.metric("Media histórica", f"{df_hist['Rent'].mean():.2f}%")
        st.metric("Mediana", f"{df_hist['Rent'].median():.2f}%")
        st.metric("Desviación típica", f"{df_hist['Rent'].std():.2f}%")
    with col_h3:
        st.metric("Peor año", f"{df_hist['Rent'].min():.1f}%", delta="2008")
        st.metric("Mejor año", f"{df_hist['Rent'].max():.1f}%", delta="1995")
        positivos = (df_hist['Rent'] > 0).sum()
        st.metric("Años positivos", f"{positivos}/51", delta=f"{positivos/51*100:.0f}%")

# --- 4. CONFIGURACIÓN DE ESCENARIOS ---
if 'curva' not in st.session_state or len(st.session_state.curva) != años:
    st.session_state.curva = np.random.choice(df_hist["Rent"].values, size=años)

st.subheader("📈 Configuración del Escenario de Simulación")

# Botones de acceso rápido
col_quick1, col_quick2, col_quick3, col_quick4 = st.columns(4)
with col_quick1:
    if st.button("🎯 Usar Media Histórica (12.9%)", use_container_width=True):
        muestras = np.random.choice(df_hist["Rent"].values, size=años)
        st.session_state.curva = muestras + (12.9 - np.mean(muestras))
        st.rerun()
with col_quick2:
    if st.button("🛡️ Conservador (8%)", use_container_width=True):
        muestras = np.random.choice(df_hist["Rent"].values, size=años)
        st.session_state.curva = muestras + (8.0 - np.mean(muestras))
        st.rerun()
with col_quick3:
    if st.button("📈 Optimista (15%)", use_container_width=True):
        muestras = np.random.choice(df_hist["Rent"].values, size=años)
        st.session_state.curva = muestras + (15.0 - np.mean(muestras))
        st.rerun()
with col_quick4:
    if st.button("🎲 Montecarlo 50%", use_container_width=True):
        sims = np.random.choice(df_hist["Rent"].values, size=(1000, años))
        st.session_state.curva = np.percentile(sims, 50, axis=0)
        st.rerun()

tab_gen, tab_man, tab_mc = st.tabs(["🎮 Generador de Escenarios", "📝 Editor Manual", "🎲 Montecarlo"])

with tab_gen:
    st.info("💡 **Guía rápida:** Conservador (5-7% anual) | Realista (8-10% anual) | Optimista (11-13% anual)")
    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        rent_objetivo = st.slider("Media Objetivo S&P (%)", 0.0, 15.0, 10.0)
        if rent_objetivo < 7: st.warning("🐢 Escenario MUY CONSERVADOR")
        elif rent_objetivo < 9: st.info("🛡️ Escenario CONSERVADOR")
        elif rent_objetivo < 11: st.success("✅ Escenario REALISTA")
        elif rent_objetivo < 13: st.success("📈 Escenario OPTIMISTA")
        else: st.error("🚀 Escenario MUY OPTIMISTA")
        
        modelo_pre = st.selectbox("Cargar escenario histórico:", 
                                  ["Aleatorio (Bootstrap)", "Media Histórica (12.9%)", "Conservador (8%)", 
                                   "Crisis 2008", "Burbuja Dotcom", "Década 90 (Oro)", "Últimos 10 años"])
        if st.button("🔄 Aplicar Escenario"):
            if modelo_pre == "Crisis 2008":
                idx = df_hist[df_hist['Año'] == 2008].index[0]
                st.session_state.curva = np.resize(df_hist['Rent'].iloc[idx:].values, años)
            elif modelo_pre == "Burbuja Dotcom":
                idx = df_hist[df_hist['Año'] == 2000].index[0]
                st.session_state.curva = np.resize(df_hist['Rent'].iloc[idx:].values, años)
            elif modelo_pre == "Década 90 (Oro)":
                idx = df_hist[df_hist['Año'] == 1990].index[0]
                st.session_state.curva = np.resize(df_hist['Rent'].iloc[idx:].values, años)
            elif modelo_pre == "Últimos 10 años":
                st.session_state.curva = np.resize(df_hist['Rent'].iloc[-10:].values, años)
            else:
                muestras = np.random.choice(df_hist["Rent"].values, size=años)
                st.session_state.curva = muestras + (rent_objetivo - np.mean(muestras))
            st.rerun()
    with col_g2:
        media_escenario = np.mean(st.session_state.curva)
        fig_pre = go.Figure()
        fig_pre.add_trace(go.Scatter(y=st.session_state.curva, mode='lines+markers', name='Rentabilidad', line=dict(color='cyan')))
        fig_pre.add_hline(y=0, line_color="red", line_dash="dash")
        fig_pre.update_layout(template="plotly_dark", height=300, title="Vista Previa del Escenario")
        st.plotly_chart(fig_pre, use_container_width=True)

with tab_man:
    df_ed = pd.DataFrame({"Año": range(1, años + 1), "Rent%": st.session_state.curva})
    edited = st.data_editor(df_ed, hide_index=True, use_container_width=True)
    if st.button("✅ Aplicar cambios manuales"):
        st.session_state.curva = edited["Rent%"].values
        st.success("Escenario actualizado")

with tab_mc:
    num_sims = st.slider("Número de simulaciones", 100, 5000, 1000)
    percentil = st.slider("Percentil", 5, 95, 50)
    if st.button("🎯 Generar simulación"):
        sims = np.random.choice(df_hist["Rent"].values, size=(num_sims, años))
        st.session_state.curva = np.percentile(sims, percentil, axis=0)
        st.rerun()

# --- 5. MOTOR DE CÁLCULO ---
lista_rent_sp = st.session_state.curva / 100
data_calc = []
data_all_products = []
data_detallado = [] # CORRECCIÓN: Inicialización necesaria

# Inicialización saldos
s_sp, s_pe, s_pp, s_rf = float(ini_sp), float(ini_pe), float(ini_pp), float(ini_rf)
inv_sp_nom, inv_pe_nom, inv_pp_nom, inv_rf_nom = float(ini_sp), float(ini_pe), float(ini_pp), float(ini_rf)
inv_sp_real, inv_pe_real, inv_pp_real, inv_rf_real = float(ini_sp), float(ini_pe), float(ini_pp), float(ini_rf)
com_tot_sp, com_tot_pe, com_tot_pp, com_tot_rf = 0.0, 0.0, 0.0, 0.0
ahorro_f_pe, ahorro_f_pp = 0.0, 0.0
m_sp, m_pp, m_rf = float(m_sp_ini), float(m_pp_ini), float(m_rf_ini)
salario_acum = float(salario_bruto)

# Variables auxiliares Drawdown
pico_max_sp = s_sp
años_en_drawdown = 0

for i in range(años):
    factor_inf_anual = (1 + tasa_inflacion)**(i+1)
    if ajustar_ipc_aportes and i > 0:
        m_sp *= (1 + tasa_inflacion); m_pp *= (1 + tasa_inflacion)
        m_rf *= (1 + tasa_inflacion); salario_acum *= (1 + tasa_inflacion)
    
    rv_sp = lista_rent_sp[i]
    saldo_ini_año_sp = s_sp
    aportado_este_año_sp = 0
    comisiones_este_año_sp = 0
    
    # Custodia anual
    c_cust_sp = s_sp * com_custodia
    s_sp -= c_cust_sp; com_tot_sp += c_cust_sp; comisiones_este_año_sp += c_cust_sp
    
    # Otros productos custodia
    s_pe -= s_pe * com_custodia; s_pp -= s_pp * com_custodia; s_rf -= s_rf * com_custodia

    for mes in range(12):
        # Aportaciones S&P
        m_sp_n = m_sp * (1 - com_compra)
        com_tot_sp += m_sp * com_compra; comisiones_este_año_sp += m_sp * com_compra
        aportado_este_año_sp += m_sp
        
        # Capitalización S&P
        v_p_sp = s_sp
        s_sp = (s_sp + m_sp_n) * (1 + (rv_sp/12) - (com_gestion/12))
        com_tot_sp += (v_p_sp + m_sp_n) * (com_gestion/12)
        comisiones_este_año_sp += (v_p_sp + m_sp_n) * (com_gestion/12)
        
        # Otros productos simplificados
        s_pp = (s_pp + m_pp*(1-com_compra)) * (1 + (rent_pp_estimada/12) - (com_gestion/12))
        s_rf = (s_rf + m_rf*(1-com_compra)) * (1 + (interes_fijo/12) - (com_gestion/12))
        ap_pe = (salario_acum * (pct_empleado + pct_empresa)) / 12
        s_pe = (s_pe + ap_pe) * (1 + (rent_pe_estimada/12) - (com_gestion/12))
        
        inv_sp_nom += m_sp; inv_pp_nom += m_pp; inv_rf_nom += m_rf; inv_pe_nom += (salario_acum * pct_empleado / 12)
        f_i_m = (1 + tasa_inflacion)**(i + mes/12)
        inv_sp_real += m_sp / f_i_m; inv_pp_real += m_pp / f_i_m; inv_rf_real += m_rf / f_i_m; inv_pe_real += (salario_acum * pct_empleado / 12) / f_i_m

    # Ahorro fiscal
    ahorro_f_pe += min(salario_acum*pct_empleado, limite_fiscal_pe) * (irpf_actual/100)
    ahorro_f_pp += min(m_pp*12, limite_fiscal_pp) * (irpf_actual/100)

    # Lógica Drawdown
    if s_sp > pico_max_sp: pico_max_sp = s_sp; años_en_drawdown = 0
    else: años_en_drawdown += 1
    
    data_detallado.append({
        "Año": i+1, "Rent. Año (%)": rv_sp * 100, "Aportado Año": aportado_este_año_sp,
        "Comisiones Año": comisiones_este_año_sp, "Saldo Inicio": saldo_ini_año_sp,
        "Saldo Final": s_sp, "Ganancia/Pérdida": s_sp - saldo_ini_año_sp - aportado_este_año_sp,
        "Variación (%)": ((s_sp/saldo_ini_año_sp)-1)*100 if saldo_ini_año_sp>0 else 0,
        "Capital Invertido": inv_sp_nom, "Beneficio Acum.": s_sp - inv_sp_nom,
        "Pico Máximo": pico_max_sp, "Drawdown (%)": ((s_sp/pico_max_sp)-1)*100, "Años en Drawdown": años_en_drawdown
    })
    
    data_all_products.append({
        "Año": i+1,
        "S&P 500": s_sp/factor_inf_anual if ajustar_ipc_valor_real else s_sp,
        "Plan Empleo": s_pe/factor_inf_anual if ajustar_ipc_valor_real else s_pe,
        "Plan Individual": s_pp/factor_inf_anual if ajustar_ipc_valor_real else s_pp,
        "Renta Fija": s_rf/factor_inf_anual if ajustar_ipc_valor_real else s_rf
    })

# --- 6. SALIDA Y FISCALIDAD ---
def tax_ahorro(b_f, i_n):
    g = max(0, b_f - i_n)
    if g <= 6000: return g * 0.19
    elif g <= 50000: return 1140 + (g - 6000) * 0.21
    elif g <= 200000: return 1140 + 9240 + (g - 50000) * 0.23
    else: return 1140 + 9240 + 34500 + (g - 200000) * 0.26

s_sp_f = s_sp * (1 - com_venta); t_sp = tax_ahorro(s_sp_f, inv_sp_nom)
s_pe_f = s_pe * (1 - com_venta); t_pe = s_pe_f * (irpf_jubilacion / 100)
s_pp_f = s_pp * (1 - com_venta); t_pp = s_pp_f * (irpf_jubilacion / 100)
s_rf_f = s_rf * (1 - com_venta); t_rf = tax_ahorro(s_rf_f, inv_rf_nom)

# --- 7. TARJETAS ---
st.subheader("💰 Resultados Finales")
def render_card(tit, s_f_n, i_n, i_r, t_n, a_n, c_t_n, icono="📊"):
    def_ = (1 + tasa_inflacion)**años if ajustar_ipc_valor_real else 1.0
    neto = (s_f_n - t_n) / def_
    i_c = i_r if ajustar_ipc_valor_real else i_n
    r_r = ((neto / i_c) - 1) * 100 if i_c > 0 else 0
    with st.container(border=True):
        st.markdown(f"### {icono} {tit}")
        c1, c2, c3 = st.columns(3)
        c1.metric("NETO FINAL", f"{neto:,.0f} €", f"{r_r:+.1f}%")
        c2.metric("ESFUERZO REAL", f"{i_c:,.0f} €")
        c3.metric("TAE", f"{((neto/i_c)**(1/años)-1)*100:.2f}%" if i_c>0 else "0%")

col1, col2 = st.columns(2)
with col1:
    render_card("S&P 500 Indexado", s_sp_f, inv_sp_nom, inv_sp_real, t_sp, 0, com_tot_sp, "📈")
    render_card("Plan de Empleo", s_pe_f, inv_pe_nom, inv_pe_real, t_pe, ahorro_f_pe, com_tot_pe, "🏢")
with col2:
    render_card("Plan Individual", s_pp_f, inv_pp_nom, inv_pp_real, t_pp, ahorro_f_pp, com_tot_pp, "👴")
    render_card("Renta Fija", s_rf_f, inv_rf_nom, inv_rf_real, t_rf, 0, com_tot_rf, "🛡️")

# --- 8. COMPARATIVA ---
st.subheader("🔍 Comparativa de Productos")
df_comp = pd.DataFrame({
    "Producto": ["S&P 500", "Plan Empleo", "Plan Individual", "Renta Fija"],
    "Neto Final": [(s_sp_f-t_sp)/def_, (s_pe_f-t_pe)/def_, (s_pp_f-t_pp)/def_, (s_rf_f-t_rf)/def_],
    "Inversión": [inv_sp_real, inv_pe_real, inv_pp_real, inv_rf_real] if ajustar_ipc_valor_real else [inv_sp_nom, inv_pe_nom, inv_pp_nom, inv_rf_nom]
})
st.plotly_chart(px.bar(df_comp, x="Producto", y="Neto Final", color="Producto", template="plotly_dark"), use_container_width=True)

# --- 9. ESCENARIOS RÁPIDOS ---
st.subheader("🎲 Comparativa de Escenarios S&P")
with st.expander("Ver Pesimista vs Realista vs Optimista"):
    esc_vals = {"Pesimista (6%)": 6.0, "Realista (10%)": 10.0, "Optimista (14%)": 14.0}
    res_esc = []
    for k, v in esc_vals.items():
        s_t = float(ini_sp)
        for _ in range(años): s_t = (s_t + m_sp_ini*12) * (1+v/100)
        res_esc.append({"Escenario": k, "Neto": s_t/def_})
    st.table(pd.DataFrame(res_esc))

# --- 10. EVOLUCIÓN ---
st.subheader("📉 Evolución Temporal")
st.plotly_chart(px.line(pd.DataFrame(data_all_products), x="Año", y=["S&P 500", "Plan Empleo", "Plan Individual", "Renta Fija"], template="plotly_dark"), use_container_width=True)

# --- 10.5. DETALLE (ESTO CORRIGE TU ERROR) ---
st.subheader("📋 Análisis Detallado (S&P 500)")
with st.expander("📊 Ver tabla y Drawdown", expanded=False):
    if len(data_detallado) > 0:
        df_det = pd.DataFrame(data_detallado)
        c_d1, c_d2 = st.columns(2)
        c_d1.plotly_chart(px.bar(df_det, x="Año", y="Drawdown (%)", color="Drawdown (%)", template="plotly_dark"))
        c_d2.plotly_chart(px.bar(df_det, x="Año", y="Ganancia/Pérdida", template="plotly_dark"))
        st.dataframe(df_det.style.format("{:.0f}"), use_container_width=True)

# --- 11. SENSIBILIDAD ---
st.subheader("🎯 Análisis de Sensibilidad")
with st.expander("Sensibilidad a Inflación y Rentabilidad"):
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        infs = list(range(0, 8))
        impacto = [(s_sp_f-t_sp)/((1+i/100)**años) for i in infs]
        st.plotly_chart(px.line(x=infs, y=impacto, title="Impacto Inflación", template="plotly_dark"))
    with c_s2:
        rents = list(range(0, 16))
        impacto_r = [float(ini_sp)*(1+r/100)**años for r in rents]
        st.plotly_chart(px.line(x=rents, y=impacto_r, title="Impacto Rentabilidad", template="plotly_dark"))

# --- 12. RESUMEN ---
st.subheader("📑 Resumen Ejecutivo")
t_neto = ((s_sp_f-t_sp)+(s_pe_f-t_pe)+(s_pp_f-t_pp)+(s_rf_f-t_rf))/def_
cr1, cr2, cr3 = st.columns(3)
cr1.metric("CAPITAL NETO TOTAL", f"{t_neto:,.0f} €")
cr2.metric("COSTE FISCAL/COMISIONES", f"{(com_tot_sp+t_sp)/def_:,.0f} €")
cr3.metric("EDAD FINAL", f"{edad_actual+años} años")

# --- 13. NOTAS ---
with st.expander("ℹ️ Notas"):
    st.write("Cálculos basados en fiscalidad 2024. Rentabilidades pasadas no garantizan futuras.")

# --- 14. EXPORTAR ---
st.download_button("📥 Descargar CSV", pd.DataFrame(data_detallado).to_csv().encode('utf-8'), "simulacion.csv", "text/csv")