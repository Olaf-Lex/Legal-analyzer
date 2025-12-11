import streamlit as st
import PyPDF2
import docx  # Requiere instalar python-docx
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="NDA Risk Analyzer", page_icon="⚖️")

# --- LÓGICA DE NEGOCIO (EL CEREBRO) ---
def extract_text_from_file(uploaded_file):
    """Extrae texto de PDF o DOCX directamente desde memoria."""
    text = ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            # Limite de seguridad: Solo lee las primeras 10 páginas para evitar crash
            for i, page in enumerate(reader.pages):
                if i > 10: break 
                text += page.extract_text() or ""
        
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        return text[:10000] # Limite de caracteres
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_nda_text(text):
    """Tu lógica de análisis de riesgos original."""
    risks = []
    risk_score = 0
    text_lower = text.lower()
    
    # Lógica de detección
    if "10 years" in text_lower or "ten years" in text_lower:
        risks.append({
            "level": "high",
            "title": "Confidencialidad Excesiva",
            "text": "Se detectó un periodo de 10 años.",
            "suggestion": "Negociar a 3-5 años."
        })
        risk_score += 30
    
    if "irreparable harm" in text_lower:
        risks.append({
            "level": "high",
            "title": "Daño Irreparable Automático",
            "text": "Cláusula de 'Irreparable Harm' detectada.",
            "suggestion": "Limitar a daños reales probados."
        })
        risk_score += 25

    if not risks:
        risk_score = 10
        risks.append({"level": "low", "title": "Sin Riesgos Obvios", "text": "Parece estándar.", "suggestion": "Revisar manualmente."})

    return min(risk_score, 100), risks

# --- INTERFAZ DE USUARIO (LO QUE VE LA GENTE) ---
st.title("⚖️ AI Legal Assistant: NDA Reviewer")
st.markdown("Sube un contrato (PDF o DOCX) para detectar riesgos legales automáticamente.")

uploaded_file = st.file_uploader("Arrastra tu archivo aquí", type=['pdf', 'docx'])

if uploaded_file is not None:
    with st.spinner('Analizando documento...'):
        # 1. Extracción
        text_content = extract_text_from_file(uploaded_file)
        
        # 2. Análisis
        score, findings = analyze_nda_text(text_content)
        
        # 3. Mostrar Resultados
        st.divider()
        
        # Columna de puntuación
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="Nivel de Riesgo", value=f"{score}/100", 
                     delta="- Alto Riesgo" if score > 50 else "Aceptable",
                     delta_color="inverse")
        
        with col2:
            st.subheader("Hallazgos Clave")
            for risk in findings:
                if risk['level'] == 'high':
                    st.error(f"**{risk['title']}**: {risk['suggestion']}")
                elif risk['level'] == 'medium':
                    st.warning(f"**{risk['title']}**: {risk['suggestion']}")
                else:
                    st.success(f"**{risk['title']}**: {risk['suggestion']}")

        with st.expander("Ver texto extraído"):
            st.text(text_content)
