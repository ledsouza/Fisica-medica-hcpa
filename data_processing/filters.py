import numpy as np
import pandas as pd
import streamlit as st

def filters_bi(data):
    data['Atividade Administrada'] = data['Atividade Administrada'].fillna(0.0)
    data['Dose (mSv)'] = data['Dose (mSv)'].fillna(0.0)
    data['Peso (kg)'] = data['Peso (kg)'].fillna(0.0)
    data['Idade do paciente'] = data['Idade do paciente'].fillna(0.0)
    
    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>Filtros</h1>", unsafe_allow_html=True)
        
        periodo = st.date_input(
            label="Selecione o Período",
            min_value=data["Data"].min(),
            max_value=data["Data"].max(),
            value=(data["Data"].min(), data["Data"].max()),
        )
        try:
            start_date, end_date = periodo
        except:
            st.error("É necessário selecionar um período válido")
            st.stop()
            
        atividade_administrada = st.slider('Selecione a Atividade Administrada', 
                                           0.0, data['Atividade Administrada'].max(), 
                                           (0.0, data['Atividade Administrada'].max()),
                                           help='O valor 0 representa a atividade administrada não preenchida pelo usuário')
        
        dose = st.slider('Selecione a Dose', 
                         0.0, data['Dose (mSv)'].max(), 
                         (0.0, data['Dose (mSv)'].max()),
                         help='O valor 0 representa a dose não preenchida pelo usuário')
        
        if 0.0 == data['Peso (kg)'].max():
            st.error("Não há valores de peso preenchidos")
            peso = (0.0, 0.0)
        else:
            peso = st.slider('Selecione o Peso', 
                             0.0, data['Peso (kg)'].max(), 
                             (0.0, data['Peso (kg)'].max()),
                             help='O valor 0 representa o peso não preenchido pelo usuário')
            
        idade = st.slider('Selecione a Idade', 
                          0, data['Idade do paciente'].max(), 
                          (0, data['Idade do paciente'].max()),
                          help='O valor 0 representa a idade não preenchida pelo usuário')
        
        sexo = st.multiselect("Selecione o Sexo", data['Sexo'].unique(), data['Sexo'].unique())
        nome_sala = st.multiselect("Selecione a Sala", data['Nome da sala'].unique(), data['Nome da sala'].unique())
    

    query = """
    @periodo[0] <= Data <= @periodo[1] and \
    @atividade_administrada[0] <= `Atividade Administrada` <= @atividade_administrada[1] and \
    @dose[0] <= `Dose (mSv)` <= @dose[1] and \
    @peso[0] <= `Peso (kg)` <= @peso[1] and \
    @idade[0] <= `Idade do paciente` <= @idade[1] and \
    Sexo in @sexo and \
    `Nome da sala` in @nome_sala
    """
    
    filtered_data = data.query(query)
    filtered_data['Atividade Administrada'] = filtered_data['Atividade Administrada'].replace(0.0, np.nan)
    filtered_data['Dose (mSv)'] = filtered_data['Dose (mSv)'].replace(0.0, np.nan)
    filtered_data['Peso (kg)'] = filtered_data['Peso (kg)'].replace(0.0, np.nan)
    filtered_data['Idade do paciente'] = filtered_data['Idade do paciente'].replace(0.0, np.nan)
    
    return filtered_data