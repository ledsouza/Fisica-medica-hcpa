import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

def plot_indicadores(done_df: pd.DataFrame, due_df: pd.DataFrame, indicador: str):
        if indicador == 'realizados':
            title = 'Indicador de Realização por Equipamento'
            column = 'Indicador de Realização'
        elif indicador == 'arquivados':
            title = 'Indicador de Arquivamento por Equipamento'
            column = 'Indicador de Arquivamento'
        else:
            raise ValueError('Tipo de indicador inválido')
        
        grouped_done_df = done_df.groupby(['Equipamento']).size().reset_index(name='Realizados')
        grouped_due_df = due_df.groupby(['Equipamento']).size().reset_index(name='Previstos')
        realizacao_equipamento = pd.merge(grouped_done_df, grouped_due_df, on='Equipamento', how='outer')
        realizacao_equipamento.fillna(0, inplace=True)
        realizacao_equipamento[column] = realizacao_equipamento['Realizados'] / realizacao_equipamento['Previstos'] * 100
        realizacao_equipamento.sort_values(by=column, ascending=True, inplace=True)

        fig = go.Figure(data=[go.Bar(x=realizacao_equipamento[column], 
                                    y=realizacao_equipamento["Equipamento"], 
                                    orientation='h',
                                    name='',
                                    textfont=dict(size=14),
                                    text=realizacao_equipamento[column].apply(lambda x: f'{x:.2f}%'.replace('.', ',')),
                                    textposition='inside',
                                    hoverinfo='none'
                        )])
        fig.update_layout(title=title, 
                        xaxis_title="", 
                        xaxis_title_font=dict(size=16),
                        xaxis=dict(range=[0, 101], fixedrange=True, tickfont=dict(size=14)),
                        yaxis_title="",
                        yaxis=dict(tickfont=dict(size=14)),
                        title_font=dict(size=24),
                        height=700
                        )
        st.plotly_chart(fig, use_container_width=True)

