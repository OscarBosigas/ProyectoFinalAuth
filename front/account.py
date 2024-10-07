import streamlit as st

def app():

    st.title("Bienvenido a :violet[INVOICIFY]")

    choice = st.selectbox('Iniciar Sesión / Registrarse',['Iniciar Sesión','Registrarse'])

    if choice == 'Iniciar Sesión':
        email = st.text_input('Correo')
        password = st.text_input('Contraseña',type='password')
        st.button('Iniciar Sesión')

    else:
        email = st.text_input('Correo')
        password = st.text_input('Contraseña',type='password')
        username = st.text_input('Nombre de usuario')
        st.button('Crear cuenta')