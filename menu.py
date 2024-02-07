import streamlit as st

def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("Home.py", label="Alterar conta")
    st.sidebar.page_link("pages/user.py", label="Seu perfil")
    if st.session_state.username in st.session_state.authenticated_usernames:
        st.sidebar.page_link("pages/Gerenciamento de Usuários.py", label="Gerenciamento de Usuários")
        st.sidebar.page_link("pages/Tratamento de Dados do BI.py", label="Tratamento de Dados do BI")
        st.session_state['authenticator'].logout_widget()


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("Home.py", label="Log in")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "username" not in st.session_state or st.session_state.username is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "username" not in st.session_state or st.session_state.username  None:
        st.switch_page("Home.py")
    menu()