class DataPlotting:
    def __init__(self, data: pd.DataFrame):
        self.data = self._viz_data(data)
        self.exame, self.atividade_max, self.atividade_min, self.dose_max, self.dose_min, self.conversion_factor = self._extract_info(data)
        self.periodo = f"{self.data['Mês'].values[0]} de {self.data['Ano'].values[0]} a {self.data['Mês'].values[-1]} de {self.data['Ano'].values[-1]}"
    
    @staticmethod    
    def _viz_data(data):
        viz_data = data.copy()
        viz_data['Atividade Administrada (str)'] = viz_data['Atividade Administrada'].apply(lambda x: f"{x:.2f}").str.replace('.', ',')
        viz_data['Dose (str)'] = viz_data['Dose (mSv)'].apply(lambda x: f"{x:.2f}").str.replace('.', ',')
        viz_data['Atividade específica (str)'] = viz_data['Atividade específica (mCi/kg)'].apply(lambda x: f"{x:.2f}").str.replace('.', ',')
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
        conversion_factor = info[exame][2]
        dose_max = atividade_max * conversion_factor
        dose_min = atividade_min * conversion_factor
        return exame, atividade_max, atividade_min, dose_max, dose_min, conversion_factor

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
            yaxis_title="Atividade administrada (mCi)",
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
            xaxis_title="Atividade administrada (mCi)",
            yaxis_title="Percentual",
            yaxis=dict(showticklabels=False, showgrid=False),
            height=500
        )

        fig.update_traces(marker_line_width=1, marker_line_color="white")

        st.plotly_chart(fig, use_container_width=True)
        
    def plot_dose(self):
        
        title_text = f"Dose recebida pelo paciente em cada solicitação de exame<br><sup size=16>Paciente Adulto com idade acima de 18 anos | Fator de conversão: {self.conversion_factor:.2f}<br>Período: {self.periodo}</sup>".replace('.', ',')

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
            yaxis_title="Dose (mSv)",
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
        title_text = f"Distribuição da dose recebida pelo paciente<br><sup size=16>Paciente Adulto com idade acima de 18 anos | Fator de conversão: {self.conversion_factor:.2f}<br>Período: {self.periodo}</sup>".replace('.', ',')
        
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
            xaxis_title="Dose (mSv)",
            yaxis_title="Percentual",
            yaxis=dict(showticklabels=False, showgrid=False),
            height=500
        )

        fig.update_traces(marker_line_width=1, marker_line_color="white")

        st.plotly_chart(fig, use_container_width=True)
        
    def plot_correlation_atvs_peso(self, df_correlation):
        
        title_text = f"Correlação entre Atividade Específica e Peso<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {self.periodo}</sup>"
        
        fig = go.Figure(data=go.Scatter(x=df_correlation['Peso (kg)'], 
                                            y=df_correlation['Atividade específica (mCi/kg)'], 
                                            mode='markers',
                                            name='',
                                            marker_color="#023E73",
                                            customdata= np.stack((self.data["Atividade específica (str)"], self.data['Dose (str)']), axis=-1),
                                            hovertemplate="<b>Atividade específica: %{customdata[0]} mCi/kg<br>Dose: %{customdata[1]} mSv</b>"
                                            ))
        
        fig.update_layout(title=title_text, 
                            xaxis_title='Peso (kg)', 
                            yaxis_title='Atividade específica (mCi/kg)',
                            xaxis=dict(range=[0, 200], fixedrange=True),
                            )
        
        st.plotly_chart(fig, use_container_width=True)
        
    def plot_correlation_atv_peso(self, df_correlation):
        
        title_text = f"Correlação entre Atividade Administrada e Peso<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {self.periodo}</sup>"
        
        fig = go.Figure(data=go.Scatter(x=df_correlation['Peso (kg)'], 
                                            y=df_correlation['Atividade Administrada'], 
                                            mode='markers',
                                            name='',
                                            marker_color="#023E73",
                                            customdata= np.stack((self.data["Atividade Administrada (str)"], self.data['Dose (str)']), axis=-1),
                                            hovertemplate="<b>Atividade administrada: %{customdata[0]} mCi<br>Dose: %{customdata[1]} mSv</b>"
                                            ))
        
        fig.update_layout(title=title_text, 
                            xaxis_title='Peso (kg)', 
                            yaxis_title='Atividade administrada (mCi)',
                            xaxis=dict(range=[0, 200], fixedrange=True),
                            )
        
        st.plotly_chart(fig, use_container_width=True)
        
    def plot_correlation_atv_dose(self, df_correlation):
        
        title_text = f"Correlação entre Atividade Administrada e Dose<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {self.periodo}</sup>"
        
        fig = go.Figure(data=go.Scatter(x=df_correlation['Atividade Administrada'], 
                                            y=df_correlation['Dose (mSv)'], 
                                            mode='markers',
                                            name='',
                                            marker_color="#023E73",
                                            customdata= np.stack((self.data["Atividade Administrada (str)"], self.data['Dose (str)']), axis=-1),
                                            hovertemplate="<b>Atividade administrada: %{customdata[0]} mCi<br>Dose: %{customdata[1]} mSv</b>"
                                            ))
        
        fig.update_layout(title=title_text, 
                            xaxis_title='Atividade administrada (mCi)', 
                            yaxis_title='Dose (mSv)',
                            xaxis=dict(range=[df_correlation['Atividade Administrada'].min(), df_correlation['Atividade Administrada'].max()], fixedrange=True),
                            )
        
        st.plotly_chart(fig, use_container_width=True)
        
    def plot_correlation_atvs_dose(self, df_correlation):
        
        title_text = f"Correlação entre Atividade Específica e Dose<br><sup size=16>Paciente Adulto com idade acima de 18 anos<br>Período: {self.periodo}</sup>"
        
        fig = go.Figure(data=go.Scatter(x=df_correlation['Atividade específica (mCi/kg)'], 
                                            y=df_correlation['Dose (mSv)'], 
                                            mode='markers',
                                            name='',
                                            marker_color="#023E73",
                                            customdata= np.stack((self.data["Atividade específica (str)"], self.data['Dose (str)']), axis=-1),
                                            hovertemplate="<b>Atividade específica: %{customdata[0]} mCi/kg<br>Dose: %{customdata[1]} mSv</b>"
                                            ))
        
        fig.update_layout(title=title_text, 
                            xaxis_title='Atividade específica (mCi/kg)', 
                            yaxis_title='Dose (mSv)',
                            xaxis=dict(range=[df_correlation['Atividade específica (mCi/kg)'].min(), df_correlation['Atividade específica (mCi/kg)'].max()], fixedrange=True),
                            )
        
        st.plotly_chart(fig, use_container_width=True)