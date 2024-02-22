import streamlit as st
from PIL import Image
from menu import menu_with_redirect
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import time
from data_processing.stylized_table import StylizedCQ
from forms import FormMongoDB
from datetime import datetime

list_tests_gc_periodicity = {
    'Uniformidade intrínseca para alta densidade de contagem': 'Mensal',
    'Resolução e linearidade espacial intrínseca': 'Mensal',
    'Centro de rotação LEHR': 'Mensal',
    'Centro de rotação MEGP': 'Mensal',
    'Centro de rotação HEGP': 'Mensal',
    'Resolução energética Tc-99m': 'Semestral',
    'Resolução energética Tl-201': 'Semestral',
    'Resolução energética Ga-67': 'Semestral',
    'Resolução energética I-131': 'Semestral',
    'Taxa máxima de contagem': 'Semestral',
    'Resolução espacial íntriseca para fontes multi-energética I-131': 'Semestral',
    'Resolução espacial íntriseca para fontes multi-energética Ga-67': 'Semestral',
    'Resolução espacial íntriseca para fontes multi-energética Tl-201': 'Semestral',
    'Corregistro espacial para fontes multi-energéticas Ga-67': 'Semestral',
    'Corregistro espacial para fontes multi-energéticas Tl-201': 'Semestral',
    'Sensibilidade planar Tc-99m': 'Semestral',
    'Sensibilidade planar Ga-67': 'Semestral',
    'Sensibilidade planar I-131': 'Semestral',
    'Sensibilidade planar Tl-201': 'Semestral',
    'Uniformidade extrínseca para alta densidade de contagem LEHR': 'Semestral',
    'Uniformidade extrínseca para alta densidade de contagem MEGP': 'Semestral',
    'Uniformidade extrínseca para alta densidade de contagem HEGP': 'Semestral',
    'Verificação da angulação dos furos LEHR': 'Semestral',
    'Verificação da angulação dos furos MEGP': 'Semestral',
    'Verificação da angulação dos furos HEGP': 'Semestral',
    'Velocidade da mesa em varreduras de corpo inteiro': 'Semestral',
    'Desempenho geral da câmara SPECT': 'Semestral',
    'Uniformidade íntrinseca para I-131': 'Anual',
    'Uniformidade íntrinseca para Ga-67': 'Anual',
    'Uniformidade íntrinseca para Tl-201': 'Anual',
    'Uniformidade intrínseca com janelas energéticas assimétricas': 'Anual',
    'Resolução e linearidade espacial extrínseca LEHR': 'Anual',
    'Resolução e linearidade espacial extrínseca MEGP': 'Anual',
    'Resolução e linearidade espacial extrínseca HEGP': 'Anual'
}

st.set_page_config(page_title="Gerência de Controle de Qualidade", layout="wide")
# Open an image file
img = Image.open('Logo_SFMR_Horizontal_Centralizado.png')
st.sidebar.image(img, use_column_width=True)

menu_with_redirect()

uri = f"mongodb+srv://ledsouza:{os.getenv('MONGODB_PASSWORD')}@mnmanagement.opks2ne.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), maxIdleTimeMS=60000*10)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client['cq_gestao']
    
indicadores, panorama_ano, arquivamento, registrar_teste, remover_teste = st.tabs(['Indicadores',
                                                                                   'Panorama do ano',
                                                                                   'Arquivamento',
                                                                                   'Registrar teste',
                                                                                   'Remover teste'])

with indicadores:
    collection = db['testes']
    
    col1, col2 = st.columns(2)
    
    with col1:
        years = collection.find().distinct('Data da próxima realização')
        years = set([year[-4:] for year in years])
        years = sorted(years, reverse=True)
        year = st.selectbox('Selecione o ano', years)
    
    with col2:
        months = {
            'Janeiro': '01',
            'Feveiro': '02',
            'Março': '03',
            'Abril': '04',
            'Maio': '05',
            'Junho': '06',
            'Julho': '07',
            'Agosto': '08',
            'Setembro': '09',
            'Outubro': '10',
            'Novembro': '11',
            'Dezembro': '12'
        }
        months_key = st.selectbox('Selecione o mês', months.keys())
        month = months[months_key]
    
    pattern = '^\d{2}/' + f'{month}/{year}$'
    docs = collection.find({'Data da próxima realização': {'$regex': pattern}}, {'_id': 0, 'Equipamento': 1, 'Nome': 1, 'Data da próxima realização': 1})
    year = f'[{int(year[-1]) - 1}-9]'
    tests_done = pd.DataFrame()
    for doc in docs:
        pattern = '^\d{2}/\d{2}/202' + f'{year}$'
        data_da_proxima_realizacao = doc.pop('Data da próxima realização')
        data_de_realizacao = {'Data de realização': {'$regex': pattern}}
        query = {**doc, **data_de_realizacao}
        result = collection.find(query, {'_id': 0, 'Data da próxima realização': 0})
        test_done = pd.DataFrame(list(result))
        try:
            test_done['Data de realização'] = pd.to_datetime(test_done['Data de realização'], format='%d/%m/%Y')
            test_done.sort_values(by='Data de realização', ascending=False, inplace=True)
            test_done['Data da próxima realização'] = data_da_proxima_realizacao
            test_done['Data da próxima realização'] = pd.to_datetime(test_done['Data da próxima realização'], format='%d/%m/%Y')
            test_done['Diferença data'] = (test_done['Data da próxima realização'] - test_done['Data de realização']).dt.days
            test_done['how_to_due'] = (test_done['Data da próxima realização'] - datetime.now()).dt.days
            test_done['how_long_done'] = (datetime.now() - test_done['Data de realização'])
            # if list_tests_gc_periodicity[doc['Nome']] == 'Mensal':
            #     if test_done['Diferença data'] > pd.Timedelta(month=1):
            #         tests_done = pd.concat([tests_done, test_done.iloc[[0]]])
            # elif list_tests_gc_periodicity[doc['Nome']] == 'Trimestral':
            #     if test_done['Diferença data'] > pd.Timedelta(month=3):
            #         tests_done = pd.concat([tests_done, test_done.iloc[[0]]])
            # elif list_tests_gc_periodicity[doc['Nome']] == 'Semestral':
            #     if test_done['Diferença data'] > pd.Timedelta(month=6):
            #         tests_done = pd.concat([tests_done, test_done.iloc[[0]]])
            # elif list_tests_gc_periodicity[doc['Nome']] == 'Anual':
            #     if test_done['Diferença data'] > pd.Timedelta(year=1):
            #         tests_done = pd.concat([tests_done, test_done.iloc[[0]]])
            tests_done = pd.concat([tests_done, test_done.iloc[[0]]])
        except:
            continue
    
    st.dataframe(tests_done)
    

if 'teste_archivation' not in st.session_state:
    st.session_state.teste_archivation = False

def change_archive_status():
    st.session_state.teste_archivation = True

with arquivamento:    
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
        query['Data de realização'] = query['Data de realização'].dt.strftime('%d/%m/%Y')
        query = query.to_dict('records')
        
        # Get only the archivation status with differences
        diff_value = diff['other']
        archived_status = {'Arquivado': diff_value.values[0]}
        
        update_status = teste_col.update_one(query[0], {'$set': archived_status})
        if update_status.matched_count > 0:
            st.success('Status de arquivamento atualizado com sucesso!')
            time.sleep(1)
            client.close()
            st.rerun()
        else:
            st.error('Erro ao atualizar o status de arquivamento!')
    
with registrar_teste:
    FormMongoDB(client).form_widget('registration')

with remover_teste:
    FormMongoDB(client).form_widget('removal')

client.close()