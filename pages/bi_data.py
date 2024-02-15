import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from menu import menu_with_redirect
from data_processing.cleaning_data import DataCleaning
from data_processing.plot_data import DataPlotting
from data_processing.stylized_table import stylized_table

st.set_page_config(page_title="Tratamento de Dados do BI", layout="wide")
menu_with_redirect()

# Extracting the data
bi_data = st.file_uploader("Faça o upload dos dados do BI", type=["csv", "xlsx"])

exames = ['Cintilografia Óssea', 
          'Cintilografia Renal Estática (DMSA)', 
          'Cintilografia Renal Estática (DTPA)',
          'Cintilografia Miocárdica em Repouso',
          'Cintilografia Miocardica de Esforço',
          'Cintilografia Miocárdica com Dipiridamol',
          'Cintilografia de Paratireoides',
          'Cintilografia para Determinação de Fluxo Renal',
          ]
map_to_sheet_name = dict(zip(exames, ['Cintilografia Óssea',
                                      'Cintilografia Renal Estática (D',
                                      'Cintilografia Renal Dinâmica (D',
                                      'Cintilografia Miocárdica em Rep',
                                      'Cintilografia Miocardica de Esf',
                                      'Cintilografia Miocardica de Dip',
                                      'Cintilografia de Paratireóides',
                                      'Cintilografia para Determinação']))

if bi_data is not None:
    @st.cache_data
    def load_data(data, sheet_name):
        if data.name.endswith("csv"):
            bi_dataframe = pd.read_csv(data)
        else:
            check_header = pd.read_excel(data, sheet_name=sheet_name, usecols='A')
            rows_to_skip = check_header[check_header['Unnamed: 0'] == 'SERVICO DE MEDICINA NUCLEAR'].index[0] + 2
            bi_dataframe = pd.read_excel(data, skiprows=rows_to_skip, usecols='A:T', sheet_name=sheet_name)
            return bi_dataframe

    sheet_name = st.selectbox("Selecione o exame", exames)

    
    bi_dataframe = load_data(bi_data, map_to_sheet_name[sheet_name])

    # Cleaning the data
    
    data_cleaner = DataCleaning(bi_dataframe)
    cleaned_bi = data_cleaner.clean_data()
    
    # Filters
    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>Filtros</h1>", unsafe_allow_html=True)
        
        periodo = st.date_input(
            label="Selecione o Período",
            min_value=cleaned_bi["Data"].min(),
            max_value=cleaned_bi["Data"].max(),
            value=(cleaned_bi["Data"].min(), cleaned_bi["Data"].max()),
        )
        try:
            start_date, end_date = periodo
        except:
            st.error("É necessário selecionar um período válido")
            st.stop()
            
        atividade_administrada = st.slider('Selecione a Atividade Administrada', 0.0, cleaned_bi['Atividade Administrada'].max(), (0.0, cleaned_bi['Atividade Administrada'].max()))
        dose = st.slider('Selecione a Dose', 0.0, cleaned_bi['Dose (mSv)'].max(), (0.0, cleaned_bi['Dose (mSv)'].max()))
        if cleaned_bi['Peso (kg)'].isnull().all():
            st.error("Não há dados de peso disponíveis para filtrar")
        else:
            peso = st.slider('Selecione o Peso', 0.0, cleaned_bi['Peso (kg)'].max(), (0.0, cleaned_bi['Peso (kg)'].max()))
        idade = st.slider('Selecione a Idade', 0, cleaned_bi['Idade do paciente'].max(), (0, cleaned_bi['Idade do paciente'].max()))
        sexo = st.multiselect("Selecione o Sexo", cleaned_bi['Sexo'].unique(), cleaned_bi['Sexo'].unique())
        nome_sala = st.multiselect("Selecione a Sala", cleaned_bi['Nome da sala'].unique(), cleaned_bi['Nome da sala'].unique())
    
    if cleaned_bi['Peso (kg)'].isnull().all():
        query = """
        @periodo[0] <= Data <= @periodo[1] and \
        @atividade_administrada[0] <= `Atividade Administrada` <= @atividade_administrada[1] and \
        @dose[0] <= `Dose (mSv)` <= @dose[1] and \
        @idade[0] <= `Idade do paciente` <= @idade[1] and \
        Sexo in @sexo and \
        `Nome da sala` in @nome_sala
        """
    else:  
        query = """
        @periodo[0] <= Data <= @periodo[1] and \
        @atividade_administrada[0] <= `Atividade Administrada` <= @atividade_administrada[1] and \
        @dose[0] <= `Dose (mSv)` <= @dose[1] and \
        @peso[0] <= `Peso (kg)` <= @peso[1] and \
        @idade[0] <= `Idade do paciente` <= @idade[1] and \
        Sexo in @sexo and \
        `Nome da sala` in @nome_sala
        """
    filtered_data = cleaned_bi.query(query)
    
    # Download button
    @st.cache_data
    def convert_to_csv(data):
        return data.to_csv(index=False)
    
    col1, col2 = st.columns(2)
    with col1:
        file_name = st.text_input("Prencha aqui o nome do arquivo para download", value="dados_tratados")
        
    with col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if bi_data.name.endswith("csv"):
            st.download_button(
                label="Baixar os dados tratados",
                data=convert_to_csv(filtered_data),
                file_name=f"{file_name}.csv",
                mime="text/csv",
                type='primary'
            )
        else:
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                filtered_data.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                
                st.download_button(
                    label="Baixar os dados tratados",
                    data=buffer,
                    file_name=f"{file_name}.xlsx",
                    mime="application/vnd.ms-excel",
                    type='primary'
                )
    
    tab1, tab2, tab3 = st.tabs(["Tabela", "Atividade Administrada", "Dose"])
    
    with tab1:
        tableviz = stylized_table(filtered_data)
        st.dataframe(tableviz, use_container_width=True, hide_index=True)
        st.dataframe(cleaned_bi, use_container_width=True, hide_index=True)
        
    # Plotting the data
    plot = DataPlotting(filtered_data)
    
    with tab2:
        plot.plot_atividade_administrada()
    with tab3:
        plot.plot_dose()