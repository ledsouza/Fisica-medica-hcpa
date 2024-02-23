import pandas as pd
import numpy as np
import streamlit as st

def filters_archivation(dataframe: pd.DataFrame):
    
    
    equipamento = st.multiselect('Selecione o equipamento', dataframe['Equipamento'].unique(), default=dataframe['Equipamento'].unique())
    with st.expander('Selecione o nome do teste'):
        nome = st.multiselect('Selecione o nome do teste', dataframe['Nome'].unique(), default=dataframe['Nome'].unique(), label_visibility='hidden')
    periodo = st.date_input(
            label="Selecione o Período",
            min_value=dataframe["Data de realização"].min(),
            max_value=dataframe["Data de realização"].max(),
            value=(dataframe["Data de realização"].min(), dataframe["Data de realização"].max()),
    )
    try:
        start_date, end_date = periodo
    except:
        st.error("É necessário selecionar um período válido")
        st.stop()
    
    query = """
            Equipamento in @equipamento and \
            @periodo[0] <= `Data de realização` <= @periodo[1] and \
            Nome in @nome
    """
    
    filtered_df = dataframe.query(query)
    return filtered_df

def filters_bi(dataframe):
    dataframe['Atividade Administrada'] = dataframe['Atividade Administrada'].fillna(0.0)
    dataframe['Dose (mSv)'] = dataframe['Dose (mSv)'].fillna(0.0)
    dataframe['Peso (kg)'] = dataframe['Peso (kg)'].fillna(0.0)
    dataframe['Idade do paciente'] = dataframe['Idade do paciente'].fillna(0.0)
    
    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>Filtros</h1>", unsafe_allow_html=True)
        
        periodo = st.date_input(
            label="Selecione o Período",
            min_value=dataframe["Data"].min(),
            max_value=dataframe["Data"].max(),
            value=(dataframe["Data"].min(), dataframe["Data"].max()),
        )
        try:
            start_date, end_date = periodo
        except:
            st.error("É necessário selecionar um período válido")
            st.stop()
            
        atividade_administrada = st.slider('Selecione a Atividade Administrada', 
                                           0.0, dataframe['Atividade Administrada'].max(), 
                                           (0.0, dataframe['Atividade Administrada'].max()),
                                           help='O valor 0 representa a atividade administrada não preenchida pelo usuário')
        
        dose = st.slider('Selecione a Dose', 
                         0.0, dataframe['Dose (mSv)'].max(), 
                         (0.0, dataframe['Dose (mSv)'].max()),
                         help='O valor 0 representa a dose não preenchida pelo usuário')
        
        if 0.0 == dataframe['Peso (kg)'].max():
            st.error("Não há valores de peso preenchidos")
            peso = (0.0, 0.0)
        else:
            peso = st.slider('Selecione o Peso', 
                             0.0, dataframe['Peso (kg)'].max(), 
                             (0.0, dataframe['Peso (kg)'].max()),
                             help='O valor 0 representa o peso não preenchido pelo usuário')
            
        idade = st.slider('Selecione a Idade', 
                          0, dataframe['Idade do paciente'].max(), 
                          (0, dataframe['Idade do paciente'].max()),
                          help='O valor 0 representa a idade não preenchida pelo usuário')
        
        sexo = st.multiselect("Selecione o Sexo", dataframe['Sexo'].unique(), dataframe['Sexo'].unique())
        nome_sala = st.multiselect("Selecione a Sala", dataframe['Nome da sala'].unique(), dataframe['Nome da sala'].unique())
    

    query = """
    @periodo[0] <= Data <= @periodo[1] and \
    @atividade_administrada[0] <= `Atividade Administrada` <= @atividade_administrada[1] and \
    @dose[0] <= `Dose (mSv)` <= @dose[1] and \
    @peso[0] <= `Peso (kg)` <= @peso[1] and \
    @idade[0] <= `Idade do paciente` <= @idade[1] and \
    Sexo in @sexo and \
    `Nome da sala` in @nome_sala
    """
    
    filtered_df = dataframe.query(query)
    filtered_df['Atividade Administrada'] = filtered_df['Atividade Administrada'].replace(0.0, np.nan)
    filtered_df['Dose (mSv)'] = filtered_df['Dose (mSv)'].replace(0.0, np.nan)
    filtered_df['Peso (kg)'] = filtered_df['Peso (kg)'].replace(0.0, np.nan)
    filtered_df['Idade do paciente'] = filtered_df['Idade do paciente'].replace(0.0, np.nan)
    
    return filtered_df