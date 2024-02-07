import streamlit as st
from menu import menu
from users_management import UsersManagement

# Initialize st.session_state
if "username" not in st.session_state:
    st.session_state.username = None
if "authenticated_usernames" not in st.session_state:
    st.session_state.authenticated_usernames = None
    
user_management = UsersManagement()
user_management.login_widget()

menu()