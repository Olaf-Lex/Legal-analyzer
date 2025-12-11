import streamlit as st
import pandas as pd
import re
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="LegalTech Contract Analyzer",
    page_icon="⚖️",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS (PARA QUE SE VEA "PRO") ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        color: white;
        background-color: #0e1117;
        border-radius: 8px;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN SIMULADO ---
def check_password():
    """Retorna `True` si el usuario tiene la clave correcta."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.markdown("### 🔒 Acceso Restringido - Demo Privado")
    password = st.text_input("Ingrese la clave de acceso (Pista: legaltech)", type="password")
    
    if st.button("Ingresar"):
        if password == "legaltech":  # CLAVE DE ACCESO
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Clave incorrecta. Intente nuevamente.")
    return False

if not check_password():
    st.stop()

# --- LÓGICA DE ANÁLISIS (EL "CEREBRO") ---
def analyze_contract(text):
    """Busca palabras clave de riesgo y genera estadísticas."""
    risks = []
    score = 100
    
    # Base de datos de "Red Flags" (Palabras clave)
    keywords = {
        "Jurisdicción Extranjera": ["Nueva York", "Delaware", "Londres", "arbitraje internacional"],
        "Responsabilidad Ilimitada": ["indemnidad total", "sin límite", "hold harmless", "consequential damages"],
        "Terminación Unilateral": ["sin causa", "terminación inmediata", "a su sola discreción"],
        "Renuncia de Derechos": ["renuncia a juicio", "waive trial", "renuncia a reclamar"],
        "Confidencialidad Perpetua": ["para siempre", "perpetuidad", "indefinidamente"]
    }

    found_counts = {}

    for category, terms in keywords.items():
        count = 0
        for term in terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                risks.append(f"⚠️ **{category}**: Se detectó el término '{term}'.")
                count += 1
                score -= 15 # Bajamos el puntaje por cada riesgo
        found_counts[category] = count

    # Ajuste final del score
    score = max(0, score) # Que no baje de 0
    
    return score, risks, found_counts

# --- INTERFAZ PRINCIPAL ---

# Barra lateral
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1904/1904565.png", width=50)
    st.header("Configuración del Caso")
    client_name = st.text_input("Cliente", "Empresa Alpha S.A.")
    contract_type = st.selectbox("Tipo de Contrato", ["NDA (Confidencialidad)", "Prestación de Servicios", "SaaS Agreement", "Arrendamiento"])
    st.divider()
    st.info("💡 Este prototipo utiliza análisis de patrones de texto para identificar cláusulas de alto riesgo predefinidas.")
    st.write("Versión 1.0.2")

# Título Principal
st.title("🤖 AI Contract Risk Auditor")
st.markdown(f"Análisis preliminar para: **{client_name}** | Documento: **{contract_type}**")
st.divider()

# Columnas para entrada de datos
col1, col2 = st.columns([1, 1])

contract_text = ""

with col1:
    st.subheader("1. Documento a Analizar")
    # Botón para cargar texto de ejemplo (Para el demo rápido)
    if st.button("📄 Cargar Contrato de Ejemplo con Riesgos"):
        contract_text = """
        ACUERDO DE SERVICIOS
        1. Las partes acuerdan someterse a la jurisdicción de los tribunales de Nueva York para cualquier disputa.
        2. El proveedor mantendrá en total indemnidad al cliente por cualquier daño, sin límite de monto (consequential damages).
        3. El cliente podrá terminar este contrato a su sola discreción y sin causa alguna.
        4. La confidencialidad de este acuerdo durará a perpetuidad.
        """
    else:
        contract_text = st.text_area("Pega el texto del contrato aquí:", height=300)

with col2:
    st.subheader("2. Resultados del Análisis")
    
    if contract_text:
        with st.spinner('Analizando cláusulas legales...'):
            time.sleep(1.5) # Simula tiempo de "pensamiento" de la IA
            score, risks, counts = analyze_contract(contract_text)
            
            # Mostrar Score con colores
            score_color = "red" if score < 60 else "orange" if score < 85 else "green"
            st.markdown(f"""
                <div style="text-align: center; border: 2px solid {score_color}; padding: 10px; border-radius: 10px;">
                    <h2 style="margin:0; color: {score_color};">Compliance Score: {score}/100</h2>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("") # Espacio
            
            # Gráfico de barras simple
            df_chart = pd.DataFrame(list(counts.items()), columns=["Categoría", "Hallazgos"])
            st.bar_chart(df_chart.set_index("Categoría"))

# Sección de Detalles (Abajo)
if contract_text:
    st.divider()
    st.subheader("🚩 Hallazgos Detallados")
    
    if risks:
        for risk in risks:
            st.error(risk)
        st.warning("Recomendación: Revisión manual requerida en las cláusulas marcadas.")
    else:
        st.success("✅ No se detectaron palabras clave de alto riesgo en el análisis preliminar.")

    # Call to Action final
    st.markdown("---")
    st.info("🚀 **¿Te gustó este demo?** Esta herramienta reduce el tiempo de revisión preliminar en un 40%. Contáctame para discutir cómo implementarla en la firma.")
