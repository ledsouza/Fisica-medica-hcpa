import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time

def login_widget() -> tuple:
    
    # Opening the config file with the credentials
    with open(".streamlit/config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )

    # Creating a login widget
    try:
        authenticator.login(fields={"Username": "Usuário", "Password": "Senha"})
    except Exception as e:
        st.error(e)
        
    return authenticator, config

def forgot_password_widget(authenticator) -> None:
    try:
        (
            username_of_forgotten_password,
            email_of_forgotten_password,
            new_random_password,
        ) = authenticator.forgot_password(
            fields={
                "Form name": "Esqueci minha senha",
                "Username": "Usuário",
                "Submit": "Submeter",
            }
        )
        if username_of_forgotten_password:
            st.session_state['forgot_password_clicked'] = False
            st.success("Nova senha enviada por e-mail com sucesso!")
            time.sleep(1)
            st.rerun()
        elif username_of_forgotten_password == False:
            st.error("Usuário não encontrado")
    except Exception as e:
        st.error(e)
        
def forgot_username_widget(authenticator) -> None:
    try:
        username_of_forgotten_username, email_of_forgotten_username = (
            authenticator.forgot_username(
                fields={
                    "Form name": "Esqueci meu usuário",
                    "Email": "Email",
                    "Submit": "Submeter",
                }
            )
        )
        if username_of_forgotten_username:
            st.session_state['forgot_username_clicked'] = False
            st.success("Usuário enviado por e-mail com sucesso!")
            time.sleep(1)
            st.rerun()
        elif username_of_forgotten_username == False:
            st.error("Email não encontrado")
    except Exception as e:
        st.error(e)
        
def reset_password_widget(authenticator) -> None:
    try:
        if authenticator.reset_password(
            st.session_state["username"],
            fields={
                "Form name": "Redefinir senha",
                "Current password": "Senha atual",
                "New password": "Nova senha",
                "Repeat password": "Repetir senha",
                "Reset": "Redefinir",
            }
        ):
            st.success("Senha modificada com sucesso!")
    except Exception as e:
        st.error(e)
        
def new_user_widget(authenticator) -> None:
    try:
        (
            email_of_registered_user,
            username_of_registered_user,
            name_of_registered_user,
        ) = authenticator.register_user(
            preauthorization=False,
            domains=['@hcpa.edu.br'],
            fields={
                "Form name": "Registrar usuário",
                "Email": "Email",
                'Name': 'Nome',
                "Username": "Usuário",
                "Password": "Senha",
                "Repeat password": "Repetir senha",
                "Register": "Registrar",
            }
        )
        if email_of_registered_user:
            st.success("Usuário registrado com sucesso!")
    except Exception as e:
        st.error(e)
        
def update_user_widget(authenticator) -> None:
    try:
        if authenticator.update_user_details(
            st.session_state["username"],
            fields={
                "Form name": "Atualizar detalhes do usuário",
                "Field": "Campo",
                "Name": "Nome",
                "Email": "Email",
                "New value": "Novo valor",
                "Update": "Atualizar",
            },
        ):
            st.success("Campos atualizados com sucesso!")
    except Exception as e:
        st.error(e)