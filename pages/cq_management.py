import streamlit as st
from PIL import Image
from menu import menu_with_redirect
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd

st.set_page_config(page_title="Gerência de Controle de Qualidade", layout="wide")
# Open an image file
img = Image.open('Logo_SFMR_Horizontal_Centralizado.png')
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

def proximo_teste(nome, data):
    periodicidade = lista_testes_gc_periodicidade[nome]
    if periodicidade == 'Mensal':
        return data + pd.DateOffset(months=1)
    elif periodicidade == 'Semestral':
        return data + pd.DateOffset(months=6)
    elif periodicidade == 'Anual':
        return data + pd.DateOffset(years=1)
    
tab1, tab2 = st.tabs(['Dashboard', 'Registrar Teste'])

with tab1:    
    teste_col = db['testes']
    testes = pd.DataFrame(list(teste_col.find({}, {'_id': 0})))
    st.dataframe(testes, hide_index=True, use_container_width=True)
with tab2:
    with st.form(key='insert_teste', clear_on_submit=True):
        teste = {}
        equipamentos_col = db['equipamentos']
        equipamentos = equipamentos_col.find({}, {'_id': 0, 'Identificação': 1})
        
        teste['Equipamento'] = st.selectbox('Equipamento', [equipamento['Identificação'] for equipamento in equipamentos])
        teste['Nome'] = st.selectbox('Nome do Teste', list(lista_testes_gc_periodicidade.keys()))
        teste['Data de realização'] = pd.to_datetime(st.date_input('Data de realização'), format='DD/MM/YYYY')
        teste['Data da próxima realização'] = proximo_teste(teste['Nome'], teste['Data de realização'])
        teste['Arquivado'] = False
        
        teste['Data de realização'] = teste['Data de realização'].strftime('%d/%m/%Y')
        teste['Data da próxima realização'] = teste['Data da próxima realização'].strftime('%d/%m/%Y')
        
        submit_button = st.form_submit_button(label='Inserir Teste')
        if submit_button:
            teste_col = db['testes']
            insert_status = teste_col.insert_one(teste)
            if insert_status.acknowledged:
                st.success('Teste inserido com sucesso!')
                st.rerun()

#collection.insert_one(teste)

# Convert the collection data to a DataFrame
# equipamentos_diagnostico = pd.DataFrame(list(collection.find()))

# st.dataframe(equipamentos_diagnostico)

client.close()