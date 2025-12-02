import streamlit as st
from groq import Groq

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Asistente Virtual FAQ",
    page_icon="🤖",
    layout="centered"
)

# --- Título y Descripción ---
st.title("🤖 Chatbot de Atención al Cliente")
st.markdown("""
Este asistente responde automáticamente preguntas frecuentes sobre horarios, ubicación y requisitos.
""")

# --- Configuración de la Barra Lateral (Sidebar) ---
with st.sidebar:
    st.header("Configuración")
    # Entrada para la API Key (para seguridad en Streamlit Cloud)
    groq_api_key = st.text_input("Introduce tu Groq API Key:", type="password")
    st.markdown("[Obtener API Key gratis aquí](https://console.groq.com/keys)")
    
    st.divider()
    st.info("Modelo: "llama-3.3-70b (Via Groq)")

# --- BASE DE CONOCIMIENTO (Aquí centralizas la información) ---
# Puedes editar este texto para cambiar las respuestas del bot
CONOCIMIENTO_EMPRESA = """
Eres un asistente virtual amable y profesional para la empresa "Servicios Rápidos S.A.".
Tu objetivo es responder dudas basándote EXCLUSIVAMENTE en la siguiente información.
Si te preguntan algo que no está aquí, responde amablemente que deben llamar por teléfono.

INFORMACIÓN OFICIAL:
1. HORARIOS DE ATENCIÓN:
   - Lunes a Viernes: 09:00 AM a 18:00 PM (Horario continuado).
   - Sábados: 10:00 AM a 14:00 PM.
   - Domingos y Festivos: Cerrado.

2. UBICACIÓN:
   - Dirección: Av. Siempre Viva 742, Oficina 305, Ciudad Capital.
   - Referencia: Al lado de la estación de metro "Central", edificio azul.
   - Mapa: https://maps.google.com/?q=Av+Siempre+Viva+742

3. REQUISITOS PARA TRÁMITES:
   - Documento de Identidad vigente (Cédula o Pasaporte).
   - Comprobante de domicilio (no mayor a 3 meses).
   - Para empresas: Carpeta tributaria electrónica.

4. CONTACTO HUMANO:
   - Teléfono: +56 9 1234 5678
   - Email: contacto@serviciosrapidos.com

Instrucciones de tono: Sé breve, directo y cordial. Usa emojis ocasionalmente.
"""

# --- Inicializar Historial de Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Mostrar Mensajes Anteriores ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Lógica del Chat ---
if prompt := st.chat_input("Escribe tu pregunta aquí (ej: ¿A qué hora abren?)"):
    
    # 1. Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Verificar API Key
    if not groq_api_key:
        st.error("⚠️ Por favor, introduce tu API Key de Groq en la barra lateral para continuar.")
        st.stop()

    # 3. Generar respuesta con Groq
    try:
        client = Groq(api_key=groq_api_key)
        
        # Construimos el historial para enviarlo al modelo
        # Incluimos el "system prompt" con el conocimiento de la empresa
        messages_payload = [
            {"role": "system", "content": CONOCIMIENTO_EMPRESA}
        ]
        # Añadimos los últimos mensajes del chat para mantener contexto
        for msg in st.session_state.messages:
            messages_payload.append({"role": msg["role"], "content": msg["content"]})

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Modelo rápido y eficiente
            messages=messages_payload,
            temperature=0.5, # Baja temperatura para respuestas más precisas y menos creativas
            max_tokens=500,
            stream=True,
        )

        # 4. Mostrar respuesta en tiempo real (streaming)
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        
        # 5. Guardar respuesta en historial
        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:

        st.error(f"Ocurrió un error al conectar con Groq: {e}")



