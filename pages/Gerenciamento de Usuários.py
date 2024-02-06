import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from users import login_widget, forgot_password_widget, forgot_username_widget, reset_password_widget, new_user_widget, update_user_widget
import time

# App
authenticator, config = login_widget()

if st.session_state["authentication_status"] is False:
    st.error('Usuário ou senha incorretos!')
    
    if 'forgot_password_clicked' not in st.session_state:
        st.session_state['forgot_password_clicked'] = False
    if 'forgot_username_clicked' not in st.session_state:
        st.session_state['forgot_username_clicked'] = False
        
    def forgot_password_button():
        st.session_state['forgot_password_clicked'] = True
        st.session_state['forgot_username_clicked'] = False
    def forgot_username_button():
        st.session_state['forgot_username_clicked'] = True
        st.session_state['forgot_password_clicked'] = False
        
    col1, col2 = st.columns([1, 3.4])
    
    with col1:
        st.button('Esqueceu a senha?', type='primary', key='forgot_password', on_click=forgot_password_button)
    if st.session_state['forgot_password_clicked'] and not st.session_state['forgot_username_clicked']:
        forgot_password_widget(authenticator)
    with col2:
        st.button('Esqueceu o usuário?', type='primary', key='forgot_username', on_click=forgot_username_button)
    if st.session_state['forgot_username_clicked'] and not st.session_state['forgot_password_clicked']:
        forgot_username_widget(authenticator)
    
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, preencha os campos de usuário e senha.')
    
elif st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")
    
    st.write('Usuário autenticado com sucesso!')
    
    reset_password, new_user, update_user = st.tabs(
        [
            "Redefinir senha",
            "Registrar usuário",
            "Atualizar detalhes do usuário"
        ]
    )

    # Creating a password reset widget
    with reset_password:
        reset_password_widget(authenticator)

    # Creating a new user registration widget
    with new_user:
        new_user_widget(authenticator)

    # Creating an update user details widget
    with update_user:
        update_user_widget(authenticator)

    # # Saving config file
    # with open(".streamlit/config.yaml", "w") as file:
    #     yaml.dump(config, file, default_flow_style=False)
