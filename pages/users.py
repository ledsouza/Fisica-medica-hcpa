import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from users_management import UsersManagement
import time
from menu import menu

menu()
    
############################################################################################################
# ! FOR SOME REASON THIS PART OF THE CODE HAS BLANK PAGE WHEN RUNNING LOCALLY
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
    st.session_state.user_management.reset_password_widget()

# Creating a new user registration widget
with tab2:
    st.session_state.user_management.new_user_widget()

# Creating a remove user widget    
with tab3:
    st.session_state.user_management.remove_user_widget()

# Creating an update user details widget
with tab4:
    st.session_state.user_management.update_user_widget()
