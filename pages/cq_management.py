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
from data_processing.filters import filters_archivation, user_period_query
from data_processing.plot_data import plot_indicadores
from data_processing.tests_to_do import current_month_done
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

# Aba de indicadores
indicadores, arquivamento, registrar_teste, remover_teste = st.tabs(['Indicadores',
                                                                    'Arquivamento',
                                                                    'Registrar teste',
                                                                    'Remover teste'])

with indicadores:
    collection = db['testes']
    
    # Selectbox para escolher o ano e mês
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
            'Fevereiro': 2,
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
    
    # Query para buscar os testes que estão para vencer
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
    
    tests_to_do_current_month, tests_done_current_month, tests_to_due_current_month = current_month_done(tests_to_due, begin_period, end_period, collection)
    
    # Verificar presença de materiais para realização dos testes
    due_df = pd.DataFrame(tests_to_due_current_month, columns=['Equipamento', 'Nome'])
    due_df['Sem material'] = False
    tests_to_do_current_month['Sem material'] = False
    with st.sidebar:
        st.markdown('Materiais ausentes para realização dos testes:')
        materials = {}
        materials['Ga-67'] = st.toggle('Ga-67', value=True)
        materials['Tl-201'] = st.toggle('Tl-201', value=True)
        materials['I-131'] = st.toggle('I-131', value=False)
    
    if materials['Ga-67'] and materials['Tl-201'] and materials['I-131']:
        tests_to_do_current_month['Sem material'] = tests_to_do_current_month['Nome'].apply(lambda x: True if 'Ga-67' in x or 'Tl-201' in x or 'I-131' in x else False)
        due_df['Sem material'] = due_df['Nome'].apply(lambda x: True if 'Ga-67' in x or 'Tl-201' in x or 'I-131' in x else False)

    if materials['Ga-67'] and materials['Tl-201'] and not materials['I-131']:
        tests_to_do_current_month['Sem material'] = tests_to_do_current_month['Nome'].apply(lambda x: True if 'Ga-67' in x or 'Tl-201' in x else False)
        due_df['Sem material'] = due_df['Nome'].apply(lambda x: True if 'Ga-67' in x or 'Tl-201' in x else False)

    if materials['Ga-67'] and not materials['Tl-201'] and materials['I-131']:
        tests_to_do_current_month['Sem material'] = tests_to_do_current_month['Nome'].apply(lambda x: True if 'Ga-67' in x or 'I-131' in x else False)
        due_df['Sem material'] = due_df['Nome'].apply(lambda x: True if 'Ga-67' in x or 'I-131' in x else False)

    if not materials['Ga-67'] and materials['Tl-201'] and materials['I-131']:
        tests_to_do_current_month['Sem material'] = tests_to_do_current_month['Nome'].apply(lambda x: True if 'Tl-201' in x or 'I-131' in x else False)
        due_df['Sem material'] = due_df['Nome'].apply(lambda x: True if 'Tl-201' in x or 'I-131' in x else False)

    if materials['Ga-67'] and not materials['Tl-201'] and not materials['I-131']:
        tests_to_do_current_month['Sem material'] = tests_to_do_current_month['Nome'].apply(lambda x: True if 'Ga-67' in x else False)
        due_df['Sem material'] = due_df['Nome'].apply(lambda x: True if 'Ga-67' in x else False)

    if not materials['Ga-67'] and materials['Tl-201'] and not materials['I-131']:
        tests_to_do_current_month['Sem material'] = tests_to_do_current_month['Nome'].apply(lambda x: True if 'Tl-201' in x else False)
        due_df['Sem material'] = due_df['Nome'].apply(lambda x: True if 'Tl-201' in x else False)

    if not materials['Ga-67'] and not materials['Tl-201'] and materials['I-131']:
        tests_to_do_current_month['Sem material'] = tests_to_do_current_month['Nome'].apply(lambda x: True if 'I-131' in x else False)
        due_df['Sem material'] = due_df['Nome'].apply(lambda x: True if 'I-131' in x else False)
    
    # Formatar o dataframe para exibição
    if not tests_to_do_current_month.empty:
        tests_to_do_current_month.rename(columns={'Data de realização': 'Data da última realização', 'Data da próxima realização': 'Data de realização esperada'}, inplace=True)
        tests_to_do_current_month.sort_values(by=['Sem material','Data de realização esperada'], inplace=True)
        s_tests_to_do_current_month = tests_to_do_current_month.drop(columns='Arquivado').style
        s_tests_to_do_current_month.format(
            {
                'Data da última realização': '{:%d/%m/%Y}',
                'Data de realização esperada': '{:%d/%m/%Y}'
            }
        )
        
        # Exibir os testes que estão para vencer no mês corrente
        st.dataframe(s_tests_to_do_current_month, hide_index=True, use_container_width=True)
    else:
        st.success('Todos os testes realizados!')

    # Calcular os indicadores
    total_done = len(tests_done_current_month)
    mask = (tests_to_do_current_month['Sem material'] == False) 
    total_due = len(tests_to_do_current_month[mask])
    total_tests = due_df[due_df['Sem material'] == False].shape[0]
        
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
        st.metric(label='Indicador de Realização Total', value=f'{indicador_realizacao:.2f}%'.replace('.', ','))
    with col3:
        st.metric(label='Indicador de Arquivamento Total', value=f'{indicador_arquivamento:.2f}%'.replace('.', ','))

    # Abas para exibir os indicadores de realização e arquivamento por equipamento com visualização de gráfica
    tab_realizacao, tab_arquivamento = st.tabs(['Realização por equipamento', 'Arquivamento por equipamento'])
    done_df = pd.DataFrame(tests_done_current_month)
    done_df = done_df[['Equipamento', 'Nome', 'Arquivado']]
    due_df = due_df[due_df['Sem material'] == False]
    
    # Indicador de realização por equipamento
    with tab_realizacao:
        plot_indicadores(done_df, due_df, indicador='realizados', month=months_key, year=year)

    # Indicador de arquivamento por equipamento
    with tab_arquivamento:
        archived_df = done_df[done_df['Arquivado'] == True]
        plot_indicadores(archived_df, due_df, indicador='arquivados', month=months_key, year=year)

# Arquivamento de testes
if 'teste_archivation' not in st.session_state:
    st.session_state.teste_archivation = False

def change_archive_status():
    st.session_state.teste_archivation = True

with arquivamento:    
    teste_col = db['testes']
    
    query = user_period_query()
        
    testes = pd.DataFrame(list(teste_col.find(query, {'_id': 0, 'Data da próxima realização': 0})))
    
    filtered_tests = filters_archivation(testes)
    
    styler = StylizedCQ(filtered_tests)
    stylized_table = styler.stylized_testes()
    
    edited_df = st.data_editor(stylized_table, hide_index=True, use_container_width=True, on_change=change_archive_status, disabled=('Equipamento', 
                                                                                                                                    'Nome', 
                                                                                                                                    'Data de realização', 
                                                                                                                                    'Data da próxima realização'))
    st.markdown("""
                <span style='font-size: smaller;'>**Observação:** Foi definido o período de um mês para realização do relatório. <br>
                O status de arquivamento é atualizado ao clicar na caixa de seleção. Arquive um teste por vez.</span>
                """
                , unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("""
                    **Legenda:** <br>
                    <span style='color: #FFA07A;'>Relatório atrasado</span> <br>
                    <span style='color: #FFD700;'>Dentro do período de desenvolvimento do relatório</span> <br>
                    <span style='color: #90EE90;'>Relatório realizado</span>
                    """, unsafe_allow_html=True)
                               
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