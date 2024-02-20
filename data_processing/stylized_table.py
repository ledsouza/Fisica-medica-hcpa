import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

class StylizedTable:
    def __init__(self, table: pd.DataFrame) -> None:
        self.table = table
        
class StylizedCQ(StylizedTable):
    def __init__(self, table: pd.DataFrame) -> None:
        super().__init__(table)
        
    def stylized_testes(self):
        # Get the current date and time
        current_datetime = datetime.now()
        self.table.sort_values(by='Data da próxima realização', inplace=True)
        self.table['Data da próxima realização'] = pd.to_datetime(self.table['Data da próxima realização'], format='%d/%m/%Y')
        
        def highlight_expired_dates(row):
            
            if row['Data da próxima realização'] - current_datetime >= timedelta(days=-30) and row['Data da próxima realização'] - current_datetime <= timedelta(days=0):
                return ['background-color: #FFD700'] * len(row)
            elif row['Data da próxima realização'] - current_datetime <= timedelta(days=-30):
                return ['background-color: #FFA07A'] * len(row)
            elif row['Data da próxima realização'] - current_datetime > timedelta(days=0):
                return ['background-color: #90EE90'] * len(row)
        
        self.table = self.table.style.apply(highlight_expired_dates, axis=1)
        self.table = self.table.format({
            'Data da próxima realização': '{:%d/%m/%Y}'
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