import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

class DataPlotting:
    def __init__(self, data: pd.DataFrame):
        self.data = self._viz_data(data)
        self.exame, self.atividade_max, self.atividade_min, self.dose_max, self.dose_min = self._extract_info(data)
    
    @staticmethod    
    def _viz_data(data):
        viz_data = data.copy()
        viz_data['Atividade Administrada (str)'] = viz_data['Atividade Administrada'].astype(str).str.replace('.', ',')
        viz_data['Dose (str)'] = viz_data['Dose (mSv)'].astype(str).str.replace('.', ',')
        return viz_data
    
    @staticmethod
    def _extract_info(data):
        exame = data['Nome da definição do procedimento'].values[0]
        info = {
            # Atividade máxima, mínima e fator de conversão
            'CINTILOGRAFIA ÓSSEA': (20, 30, 0.18),
            'CINTILOGRAFIA RENAL COM DMSA': (3, 4.5, 0.33),
            'CINTILOGRAFIA RENAL COM DTPA': (6, 10, 0.18),
            'CINTILOGRAFIA MIOCÁRDICA EM REPOUSO': (15, 35, 0.33),
            'CINTILOGRAFIA MIOCARDICA DE ESFORÇO': (15, 35, 0.29),
            'CINTILOGRAFIA MIOCÁRDICA COM DIPIRIDAMOL': (15, 35, 0.29),
            'CINTILOGRAFIA DE PARATIREÓIDES': (10, 30, 0.29),
            'CINTILOGRAFIA PARA DETERMINAÇÃO DE FLUXO RENAL': (20, 30, 0.18)
        }
        atividade_max = info[exame][0]
        atividade_min = info[exame][1]
        dose_max = atividade_max * info[exame][2]
        dose_min = atividade_min * info[exame][2]
        return exame, atividade_max, atividade_min, dose_max, dose_min

    def plot_atividade_administrada(self): 

        data_inicio = self.data['Mês'].values[0]
        data_fim = self.data['Mês'].values[-1]
        ano = self.data['Ano'].values[0]
        title_text = f"Atividade Administrada em cada solicitação de exame<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {data_inicio} a {data_fim} ({ano})</sup>"

        fig = go.Figure(
            data=go.Scatter(
                x=self.data["Número da Solicitação do Exame"],
                y=self.data["Atividade Administrada"],
                mode="markers",
                name="",
                text=self.data["Código ID do Paciente"],
                customdata= np.stack((self.data["Atividade Administrada (str)"], self.data['Dose (str)']), axis=-1),
                hovertemplate="<b>Código ID do Paciente</b>: %{text}<br><b>Atividade Administrada: %{customdata[0]} mCi<br>Dose: %{customdata[1]} mSv</b>"
            )
        )

        fig.update_layout(
            title=title_text,
            title_font=dict(size=18),
            xaxis_title="",
            yaxis_title="Atividade Administrada [mCi]",
            xaxis=dict(
                range=[0, self.data["Número da Solicitação do Exame"].max()],
                tickmode="array",
                tickvals=[],
                fixedrange=True,
            ),
            height=600,
            width=1500
        )

        fig.add_shape(
            type="line",
            x0=0,
            y0=self.atividade_max,
            x1=1,
            y1=self.atividade_max,
            xref="paper",
            line=dict(color="red", dash="dot"),
        )

        fig.add_shape(
            type="line",
            x0=0,
            y0=self.atividade_min,
            x1=1,
            y1=self.atividade_min,
            xref="paper",
            line=dict(color="red", dash="dot"),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    def plot_dose(self):

        data_inicio = self.data['Mês'].values[0]
        data_fim = self.data['Mês'].values[-1]
        ano = self.data['Ano'].values[0]
        title_text = f"Dose recebida pelo paciente em cada solicitação de exame<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {data_inicio} a {data_fim} ({ano})</sup>"

        fig = go.Figure(
            data=go.Scatter(
                x=self.data["Número da Solicitação do Exame"],
                y=self.data["Dose (mSv)"],
                mode="markers",
                name='',
                text=self.data["Código ID do Paciente"],
                customdata= np.stack((self.data["Atividade Administrada (str)"], self.data['Dose (str)']), axis=-1),
                hovertemplate="<b>Código ID do Paciente</b>: %{text}<br><b>Atividade Administrada: %{customdata[0]} mCi<br>Dose: %{customdata[1]} mSv</b>"
            )
        )

        fig.update_layout(
            title=title_text,
            title_font=dict(size=18),
            xaxis_title="",
            yaxis_title="Dose [mSv]",
            xaxis=dict(
                range=[0, self.data["Número da Solicitação do Exame"].max()],
                tickmode="array",
                tickvals=[],
                fixedrange=True
            ),
            height=600,
            width=1500
        )

        fig.add_shape(
            type="line",
            x0=0,
            y0=self.dose_max,
            x1=1,
            y1=self.dose_max,
            xref='paper',
            line=dict(color="red", dash="dot")
        )

        fig.add_shape(
            type="line",
            x0=0,
            y0=self.dose_min,
            x1=1,
            y1=self.dose_min,
            xref='paper',
            line=dict(color="red", dash="dot")
        )

        st.plotly_chart(fig, use_container_width=True)