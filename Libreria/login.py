import streamlit as st
from PIL import Image

USUARIOS = {
    "zcamposc@celerix.com": {"nombre": "Zuly Campos", "contrasena": "1234"},
    "admin": {"nombre": "Administrador", "contrasena": "adminpass"}
}

def login():
    st.markdown("""
    <style>
        /* Fondo de toda la aplicación */
        .stApp {
            background-color: #ffffff;
        }

        .login-box {
            max-width: 400px;
            margin: auto;
            padding: 30px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }

        /* Fix input text and cursor color */
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            caret-color: #000000 !important;
            border: 1px solid #ccc !important;
        }

        /* Fix password input */
        input[type="password"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            caret-color: #000000 !important;
            border: 1px solid #ccc !important;
        }

        /* Fix input labels */
        .stTextInput > label {
            color: #000000 !important;
        }

        .stButton > button {
            background-color: #566ad1 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
        }

        /* Login form specific styling */
        .login-form input {
            color: #000000 !important;
            background-color: #ffffff !important;
            caret-color: #000000 !important;
        }
        
        .login-form label {
            color: #000000 !important;
        }

        /* Force all input elements to have black cursor and text */
        input, textarea {
            color: #000000 !important;
            caret-color: #000000 !important;
        }

        /* Specific targeting for email and password inputs */
        input[type="email"], input[type="text"] {
            color: #000000 !important;
            background-color: #ffffff !important;
            caret-color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)
    
    logo = Image.open("img/logo_fraudubot.png")
    col1, col2, col3 = st.columns([4, 4, 4])
    with col2:
        st.image(logo, use_container_width=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <h1 style='text-align: center; color: #000000; font-size: 1.5em; font-weight: 600;'>
            Bienvenido
        </h1>
        <p style='text-align: center; color: #000000; font-size: 1.1em;'>
            Por favor, ingresa tus credenciales para continuar
        </p>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            correo = st.text_input("📧 Correo electrónico")
            contrasena = st.text_input("🔒 Contraseña", type="password")
            login_boton = st.form_submit_button("Ingresar")
            st.markdown('</div>', unsafe_allow_html=True)

    if login_boton:
        if correo in USUARIOS and USUARIOS[correo]["contrasena"] == contrasena:
            st.session_state["logueado"] = True
            st.session_state["usuario"] = USUARIOS[correo]["nombre"]
            st.rerun()
        else:
            st.error("Correo o contraseña incorrectos")

def verificar_login():
    if "logueado" not in st.session_state:
        st.session_state["logueado"] = False
    if not st.session_state["logueado"]:
        login()
        st.stop()