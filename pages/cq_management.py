import streamlit as st
from PIL import Image
from menu import menu_with_redirect
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests
import pandas as pd

st.set_page_config(page_title="Gerência de Controle de Qualidade", layout="wide")
# Open an image file
img = Image.open('logos\Logo_SFMR_Horizontal_Centralizado.png')
st.sidebar.image(img, use_column_width=True)

menu_with_redirect()

uri = f"mongodb+srv://ledsouza:{os.getenv('MONGODB_PASSWORD')}@mnmanagement.opks2ne.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client['cq_gestao']
collection = db['testes']

lista_testes_gc_periodicidade = {
    'Uniformidade intrínseca para alta densidade de contagem': 'Mensal',
    'Resolução e linearidade espacial intrínseca': 'Mensal',
    'Centro de rotação': 'Mensal',
    'Resolução energética': 'Semestral',
    'Taxa máxima de contagem': 'Semestral',
    'Resolução espacial para fontes multi-energética': 'Semestral',
    'Corregistro espacial para fontes multi-energéticas': 'Semestral',
    'Sensibilidade planar': 'Semestral',
    'Uniformidade extrínseca para alta densidade de contagem': 'Semestral',
    'Velocidade da mesa em varreduras de corpo inteiro': 'Semestral',
    'Desempenho geral SPECT': 'Semestral',
    'Uniformidade para nuclídeos diferentes de Tc-99m': 'Anual',
    'Uniformidade intrínseca com janelas energéticas assimétricas': 'Anual',
    'Resolução e linearidade espacial extrínseca': 'Anual'
}

teste = {
    'Nome': 'Centro de Rotação',
    'Identificação': 'GC 1',
    'Data da Realização': '14/02/2024',
    'Data da Próxima Realização': '14/03/2024',
    'Arquivado': 'false'
}

#collection.insert_one(teste)

# Convert the collection data to a DataFrame
# equipamentos_diagnostico = pd.DataFrame(list(collection.find()))

# st.dataframe(equipamentos_diagnostico)

client.close()