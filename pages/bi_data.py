import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from menu import menu_with_redirect
from cleaning_data import clean_data

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
    st.dataframe(bi_dataframe, use_container_width=True, hide_index=True)

    # Cleaning the data
    # cleaned_bi = clean_data(bi_dataframe)   
    # st.dataframe(cleaned_bi, use_container_width=True, hide_index=True)
    
    # cleaned_bi = cleaned_bi.query('`Atividade Administrada` > 10.0')
    # cleaned_bi = cleaned_bi.query('`Peso (kg)` < 150.0 and `Peso (kg)` > 10.0')
    
    # cleaned_bi['Nome do produto'] = cleaned_bi['Nome do produto'].str.replace('Tc-99m', '99mTc-MDP')
    
    # tableviz_bi = cleaned_bi.copy()
    # tableviz_bi['Data'] = tableviz_bi['Data'].dt.strftime('%d/%m/%Y')
    # tableviz_bi['Ano'] = tableviz_bi['Ano'].astype(str)
    # tableviz_bi['Código ID do Paciente'] = tableviz_bi['Código ID do Paciente'].astype(str)
    # tableviz_bi.rename(columns={
    #     'Peso (kg)': 'Peso',
    #     'Atividade específica (mCi/kg)': 'Atividade Específica',
    #     'Dose (mSv)': 'Dose'
    # }, inplace=True)
    
    # tableviz_bi = tableviz_bi.style.format({
    #     'Atividade Administrada': '{:.2f} mCi',
    #     'Peso': '{:.2f} kg',
    #     'Dose': '{:.2f} mSv',
    # }, decimal=',')
    
    # st.dataframe(tableviz_bi, use_container_width=True, hide_index=True)
    
    # # Plotting the data
    # plot_bi = cleaned_bi.copy()
    # plot_bi['Atividade Administrada (str)'] = plot_bi['Atividade Administrada'].astype(str).str.replace('.', ',')
    # plot_bi['Dose (str)'] = plot_bi['Dose (mSv)'].astype(str).str.replace('.', ',')
    
    # atividade_max = 30
    # atividade_min = 20
    # data_inicio = cleaned_bi['Mês'].values[0]
    # data_fim = cleaned_bi['Mês'].values[-1]
    # title_text = f"Atividade Administrada em cada solicitação de exame<br><sup size=16>Paciente Adulto com idade acima de 18 anos, Isótopo: Tc-99m, Fármaco: MDP<br>Perído: {data_inicio} a {data_fim}</sup>"

    # fig = go.Figure(
    #     data=go.Scatter(
    #         x=cleaned_bi["Número da Solicitação do Exame"],
    #         y=cleaned_bi["Atividade Administrada"],
    #         mode="markers",
    #         name="",
    #         text=cleaned_bi["Código ID do Paciente"],
    #         customdata=plot_bi["Atividade Administrada (str)"],
    #         hovertemplate="<b>Código ID do Paciente</b>: %{text}<br><b>Atividade Administrada</b>: %{customdata} mCi",
    #     )
    # )

    # fig.update_layout(
    #     title=title_text,
    #     title_font=dict(size=18),
    #     xaxis_title="",
    #     yaxis_title="Atividade Administrada [mCi]",
    #     xaxis=dict(
    #         range=[0, cleaned_bi["Número da Solicitação do Exame"].max()],
    #         tickmode="array",
    #         tickvals=[],
    #         fixedrange=True,
    #     ),
    #     height=600,
    #     width=1500
    # )

    # fig.add_shape(
    #     type="line",
    #     x0=0,
    #     y0=atividade_max,
    #     x1=1,
    #     y1=atividade_max,
    #     xref="paper",
    #     line=dict(color="red", dash="dot"),
    # )

    # fig.add_shape(
    #     type="line",
    #     x0=0,
    #     y0=atividade_min,
    #     x1=1,
    #     y1=atividade_min,
    #     xref="paper",
    #     line=dict(color="red", dash="dot"),
    # )

    # st.plotly_chart(fig, use_container_width=True)
    
    # fator_conversao = 0.15
    # dose_max = atividade_max * fator_conversao
    # dose_min = atividade_min * fator_conversao

    # title_text = f"Dose recebida pelo paciente em cada solicitação de exame<br><sup size=16>Paciente Adulto com idade acima de 18 anos, Isótopo: Tc-99m, Fármaco: MDP<br>Perído: {data_inicio} a {data_fim}</sup>"

    # fig = go.Figure(
    #     data=go.Scatter(
    #         x=cleaned_bi["Número da Solicitação do Exame"],
    #         y=cleaned_bi["Dose (mSv)"],
    #         mode="markers",
    #         name='',
    #         text=cleaned_bi["Código ID do Paciente"],
    #         customdata=plot_bi['Dose (str)'],
    #         hovertemplate="<b>Código ID do Paciente</b>: %{text}<br><b>Atividade Administrada</b>: %{customdata} mSv",
    #     )
    # )

    # fig.update_layout(
    #     title=title_text,
    #     title_font=dict(size=18),
    #     xaxis_title="",
    #     yaxis_title="Dose [mSv]",
    #     xaxis=dict(
    #         range=[0, cleaned_bi["Número da Solicitação do Exame"].max()],
    #         tickmode="array",
    #         tickvals=[],
    #         fixedrange=True
    #     ),
    #     height=600,
    #     width=1500
    # )

    # fig.add_shape(
    #     type="line",
    #     x0=0,
    #     y0=dose_max,
    #     x1=1,
    #     y1=dose_max,
    #     xref='paper',
    #     line=dict(color="red", dash="dot")
    # )

    # fig.add_shape(
    #     type="line",
    #     x0=0,
    #     y0=dose_min,
    #     x1=1,
    #     y1=dose_min,
    #     xref='paper',
    #     line=dict(color="red", dash="dot")
    # )

    # st.plotly_chart(fig, use_container_width=True)
    
    # # Download button
    # @st.cache_data
    # def convert_to_csv(data):
    #     return data.to_csv(index=False)
    
    # col1, col2 = st.columns(2)
    # with col1:
    #     file_name = st.text_input("Prencha aqui o nome do arquivo para download", value="dados_tratados")
        
    # with col2:
    #     st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    #     if bi_data.name.endswith("csv"):
    #         st.download_button(
    #             label="Baixar dados tratados",
    #             data=convert_to_csv(cleaned_bi),
    #             file_name=f"{file_name}.csv",
    #             mime="text/csv",
    #             type='primary'
    #         )
    #     else:
    #         buffer = BytesIO()
            
    #         with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    #             cleaned_bi.to_excel(writer, sheet_name='Sheet1', index=False)
    #             writer.close()
                
    #             st.download_button(
    #                 label="Baixar dados tratados",
    #                 data=buffer,
    #                 file_name=f"{file_name}.xlsx",
    #                 mime="application/vnd.ms-excel",
    #                 type='primary'
    #             )