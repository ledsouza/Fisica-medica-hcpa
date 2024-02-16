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
    stylized_statistics = descritive_statistics.iloc[1:,:].style.format(
        {
            'Idade do paciente': '{:.0f}',
            'Peso': '{:.2f} kg',
            'Atividade Administrada': '{:.2f} mCi',
            'Atividade Específica': '{:.2f} mCi/kg',
            'Dose': '{:.2f} mSv'
        }, decimal=','
    )
    
    stylized_statistics.apply(lambda x: ['color: #3FA63C' if (x.name in ['Mediana', '3º Quartil'] and col in ['Atividade Administrada', 'Atividade Específica']) else '' for col in x.index], axis=1)
    stylized_statistics.set_table_styles([{
        'selector': 'td,th',
        'props': 'text-align: center;'
    }], overwrite=False)

    return stylized_statistics