import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from users import Users
import time

# App

user_authentication = Users()

user_authentication.login_widget()

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
        user_authentication.forgot_password_widget()
    with col2:
        st.button('Esqueceu o usuário?', type='primary', key='forgot_username', on_click=forgot_username_button)
    if st.session_state['forgot_username_clicked'] and not st.session_state['forgot_password_clicked']:
        user_authentication.forgot_username_widget()
    
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, preencha os campos de usuário e senha.')
    
elif st.session_state["authentication_status"]:
    user_authentication.logout_widget()
    
############################################################################################################
# FOR SOME REASON THIS PART OF THE CODE HAS BLANK PAGE WHEN RUNNING LOCALLY
############################################################################################################
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Redefinir senha",
            "Registrar usuário",
            "Remover usuário",
            "Atualizar detalhes do usuário"
        ]
    )

    # Creating a password reset widget
    with tab1:
        user_authentication.reset_password_widget()

    # Creating a new user registration widget
    with tab2:
        user_authentication.new_user_widget()
        
    with tab3:
        user_authentication.remove_user_widget()

    # Creating an update user details widget
    with tab4:
        user_authentication.update_user_widget()
