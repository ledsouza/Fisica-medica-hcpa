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
from data_processing.filters import filters_archivation
from forms import FormMongoDB
from datetime import datetime
from tests_periodicity import TestsPeriodicity

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
    
    previous_year = year - 2
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
    tests_done_current_month = []
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
            tests_periodicity = TestsPeriodicity().full_list()
            
            if tests_periodicity[test['Nome']] == 'Mensal':
                test_done['diff'] = (test_done['Data da próxima realização'] - test_done['Data de realização']).dt.days
                test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=29)
            elif tests_periodicity[test['Nome']] == 'Trimestral':
                test_done['diff'] = (test_done['Data da próxima realização'] - test_done['Data de realização']).dt.days
                test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=91)
            elif tests_periodicity[test['Nome']] == 'Semestral':
                test_done['diff'] = (test_done['Data da próxima realização'] - test_done['Data de realização']).dt.days
                test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=182)
            elif tests_periodicity[test['Nome']] == 'Anual':
                test_done['diff'] = (test_done['Data da próxima realização'] - test_done['Data de realização']).dt.days
                test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=366)            
            
            if test_done['is_expired'].values[0]:
                test_done.drop(columns='is_expired', inplace=True)
                tests_to_do_current_month = pd.concat([tests_to_do_current_month, test_done])
            else:
                tests_done_current_month.append(test_done.to_dict('records')[0])
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
                                                      hide_index=True,  
                                                      disabled=('Equipamento',
                                                                'Nome',
                                                                'Data da última realização',
                                                                'Data de realização esperada'
                                                                ))

    mask = (edited_tests_to_do_current_month['Sem material'] == True) 
    total_done = len(tests_done_current_month) + len(edited_tests_to_do_current_month[mask])
    
    mask = (edited_tests_to_do_current_month['Sem material'] == False) 
    total_due = len(edited_tests_to_do_current_month[mask])
    
    total_tests = len(tests_to_due_current_month)
        
    indicador_realizacao = total_done / (total_tests) * 100
    
    total_archived = total_done
    for test in tests_done_current_month:
        if not test['Arquivado']:
            total_archived -= 1
    indicador_arquivamento = total_archived / total_tests * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label='Total de testes para realizar', value=f'{total_due}')
    with col2:
        st.metric(label='Indicador de Realização', value=f'{indicador_realizacao:.2f}%'.replace('.', ','))
    with col3:
        st.metric(label='Indicador de Arquivamento', value=f'{indicador_arquivamento:.2f}%'.replace('.', ','))
    

if 'teste_archivation' not in st.session_state:
    st.session_state.teste_archivation = False

def change_archive_status():
    st.session_state.teste_archivation = True

with arquivamento:    
    teste_col = db['testes']
    testes = pd.DataFrame(list(teste_col.find({}, {'_id': 0, 'Data da próxima realização': 0})))
    
    filtered_tests = filters_archivation(testes)
    
    styler = StylizedCQ(filtered_tests)
    stylized_table = styler.stylized_testes()
    
    edited_df = st.data_editor(stylized_table, hide_index=True, use_container_width=True, on_change=change_archive_status, disabled=('Equipamento', 
                                                                                                                                    'Nome', 
                                                                                                                                    'Data de realização', 
                                                                                                                                    'Data da próxima realização'))
                                    
    if st.session_state.teste_archivation:
        st.session_state.teste_archivation = False
        
        diff = filtered_tests.compare(edited_df)
        
        # Drop the multi-index to make filtering easier
        diff.columns = diff.columns.droplevel(0)
        
        # Get the indices of the rows with differences
        diff_indices = diff[diff['self'].notna() | diff['other'].notna()].index
        
        # Get the entire rows from the original dataframe
        diff_rows = filtered_tests.loc[diff_indices]
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
            
    
    
with registrar_teste:
    FormMongoDB(client).form_widget('registration')

with remover_teste:
    FormMongoDB(client).form_widget('removal')

client.close()