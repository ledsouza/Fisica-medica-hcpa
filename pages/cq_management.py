import streamlit as st
from PIL import Image
from menu import menu_with_redirect
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import pandas as pd
import time
from data_processing.stylized_table import StylizedCQ
from forms import FormMongoDB
from datetime import datetime
from tests_periodicity import map_gc_periodicity

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
    
indicadores, arquivamento, registrar_teste, remover_teste = st.tabs(['Indicadores',
                                                                    'Arquivamento',
                                                                    'Registrar teste',
                                                                    'Remover teste'])

with indicadores:
    collection = db['testes']
    
    col1, col2 = st.columns(2)
    
    with col1:
        pipeline = [
            {
                "$project": {
                    "year": {"$year": "$Data da próxima realização"}
                }
            },
            {
                "$group": {
                    "_id": "$year"
                }
            }
        ]
        distinct_years = collection.aggregate(pipeline)
        years = sorted([year['_id'] for year in distinct_years])[1:]
        current_year = datetime.now().year
        year = st.selectbox('Selecione o ano', years, index=years.index(current_year))
    
    with col2:
        months = {
            'Janeiro': 1,
            'Feveiro': 2,
            'Março': 3,
            'Abril': 4,
            'Maio': 5,
            'Junho': 6,
            'Julho': 7,
            'Agosto': 8,
            'Setembro': 9,
            'Outubro': 10,
            'Novembro': 11,
            'Dezembro': 12
        }
        current_month = datetime.now().month
        months_key = st.selectbox('Selecione o mês', months.keys(), index=(current_month - 1))
        month = months[months_key]
    
    previous_year = year - 1
    begin_period = datetime(previous_year, month, 1)
    if month == 12:
        end_period = datetime(year+1, 1, 1)
    else:
        end_period = datetime(year, month+1, 1)
    query = {
        "Data da próxima realização": {
            "$gte": begin_period,
            "$lt": end_period
        }
    }
    tests_to_due = collection.find(query, {'_id': 0, 'Equipamento': 1, 'Nome': 1, 'Data da próxima realização': 1}).sort('Data da próxima realização', pymongo.DESCENDING)

    tests_to_do_current_month = pd.DataFrame()
    tests_to_due_current_month = []
    check_if_archived = []
    for test in tests_to_due:
        tuple_test = (test['Equipamento'], test['Nome'])
        if tuple_test not in tests_to_due_current_month:
            test_check = tests_to_due_current_month.append(tuple_test)
        else:
            continue
        data_da_proxima_realizacao = test.pop('Data da próxima realização')
        query = {
            "Data de realização": {
                "$gte": begin_period,
                "$lt": end_period
            },
            **test
        }
        result = collection.find(query, {'_id': 0, 'Data da próxima realização': 0})
        test_done = pd.DataFrame(list(result))
        
        if not test_done.empty:
            test_done.sort_values(by='Data de realização', ascending=False, inplace=True)
            test_done['Data da próxima realização'] = data_da_proxima_realizacao
            test_done = test_done.iloc[[0]]
            
            if map_gc_periodicity(test['Nome']) == 'Mensal':
                test_done['diff'] = (test_done['Data da próxima realização'] - test_done['Data de realização']).dt.days
                test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=29)
            elif map_gc_periodicity(test['Nome']) == 'Trimestral':
                test_done['diff'] = (test_done['Data da próxima realização'] - test_done['Data de realização']).dt.days
                test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=91)
            elif map_gc_periodicity(test['Nome']) == 'Semestral':
                test_done['diff'] = (test_done['Data da próxima realização'] - test_done['Data de realização']).dt.days
                test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=182)
            elif map_gc_periodicity(test['Nome']) == 'Anual':
                test_done['diff'] = (test_done['Data da próxima realização'] - test_done['Data de realização']).dt.days
                test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=366)            
            
            if test_done['is_expired'].values[0]:
                test_done.drop(columns='is_expired', inplace=True)
                tests_to_do_current_month = pd.concat([tests_to_do_current_month, test_done.iloc[[0]]])
            else:
                check_if_archived.append({'Equipamento': test_done.iloc[[0]]['Equipamento'].values[0],
                                         'Nome': test_done.iloc[[0]]['Nome'].values[0],
                                         'Data de realização': test_done.iloc[[0]]['Data de realização'].values[0],
                                         })
        else:
            continue
    tests_to_do_current_month.drop(columns='diff', inplace=True)
    
    
    
    tests_to_do_current_month['Sem material'] = False
    tests_to_do_current_month.rename(columns={'Data de realização': 'Data da última realização', 'Data da próxima realização': 'Data de realização esperada'}, inplace=True)
    s_tests_to_do_current_month = tests_to_do_current_month.drop(columns='Arquivado').style
    s_tests_to_do_current_month.format(
        {
            'Data da última realização': '{:%d/%m/%Y}',
            'Data de realização esperada': '{:%d/%m/%Y}'
        }
    )
    
    edited_tests_to_do_current_month = st.data_editor(s_tests_to_do_current_month, 
                                                      use_container_width=True, 
                                                      hide_index=True,  
                                                      disabled=('Equipamento',
                                                                'Nome',
                                                                'Data da última realização',
                                                                'Data de realização esperada'
                                                                ))

    mask = (edited_tests_to_do_current_month['Sem material'] == False)
    total_due = len(edited_tests_to_do_current_month[mask])
    total_tests = len(tests_to_due_current_month)
        
    meta = total_tests / (total_due + total_tests) * 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label='Total de testes para realizar', value=f'{total_due}')
    with col2:
        st.metric(label='Indicador de Realização', value=f'{meta:.2f}%')
    

if 'teste_archivation' not in st.session_state:
    st.session_state.teste_archivation = False

def change_archive_status():
    st.session_state.teste_archivation = True

with arquivamento:    
    teste_col = db['testes']
    testes = pd.DataFrame(list(teste_col.find({}, {'_id': 0, 'Data da próxima realização': 0})))
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
            
    st.write(check_if_archived)
    
    
with registrar_teste:
    FormMongoDB(client).form_widget('registration')

with remover_teste:
    FormMongoDB(client).form_widget('removal')

client.close()