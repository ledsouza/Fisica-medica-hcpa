import streamlit as st
from menu import menu
from users_management import UsersManagement
    
user_management = UsersManagement()
user_management.login_widget()

menu()