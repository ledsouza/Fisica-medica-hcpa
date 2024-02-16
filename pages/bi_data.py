import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.graph_objects as go
from io import BytesIO
from menu import menu_with_redirect
from data_processing.cleaning_data import DataCleaning
from data_processing.filters import filters_bi
from data_processing.plot_data import DataPlotting
from data_processing.stylized_table import stylized_table, stylized_statistics

st.set_page_config(page_title="Tratamento de Dados do BI", layout="wide")
# Open an image file
img = Image.open('logos\Logo_SFMR_Horizontal_Centralizado.png')
st.sidebar.image(img, use_column_width=True)

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
            try:
                check_header = pd.read_excel(data, sheet_name=sheet_name, usecols='A')
                rows_to_skip = check_header[check_header['Unnamed: 0'] == 'SERVICO DE MEDICINA NUCLEAR'].index[0] + 2
                bi_dataframe = pd.read_excel(data, skiprows=rows_to_skip, usecols='A:T', sheet_name=sheet_name)
            except KeyError:
                st.error('''
                         Não há dados disponíveis para o exame selecionado.
                         Verifique a planilha selecionada e tente novamente.
                         ''')
                st.stop()
            except ValueError:
                st.error('''
                         Não há dados disponíveis para o exame selecionado.
                         Verifique a planilha selecionada e tente novamente.
                         ''')
                st.stop()
            return bi_dataframe

    sheet_name = st.selectbox("Selecione o exame", exames)

    
    bi_dataframe = load_data(bi_data, map_to_sheet_name[sheet_name])

    # Cleaning the data
    data_cleaner = DataCleaning(bi_dataframe)
    cleaned_bi = data_cleaner.clean_data()
    
    # Filters
    filtered_df = filters_bi(cleaned_bi)
    
    # Download button
    @st.cache_data
    def convert_to_csv(data):
        return data.to_csv(index=False)
    
    col1, col2 = st.columns(2)
    with col1:
        file_name = st.text_input("Prencha aqui o nome do arquivo para download", 
                                  value=f"{sheet_name} Tratado")
        
    with col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if bi_data.name.endswith("csv"):
            st.download_button(
                label=":arrow_down: Baixar os dados tratados",
                data=convert_to_csv(filtered_df),
                file_name=f"{file_name}.csv",
                mime="text/csv",
                type='primary',
                help='A planilha baixada será referente ao exame selecionado'
            )
        else:
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                
                st.download_button(
                    label=":arrow_down: Baixar os dados tratados",
                    data=buffer,
                    file_name=f"{file_name}.xlsx",
                    mime="application/vnd.ms-excel",
                    type='primary',
                    help='A planilha baixada será referente ao exame selecionado e com os filtros aplicados.'
                )
    
    tab1, tab2, tab3 = st.tabs(["Tabela", "Atividade Administrada", "Dose"])
    
    with tab1:
        tableviz = stylized_table(filtered_df)
        st.dataframe(tableviz, use_container_width=True, hide_index=True)
        
        st.markdown('## Estatística Descritiva')
        
        if not filtered_df['Peso (kg)'].isnull().all():
            descritive_statistics = stylized_statistics(filtered_df)
            
            st.dataframe(descritive_statistics, use_container_width=True)
            
            st.markdown('''
                        <sup>**Observação**: O Nível de Referência Diagnóstica (DRL) pode ser definido como o terceiro quartil 
                        ou mediana da atividade específica ou atividade administrada.
                        <br>Todos os dados nulos são desconsiderados nesses cálculos.</sup>
                        ''', unsafe_allow_html=True)
        else:
            st.error(f'Não há valores suficientes para calcular a estatística descritiva.')
        
    # Plotting the data
    plot = DataPlotting(filtered_df)
    
    with tab2:
        plot.plot_atividade_administrada()
        plot.hist_atividade_administrada()
    with tab3:
        plot.plot_dose()
        plot.hist_dose()