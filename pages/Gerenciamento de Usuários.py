import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Functions
def login_widget() -> None:
    
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
    st.session_state['authenticator'] = authenticator
    st.session_state['config'] = config

    # Creating a login widget
    try:
        authenticator.login(fields={"Username": "Usuário", "Password": "Senha"})
        authenticator.logout("Logout", "sidebar")
    except Exception as e:
        st.error(e)

# App
login_widget()
    
if st.session_state["authentication_status"]:
    reset_password, new_user, update_user = st.tabs(
        [
            "Redefinir senha",
            "Registrar usuário",
            "Atualizar detalhes do usuário"
        ]
    )

    # Creating a password reset widget
    with reset_password:
        if st.session_state["authentication_status"]:
            try:
                if st.session_state['authenticator'].reset_password(
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

    # Creating a new user registration widget
    with new_user:
        try:
            (
                email_of_registered_user,
                username_of_registered_user,
                name_of_registered_user,
            ) = st.session_state['authenticator'].register_user(
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

    # # Creating a forgot password widget
    # with forgot_password:
    #     try:
    #         (
    #             username_of_forgotten_password,
    #             email_of_forgotten_password,
    #             new_random_password,
    #         ) = st.session_state['authenticator'].forgot_password(
    #             fields={
    #                 "Form name": "Esqueci minha senha",
    #                 "Username": "Usuário",
    #                 "Submit": "Submeter",
    #             }
    #         )
    #         if username_of_forgotten_password:
    #             st.success("Nova senha enviada por e-mail com sucesso!")
    #             # Random password to be transferred to the user securely
    #         elif username_of_forgotten_password == False:
    #             st.error("Usuário não encontrado")
    #     except Exception as e:
    #         st.error(e)

    # # Creating a forgot username widget
    # with forgot_username:
    #     try:
    #         username_of_forgotten_username, email_of_forgotten_username = (
    #             st.session_state['authenticator'].forgot_username(
    #                 fields={
    #                     "Form name": "Esqueci meu usuário",
    #                     "Email": "Email",
    #                     "Submit": "Submeter",
    #                 }
    #             )
    #         )
    #         if username_of_forgotten_username:
    #             st.success("Usuário enviado por e-mail com sucesso!")
    #             # Username to be transferred to the user securely
    #         elif username_of_forgotten_username == False:
    #             st.error("Email não encontrado")
    #     except Exception as e:
    #         st.error(e)

    # Creating an update user details widget
    with update_user:
        if st.session_state["authentication_status"]:
            try:
                if st.session_state['authenticator'].update_user_details(
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
        yaml.dump(st.session_state['config'], file, default_flow_style=False)
