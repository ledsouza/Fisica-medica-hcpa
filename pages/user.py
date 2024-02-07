import streamlit as st
from menu import menu_with_redirect

# Redirect to app.py if not logged in, otherwise show the navigation menu
st.write(st.session_state)

menu_with_redirect()

st.title("This page is available to all users")
st.markdown(f"Bem vindo {st.session_state.username}.")