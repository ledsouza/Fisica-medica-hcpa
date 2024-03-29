import time
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
from PIL import Image
import pandas as pd

from menu import menu_with_redirect
from data_processing.stylized_table import StylizedCQ, styled_tests_need_to_do
from data_processing.filters import filters_archivation, user_period_query
from data_processing.plot_data import plot_indicadores
from data_processing.indicadores import current_month_due, current_month_done, get_tests_need_to_do, check_materials, calculate_indicadores
from forms import FormMongoDB


st.set_page_config(page_title="Gerência de Controle de Qualidade", layout="wide")
# Open an image file
img = Image.open('Logo_SFMR_Horizontal_Centralizado.png')
st.sidebar.image(img, use_column_width=True)

menu_with_redirect()

uri = f"mongodb+srv://ledsouza:{st.secrets['MONGODB_PASSWORD']}@mnmanagement.opks2ne.mongodb.net/?retryWrites=true&w=majority"

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
    begin_period = datetime(year, month, 1) - pd.DateOffset(year=1)
    end_period = datetime(year, month, 1) + pd.DateOffset(months=1)
    query = {
        "Data da próxima realização": {
            "$gte": begin_period,
            "$lt": end_period
        }
    }
    df_tests_to_due = current_month_due(collection, query)
    
    query = {
        "Data de realização": {
            "$gte": begin_period,
            "$lt": end_period
        }
    }
    df_tests_now = current_month_done(collection, query)
    df_tests_need_to_do = get_tests_need_to_do(df_tests_to_due, df_tests_now)
    
    # Verificar presença de materiais para realização dos testes
    df_tests_need_to_do = check_materials(df_tests_need_to_do)
    
    styled_tests_need_to_do(df_tests_need_to_do)
    
    indicador_realizacao, indicador_arquivamento, total_to_do = calculate_indicadores(df_tests_need_to_do)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label='Total de testes para realizar', value=f'{total_to_do}')
    with col2:
        st.metric(label='Indicador de Realização Total', value=f'{indicador_realizacao:.2f}%'.replace('.', ','))
    with col3:
        st.metric(label='Indicador de Arquivamento Total', value=f'{indicador_arquivamento:.2f}%'.replace('.', ','))
    with col4:
        def refresh_data():
            current_month_due.clear()
            current_month_done.clear()
            get_tests_need_to_do.clear()

        st.markdown('<br>', unsafe_allow_html=True)
        st.button('Atualizar dados', type='primary', key='update_cache', on_click=refresh_data)
        
    done_df = df_tests_need_to_do.query('not_done == False and `Sem material` == False')[['Equipamento', 'Nome', 'Arquivado']]
    due_df = df_tests_need_to_do.query('`Sem material` == False')[['Equipamento', 'Nome', 'Arquivado']]

    # Abas para exibir os indicadores de realização e arquivamento por equipamento com visualização de gráfica
    tab_realizacao, tab_arquivamento = st.tabs(['Realização por equipamento', 'Arquivamento por equipamento'])
    
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