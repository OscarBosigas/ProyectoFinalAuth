import streamlit as st

from streamlit_option_menu import option_menu

import home, about, account

st.set_page_config(
        page_title="INVOICIFY",
)

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        with st.sidebar:        
            app = option_menu(
                menu_title='INVOICIFY ',
                options=['Cuenta','Principal', 'Analisis', 'Acerca de'],
                icons=['person-circle','house-fill','trophy-fill','chat-fill'],
                menu_icon='chat-text-fill',
                default_index=1,
                styles={
                    "container": {"padding": "5!important","background-color":'black'},
        "icon": {"color": "white", "font-size": "23px"}, 
        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
        "nav-link-selected": {"background-color": "#02ab21"},}
                
                )

        
        if app == "Principal":
            home.app()
        if app == "Acerca de":
            about.app()   
        if app == "Cuenta":
            account.app()
        
                        
    run()            
         