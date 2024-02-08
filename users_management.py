import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time
import os
import logging
import boto3
from botocore.exceptions import ClientError

class UsersManagement:
    def __init__(self):
        self.config = self._open_config()
        self.config_name = 'config.yaml'
        self.bucket = 'fisica-medica-hcpa'
        self.authenticator = self._build_authenticator()
        
        st.session_state['user_management'] = self
        os.environ["AWS_ACCESS_KEY_ID"] = st.secrets['s3_credentials']['access_key']
        os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets['s3_credentials']['secret_key']
        os.environ['AWS_DEFAULT_REGION'] = st.secrets['s3_credentials']['region']
        
    def _open_config(self) -> dict:
        s3 = boto3.client('s3')
        s3.download_file('fisica-medica-hcpa', 'config.yaml', 'config.yaml')
        
        with open("config.yaml") as file:
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
                _,
                _,
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
        if st.session_state['username'] == None:
            pass
        else:
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
                    upload_status = self._save_config()
                    if upload_status:
                        st.success("Senha modificada com sucesso!")
                    else:
                        st.error("Erro ao modificar senha")
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
                _,
                _,
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
                upload_status = self._save_config()
                if upload_status:
                    st.success("Usuário registrado com sucesso!")
                else:
                    st.error("Erro ao registrar usuário")
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
        if st.session_state['username'] == None:
            pass
        else:
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
                    upload_status = self._save_config()
                    if upload_status:
                        st.success("Campos atualizados com sucesso!")
                    else:
                        st.error("Erro ao atualizar campos")
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
            upload_status = self._save_config()
            if upload_status:
                st.success('Usuário removido com sucesso!')
            else:
                st.error('Erro ao remover usuário')
            
    def remove_user_widget(self) -> None:   
        with st.form('remove_user'):
            st.write('### Remover usuário')
            username = st.text_input('Usuário')
            st.form_submit_button('Remover', on_click=self._remove_user_submit, args=(username,))
            
    def _upload_file(self):
        """Upload a file to an S3 bucket
        :return: True if file was uploaded, else False
        """

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(self.config_name, self.bucket, self.config_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True
            
    def _save_config(self) -> bool:
        with open("config.yaml", "w") as file:
            yaml.dump(self.config, file, default_flow_style=False)
            
        upload_status = self._upload_file()
        return upload_status