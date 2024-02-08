import streamlit as st
from users_management import UsersManagement

def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("Home.py", label="Alterar conta")
    if st.session_state.authentication_status == True:
        st.sidebar.page_link("pages/users.py", label="Gerenciamento de Usuários")
        st.sidebar.page_link("pages/bi_data.py", label="Tratamento de Dados do BI")
        st.session_state['user_management'].logout_widget()


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("Home.py", label="Log in")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "authentication_status" not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "authentication_status" not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
        st.switch_page("Home.py")
    menu()