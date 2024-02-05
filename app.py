import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('.streamlit/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Creating a login widget
try:
    authenticator.login(fields={'Username': 'Usuário', 'Password': 'Senha'})
except Exception as e:
    st.error(e)

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar')
    
elif st.session_state["authentication_status"] == False:
    st.error('Usuário ou senha incorreto')
elif st.session_state["authentication_status"] == None:
    st.warning('Por favor, insira o usuário e a senha')

# Creating a password reset widget
if st.session_state["authentication_status"]:
    try:
        if authenticator.reset_password(st.session_state["username"], fields={
            'Form name': 'Redefinir senha',
            'Current password': 'Senha atual',
            'New password': 'Nova senha',
            'Repeat password': 'Repetir senha',
            'Reset': 'Redefinir'
        }):
            st.success('Senha modificada com sucesso!')
    except Exception as e:
        st.error(e)

# Creating a new user registration widget
try:
    email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(preauthorization=False, fields={
        'Form name': 'Registrar usuário', 
        'Email': 'Email',
        'Username': 'Usuário',
        'Password': 'Senha',
        'Repeat password': 'Repetir senha',
        'Register': 'Registrar'
    })
    if email_of_registered_user:
        st.success('Usuário registrado com sucesso!')
except Exception as e:
    st.error(e)

# Creating a forgot password widget
try:
    username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password()
    if username_of_forgotten_password:
        st.success('New password sent securely')
        # Random password to be transferred to the user securely
    elif username_of_forgotten_password == False:
        st.error('Username not found')
except Exception as e:
    st.error(e)

# Creating a forgot username widget
try:
    username_of_forgotten_username, email_of_forgotten_username = authenticator.forgot_username()
    if username_of_forgotten_username:
        st.success('Username sent securely')
        # Username to be transferred to the user securely
    elif username_of_forgotten_username == False:
        st.error('Email not found')
except Exception as e:
    st.error(e)

# Creating an update user details widget
if st.session_state["authentication_status"]:
    try:
        if authenticator.update_user_details(st.session_state["username"]):
            st.success('Entries updated successfully')
    except Exception as e:
        st.error(e)

# Saving config file
with open('.streamlit/config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)
