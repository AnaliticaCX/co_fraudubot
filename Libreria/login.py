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

        .stTextInput > div > div > input {
            background-color: #ffffff;
            color: #333;
            border-radius: 8px;
            padding: 10px;
        }

        .stButton > button {
            background-color: #566ad1;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
        }
    </style>
""", unsafe_allow_html=True)
    logo = Image.open("img/logo_fraudubot.png")
    col1, col2, col3 = st.columns([4, 4, 4])
    with col2:
        st.image(logo, use_container_width=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ##st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("""
    <h1 style='text-align: center; color: #6A95FA; font-size: 1.5em; font-weight: 600;'>
        Bienvenido
    </h1>
    <p style='text-align: center; color: #A9A9A9; font-size: 1.1em;'>
        Por favor, ingresa tus credenciales para continuar
    </p>
""", unsafe_allow_html=True)
        ##st.title("Iniciar Sesión")
        correo = st.text_input("Correo")
        contrasena = st.text_input("Contraseña", type="password")
        login_boton = st.button("Ingresar")
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