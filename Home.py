import streamlit as st
from menu import menu
from users_management import UsersManagement
    
user_management = UsersManagement()

user_management.login_widget()

if st.session_state["authentication_status"] is False:
    st.error('Usuário ou senha incorretos!')
 
# TODO: Implementar a funcionalidade de recuperação de senha e usuário com API do Gmail           
    # if 'forgot_password_clicked' not in st.session_state:
    #     st.session_state['forgot_password_clicked'] = False
    # if 'forgot_username_clicked' not in st.session_state:
    #     st.session_state['forgot_username_clicked'] = False
        
    # def forgot_password_button():
    #     st.session_state['forgot_password_clicked'] = True
    #     st.session_state['forgot_username_clicked'] = False
    # def forgot_username_button():
    #     st.session_state['forgot_username_clicked'] = True
    #     st.session_state['forgot_password_clicked'] = False
        
    # col1, col2 = st.columns([1, 3.4])
    
    # with col1:
    #     st.button('Esqueceu a senha?', type='primary', key='forgot_password', on_click=forgot_password_button)
    # if st.session_state['forgot_password_clicked'] and not st.session_state['forgot_username_clicked']:
    #     user_management.forgot_password_widget()
    # with col2:
    #     st.button('Esqueceu o usuário?', type='primary', key='forgot_username', on_click=forgot_username_button)
    # if st.session_state['forgot_username_clicked'] and not st.session_state['forgot_password_clicked']:
    #     user_management.forgot_username_widget()
    
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, preencha os campos de usuário e senha.')
else:
    st.write(f'# Bem-vindo, {st.session_state.name}!')

menu()