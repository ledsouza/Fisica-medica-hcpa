import pandas as pd
import streamlit as st

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
        'Peso': '{:.2f} kg',
        'Dose': '{:.2f} mSv'
    }, decimal=',')
    
    return tableviz_bi