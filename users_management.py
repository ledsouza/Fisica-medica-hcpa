import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time

class UsersManagement:
    def __init__(self):
        self.config = self._open_config()
        self.authenticator = self._build_authenticator()
        st.session_state['user_management'] = self
        
    def _open_config(self) -> dict:
        with open(".streamlit/config.yaml") as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config
    
    def _build_authenticator(self) -> stauth.Authenticate:
        authenticator = stauth.Authenticate(
            self.config["credentials"],
            self.config["cookie"]["name"],
            self.config["cookie"]["key"],
            self.config["cookie"]["expiry_days"],
            self.config["preauthorized"],
        )
        return authenticator

    def login_widget(self) -> None:
        try:
            self.authenticator.login(fields={"Form name": "Log in","Username": "Usuário", "Password": "Senha"})
        except Exception as e:
            st.error(e)
            
    def logout_widget(self) -> None:
        try:
            self.authenticator.logout("Log out", "sidebar")
        except Exception as e:
            st.error(e)

    def forgot_password_widget(self) -> None:
        try:
            (
                username_of_forgotten_password,
                email_of_forgotten_password,
                new_random_password,
            ) = self.authenticator.forgot_password(
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
        
    def forgot_username_widget(self) -> None:
        try:
            username_of_forgotten_username, email_of_forgotten_username = (
                self.authenticator.forgot_username(
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
        
    def reset_password_widget(self) -> None:
        try:
            if self.authenticator.reset_password(
                st.session_state["username"],
                fields={
                    "Form name": "Redefinir senha",
                    "Current password": "Senha atual",
                    "New password": "Nova senha",
                    "Repeat password": "Repetir senha",
                    "Reset": "Redefinir",
                }
            ):
                self.save_config()
                st.success("Senha modificada com sucesso!")
        except Exception as e:
            error_messages = {
                "Password/repeat password fields cannot be empty": "Senha e repetição de senha não podem estar vazios!",
                "Passwords do not match": "Senhas não coincidem!",
                "Current password is incorrect": "Senha atual incorreta!"
            }
            error_message = error_messages.get(str(e), str(e))
            st.error(error_message)
        
    def new_user_widget(self) -> None:
        try:
            (
                email_of_registered_user,
                username_of_registered_user,
                name_of_registered_user,
            ) = self.authenticator.register_user(
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
                self.save_config()
                st.success("Usuário registrado com sucesso!")
        except Exception as e:
            error_messages = {
                    "Password/repeat password fields cannot be empty": "Senha e repetição de senha não podem estar vazios!",
                    "Passwords do not match": "Senhas não coincidem!",
                    "Email is not valid": "Email não é válido!",
                    "Email already taken": "Email já registrado!",
                    "Username is not valid": "Usuário não é válido!",
                    "Name is not valid": "Nome não é válido!",
                    "Email not allowed to register": "Email não permitido para registro!"
                }
            error_message = error_messages.get(str(e), str(e))
            st.error(error_message)
        
    def update_user_widget(self) -> None:
        try:
            if self.authenticator.update_user_details(
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
                self.save_config()
                st.success("Campos atualizados com sucesso!")
        except Exception as e:
            error_messages = {
                    "Field cannot be empty": "Campo não pode estar vazio!",
                    "New value not provided": "Novo valor não fornecido!",
                    "Email is not valid": "Email não é válido!",
                    "Email already taken": "Email já registrado!",
                    "Name is not valid": "Nome não é válido!",
                    "New and current values are the same": "Novo e valor atual são iguais!"
                }
            error_message = error_messages.get(str(e), str(e))
            st.error(error_message)
            
    def _remove_user_submit(self, username: str) -> None:
        if username is None:
            st.error('Usuário não pode estar vazio')
        elif username not in self.config['credentials']['usernames']:
            st.error('Usuário não encontrado')
        else:
            del self.config['credentials']['usernames'][username]
            self.save_config()
            st.success('Usuário removido com sucesso!')
            
    def remove_user_widget(self) -> None:   
        with st.form('remove_user'):
            st.write('### Remover usuário')
            username = st.text_input('Usuário')
            st.form_submit_button('Remover', on_click=self._remove_user_submit, args=(username,))
            
    def save_config(self) -> None:
        with open(".streamlit/config.yaml", "w") as file:
            yaml.dump(self.config, file, default_flow_style=False)