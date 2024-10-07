import streamlit as st

from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("invoicify-b8370-firebase-adminsdk-p5sbi-d92d20e560.json")
#firebase_admin.initialize_app(cred)


def app():

    st.title("Bienvenido a :violet[INVOICIFY]")

    choice = st.selectbox('Iniciar Sesión / Registrarse',['Iniciar Sesión','Registrarse'])

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    def f():
        try:
            user = auth.get_user_by_email(email)
            st.session_state.useremail = user.uid
            st.session_state.username = user.email
            st.write('Exito')
        except:
            st.warning('Credenciales incorrectas')

    if choice == 'Iniciar Sesión':
        email = st.text_input('Correo')
        password = st.text_input('Contraseña',type='password')
        st.button('Iniciar Sesión', on_click=f)

    else:
        email = st.text_input('Correo')
        password = st.text_input('Contraseña',type='password')
        username = st.text_input('Nombre de usuario')
        if st.button('Crear cuenta'):
            user = auth.create_user(email = email, password = password, uid = username)
            st.success('Cuenta creada correctamente')
            st.markdown('Por favor ingresa usando tu correo y contraseña')
            st.balloons()