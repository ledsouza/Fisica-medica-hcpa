import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

class DataPlotting:
    def __init__(self, data: pd.DataFrame):
        self.data = self._viz_data(data)
        self.exame, self.atividade_max, self.atividade_min, self.dose_max, self.dose_min = self._extract_info(data)
        self.periodo = f"{self.data['Mês'].values[0]} de {self.data['Ano'].values[0]} a {self.data['Mês'].values[-1]} de {self.data['Ano'].values[-1]}"
    
    @staticmethod    
    def _viz_data(data):
        viz_data = data.copy()
        viz_data['Atividade Administrada (str)'] = viz_data['Atividade Administrada'].apply(lambda x: f"{x:.2f}").str.replace('.', ',')
        viz_data['Dose (str)'] = viz_data['Dose (mSv)'].apply(lambda x: f"{x:.2f}").str.replace('.', ',')
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

        title_text = f"Atividade administrada em cada solicitação de exame<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {self.periodo}</sup>"

        fig = go.Figure(
            data=go.Scatter(
                x=self.data["Número da Solicitação do Exame"],
                y=self.data["Atividade Administrada"],
                marker_color="#023E73",
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
            yaxis_title="Atividade administrada [mCi]",
            xaxis=dict(
                range=[0, self.data["Número da Solicitação do Exame"].max()],
                tickmode="array",
                tickvals=[],
                fixedrange=True,
            ),
            height=500
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
        
    def hist_atividade_administrada(self):
        
        title_text = f"Distribuição da atividade administrada<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {self.periodo}</sup>"
        
        fig = go.Figure(
            data=go.Histogram(
                x=self.data["Atividade Administrada"],
                histnorm='percent',
                marker_color="#023E73",
                showlegend=False,
                name='',
                hovertemplate="Atividade administrada: %{x} mCi<br>Percentual: %{y:.2f}%",
                textposition='outside',
                texttemplate='%{y:.2f}%',
                nbinsx = 30
            )
        )

        fig.update_layout(
            title=title_text,
            title_font=dict(size=18),
            xaxis_title="Atividade administrada [mCi]",
            yaxis_title="Percentual",
            yaxis=dict(showticklabels=False, showgrid=False),
            height=500
        )

        fig.update_traces(marker_line_width=1, marker_line_color="white")

        st.plotly_chart(fig, use_container_width=True)
        
    def plot_dose(self):

        title_text = f"Dose recebida pelo paciente em cada solicitação de exame<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {self.periodo}</sup>"

        fig = go.Figure(
            data=go.Scatter(
                x=self.data["Número da Solicitação do Exame"],
                y=self.data["Dose (mSv)"],
                marker_color="#023E73",
                mode="markers",
                name='',
                text=self.data["Código ID do Paciente"],
                customdata= np.stack((self.data["Atividade Administrada (str)"], self.data['Dose (str)']), axis=-1),
                hovertemplate="<b>Código ID do Paciente</b>: %{text}<br><b>Atividade administrada: %{customdata[0]} mCi<br>Dose: %{customdata[1]} mSv</b>"
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
            height=500
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
        
    def hist_dose(self):
        title_text = f"Distribuição da dose recebida pelo paciente<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {self.periodo}</sup>"
        
        fig = go.Figure(
            data=go.Histogram(
                x=self.data["Dose (mSv)"],
                histnorm='percent',
                marker_color="#023E73",
                showlegend=False,
                name='',
                hovertemplate="Dose: %{x} mSv<br>Percentual: %{y:.2f}%",
                textposition='outside',
                texttemplate='%{y:.2f}%',
                nbinsx=30
            )
        )

        fig.update_layout(
            title=title_text,
            title_font=dict(size=18),
            xaxis_title="Dose [mSv]",
            yaxis_title="Percentual",
            yaxis=dict(showticklabels=False, showgrid=False),
            height=500
        )

        fig.update_traces(marker_line_width=1, marker_line_color="white")

        st.plotly_chart(fig, use_container_width=True)