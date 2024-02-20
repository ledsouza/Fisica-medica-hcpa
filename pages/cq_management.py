import streamlit as st
from PIL import Image
from menu import menu_with_redirect
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import time
from data_processing.stylized_table import StylizedCQ

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

lista_testes_pet_periodicidade = {
    'Uniformidade e verificação da calibração do sistema PET-CT': 'Mensal',
    'Normalização e Calibração cruzada': 'Trimestral',
    'Resolução espacial': 'Semestral',
    'Sensibilidade': 'Semestral',
    'Corregistro das imagens de PET e CT': 'Semestral',
    '''Desempenho da taxa de contagens (NECR), 
    taxa de eventos aleatórios, espalhados e verdadeiros, 
    fração de espalhamento e 
    exatidão das correções de eventos aleatórios e de perda de contagens''': 'Anual',
    'Desempenho geral e exatidão das correções de atenuação e espalhamento': 'Anual',
}

def proximo_teste(nome, data):
    lista_testes_periodicidade = {**lista_testes_gc_periodicidade, **lista_testes_pet_periodicidade}
    periodicidade = lista_testes_periodicidade[nome]
    if periodicidade == 'Mensal':
        return data + pd.DateOffset(months=1)
    elif periodicidade == 'Trimestral':
        return data + pd.DateOffset(months=3)
    elif periodicidade == 'Semestral':
        return data + pd.DateOffset(months=6)
    elif periodicidade == 'Anual':
        return data + pd.DateOffset(years=1)
    
tab1, tab2 = st.tabs(['Dashboard', 'Registrar Teste'])

if 'teste_archivation' not in st.session_state:
    st.session_state.teste_archivation = False

def change_archive_status():
    st.session_state.teste_archivation = True

with tab1:    
    teste_col = db['testes']
    testes = pd.DataFrame(list(teste_col.find({}, {'_id': 0})))
    styler = StylizedCQ(testes)
    stylized_table = styler.stylized_testes()
    
    edited_df = st.data_editor(stylized_table, hide_index=True, use_container_width=True, on_change=change_archive_status, disabled=('Equipamento', 
                                                                                                    'Nome', 
                                                                                                    'Data de realização', 
                                                                                                    'Data da próxima realização'))
    
    if st.session_state.teste_archivation:
        st.session_state.teste_archivation = False
        
        diff = testes.compare(edited_df)
        
        # Drop the multi-index to make filtering easier
        diff.columns = diff.columns.droplevel(0)
        
        # Get the indices of the rows with differences
        diff_indices = diff[diff['self'].notna() | diff['other'].notna()].index
        
        # Get the entire rows from the original dataframe
        diff_rows = testes.loc[diff_indices]
        query = diff_rows.drop(columns='Arquivado')
        query['Data da próxima realização'] = query['Data da próxima realização'].dt.strftime('%d/%m/%Y')
        query = query.to_dict('records')
        
        # Get only the archivation status with differences
        diff_value = diff['other']
        archived_status = {'Arquivado': diff_value.values[0]}
        
        update_status = teste_col.update_one(query[0], {'$set': archived_status})
        if update_status.matched_count > 0:
            st.success('Status de arquivamento atualizado com sucesso!')
            time.sleep(1)
            st.rerun()
        else:
            st.error('Erro ao atualizar o status de arquivamento!')

        
    
with tab2:
    teste = {}
    equipamentos_col = db['equipamentos']
    equipamentos = equipamentos_col.find({}, {'_id': 0, 'Identificação': 1})
    
    with st.container(border=True):
    
        teste['Equipamento'] = st.selectbox('Equipamento', [equipamento['Identificação'] for equipamento in equipamentos])
        
        with st.form(key='register_test', clear_on_submit=True, border=False):
            
            if teste['Equipamento'] in ['FMMNINFINIA', 'FMMNMILLENNIUM', 'FMMNVENTRI']:
                teste['Nome'] = st.selectbox('Nome do Teste', list(lista_testes_gc_periodicidade.keys()))
            elif teste['Equipamento'] == 'FMMNPETCT':
                teste['Nome'] = st.selectbox('Nome do Teste', list(lista_testes_pet_periodicidade.keys()))
            
            teste['Data de realização'] = pd.to_datetime(st.date_input('Data de realização'), format='DD/MM/YYYY')
            
            submit_button = st.form_submit_button(label='Inserir Teste')
            if submit_button:
                teste['Data da próxima realização'] = proximo_teste(teste['Nome'], teste['Data de realização'])
                teste['Arquivado'] = False
                
                teste['Data de realização'] = teste['Data de realização'].strftime('%d/%m/%Y')
                teste['Data da próxima realização'] = teste['Data da próxima realização'].strftime('%d/%m/%Y')
                
                teste_col = db['testes']
                insert_status = teste_col.insert_one(teste)
                if insert_status.acknowledged:
                    st.success('Teste inserido com sucesso!')
                    time.sleep(1)
                    st.rerun()

#collection.insert_one(teste)

# Convert the collection data to a DataFrame
# equipamentos_diagnostico = pd.DataFrame(list(collection.find()))

# st.dataframe(equipamentos_diagnostico)

client.close()