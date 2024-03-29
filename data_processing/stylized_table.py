import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

def styled_tests_need_to_do(dataframe):
    tests_to_do_current_month = dataframe.query('not_done == True').drop(columns=['not_done'])
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
class StylizedTable:
    def __init__(self, table: pd.DataFrame) -> None:
        self.table = table
        
class StylizedCQ(StylizedTable):
    def __init__(self, table: pd.DataFrame) -> None:
        super().__init__(table)
        
    def stylized_testes(self):
        # Get the current date and time
        current_datetime = datetime.now()
        self.table['due_diff'] = self.table['Data de realização'] - current_datetime
        self.table.sort_values(by=['Arquivado', 'due_diff'], inplace=True, ascending=[True, True])
        self.table.drop(columns='due_diff', inplace=True)
        
        def highlight_expired_dates(row):
            
            if row['Data de realização'] - current_datetime >= timedelta(days=-30) and row['Data de realização'] - current_datetime <= timedelta(days=0) and row['Arquivado'] == False:
                return ['background-color: #FFD700'] * len(row)
            elif row['Data de realização'] - current_datetime <= timedelta(days=-30) and row['Arquivado'] == False:
                return ['background-color: #FFA07A'] * len(row)
            elif row['Data de realização'] - current_datetime > timedelta(days=0) or row['Arquivado'] == True:
                return ['background-color: #90EE90'] * len(row)
        
        self.table = self.table.style.apply(highlight_expired_dates, axis=1)
        self.table = self.table.format({
            'Data de realização': '{:%d/%m/%Y}'
        })
        
        return self.table

def stylized_table(table: pd.DataFrame):   
    tableviz_bi = table.copy()[['Data', 
                                'Ano',
                                'Mês', 
                                'Código ID do Paciente', 
                                'Número do Prontuário',
                                'Número da Solicitação do Exame',
                                'Idade do paciente',
                                'Sexo',
                                'Nome da sala',
                                'Peso (kg)',
                                'Atividade Administrada',  
                                'Atividade específica (mCi/kg)', 
                                'Dose (mSv)']]
    tableviz_bi['Data'] = tableviz_bi['Data'].dt.strftime('%d/%m/%Y')
    tableviz_bi['Ano'] = tableviz_bi['Ano'].astype(str)
    tableviz_bi['Código ID do Paciente'] = tableviz_bi['Código ID do Paciente'].astype(str)
    tableviz_bi.rename(columns={
        'Peso (kg)': 'Peso',
        'Atividade específica (mCi/kg)': 'Atividade Específica',
        'Dose (mSv)': 'Dose'
    }, inplace=True)
    
    tableviz_bi = tableviz_bi.style.format({
        'Atividade Administrada': '{:.2f} mCi',
        'Atividade Específica': '{:.2f} mCi/kg',
        'Peso': '{:.2f} kg',
        'Dose': '{:.2f} mSv'
    }, decimal=',')
    
    return tableviz_bi

def stylized_statistics(table: pd.DataFrame):
    descritive_statistics = table.copy()
    descritive_statistics = descritive_statistics[['Idade do paciente', 
                                                   'Peso (kg)', 
                                                   'Atividade Administrada', 
                                                   'Atividade específica (mCi/kg)', 
                                                   'Dose (mSv)']]
    descritive_statistics.rename(columns={
        'Peso (kg)': 'Peso',
        'Atividade específica (mCi/kg)': 'Atividade Específica',
        'Dose (mSv)': 'Dose'
    }, inplace=True)
    descritive_statistics.dropna(inplace=True)
    descritive_statistics = descritive_statistics.describe().rename(
        index={'count': 'Contagem', 
               'mean': 'Média', 
               'std': 'Desvio Padrão', 
               'min': 'Mínimo', 
               '25%': '1º Quartil', 
               '50%': 'Mediana', 
               '75%': '3º Quartil', 
               'max': 'Máximo'}
    )
    s_statistics = descritive_statistics.iloc[1:,:].style.format(
        {
            'Idade do paciente': '{:.0f}',
            'Peso': '{:.2f} kg',
            'Atividade Administrada': '{:.2f} mCi',
            'Atividade Específica': '{:.2f} mCi/kg',
            'Dose': '{:.2f} mSv'
        }, decimal=','
    )
    
    s_statistics.apply(lambda x: ['color: #3FA63C' if (x.name in ['Mediana', '3º Quartil'] and col in ['Atividade Administrada', 'Atividade Específica']) else '' for col in x.index], axis=1)
    s_statistics.set_table_styles([{
        'selector': 'td,th',
        'props': 'text-align: center;'
    }], overwrite=False)

    return s_statistics

def stylized_correlation(table: pd.DataFrame):
    s_correlation = table.copy().rename(columns={
        'Peso (kg)': 'Peso',
        'Atividade específica (mCi/kg)': 'Atividade Específica',
        'Dose (mSv)': 'Dose'
    })
    
    s_correlation = s_correlation.corr().style.background_gradient(cmap='Greens', axis=None).format("{:.2f}")
    
    return s_correlation