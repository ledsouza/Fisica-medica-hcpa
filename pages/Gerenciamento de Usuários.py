import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

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
    authenticator.logout("Logout", "sidebar")
except Exception as e:
    st.error(e)
    
if st.session_state["authentication_status"]:
    reset_password, new_user, forgot_password, forgot_username, update_user = st.tabs(
        [
            "Redefinir senha",
            "Registrar usuário",
            "Esqueci minha senha",
            "Esqueci meu usuário",
            "Atualizar detalhes do usuário"
        ]
    )

    with reset_password:
        # Creating a password reset widget
        if st.session_state["authentication_status"]:
            try:
                if authenticator.reset_password(
                    st.session_state["username"],
                    fields={
                        "Form name": "Redefinir senha",
                        "Current password": "Senha atual",
                        "New password": "Nova senha",
                        "Repeat password": "Repetir senha",
                        "Reset": "Redefinir",
                    },
                ):
                    st.success("Senha modificada com sucesso!")
            except Exception as e:
                st.error(e)

    with new_user:
        # Creating a new user registration widget
        try:
            (
                email_of_registered_user,
                username_of_registered_user,
                name_of_registered_user,
            ) = authenticator.register_user(
                preauthorization=False,
                fields={
                    "Form name": "Registrar usuário",
                    "Email": "Email",
                    "Username": "Usuário",
                    "Password": "Senha",
                    "Repeat password": "Repetir senha",
                    "Register": "Registrar",
                },
            )
            if email_of_registered_user:
                st.success("Usuário registrado com sucesso!")
        except Exception as e:
            st.error(e)

    with forgot_password:
        # Creating a forgot password widget
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
                st.success("Nova senha enviada com sucesso!")
                # Random password to be transferred to the user securely
            elif username_of_forgotten_password == False:
                st.error("Usuário não encontrado")
        except Exception as e:
            st.error(e)

    with forgot_username:
        # Creating a forgot username widget
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
                st.success("Usuário enviado com sucesso!")
                # Username to be transferred to the user securely
            elif username_of_forgotten_username == False:
                st.error("Email não encontrado")
        except Exception as e:
            st.error(e)

    # Creating an update user details widget
    with update_user:
        if st.session_state["authentication_status"]:
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

    # Saving config file
    with open(".streamlit/config.yaml", "w") as file:
        yaml.dump(config, file, default_flow_style=False)
