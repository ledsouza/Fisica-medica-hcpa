import streamlit as st
from PIL import Image
from menu import menu_with_redirect

st.set_page_config(page_title="Análise de Dados do BI", layout="wide")
# Open an image file
img = Image.open('logos\Logo_SFMR_Horizontal_Centralizado.png')
st.sidebar.image(img, use_column_width=True)

menu_with_redirect()