import pandas as pd
import re

def clean_data(bi_dataframe: pd.DataFrame) -> pd.DataFrame:
    bi_dataframe['Data'] = bi_dataframe['Data'].fillna(method='ffill')
    bi_dataframe.drop(['Ano', 'Mês'], axis=1, inplace=True)
    bi_dataframe.dropna(subset=['Código ID do Paciente'], inplace=True)

    bi_dataframe['Atividade Administrada preenchida pelo USUÁRIO'] = bi_dataframe['Atividade Administrada preenchida pelo USUÁRIO'].astype(str)
    bi_dataframe['Atividade Administrada'] = bi_dataframe['Atividade Administrada preenchida pelo USUÁRIO'].apply(lambda x: x.replace(',', '.') if re.match(r'\d+|\d+,\d+', x) else None)
    bi_dataframe['Atividade Administrada'] = bi_dataframe['Atividade Administrada'].apply(lambda x: None if re.search(r':', str(x)) else x)
    bi_dataframe['Atividade Administrada'] = bi_dataframe['Atividade Administrada'].astype(float)
    bi_dataframe.dropna(subset=['Atividade Administrada'], inplace=True)

    bi_dataframe['Idade do paciente'] = bi_dataframe['Idade do paciente'].astype(int)
    bi_dataframe['Código ID do Paciente'] = bi_dataframe['Código ID do Paciente'].astype(int)

    bi_dataframe.dropna(subset=['Peso (kg)'], inplace=True)

    bi_dataframe.drop(['Atividade Administrada NUMÉRICO', 'Atividade Administrada preenchida pelo USUÁRIO'], axis=1, inplace=True)

    bi_dataframe['Mês'] = bi_dataframe['Data'].dt.strftime('%B')
    month_translation = {
        'January': 'Janeiro',
        'February': 'Fevereiro',
        'March': 'Março',
        'April': 'Abril',
        'May': 'Maio',
        'June': 'Junho',
        'July': 'Julho',
        'August': 'Agosto',
        'September': 'Setembro',
        'October': 'Outubro',
        'November': 'Novembro',
        'December': 'Dezembro'
    }
    bi_dataframe['Mês'] = bi_dataframe['Mês'].map(month_translation)

    bi_dataframe['Ano'] = bi_dataframe['Data'].dt.year

    cleaned_bi = bi_dataframe.copy()[
        [
            "Data",
            "Ano",
            "Mês",
            "Código ID do Paciente",
            "Número do Prontuário",
            "Número da Solicitação do Exame",
            "Idade do paciente",
            "Sexo",
            "Nome Completo do Paciente",
            "Nome da definição do procedimento",
            "Nome do produto",
            "Avisos de administração",
            "Observações de administração",
            "Número de imagens e instâncias do estudo armazenadas no PACS",
            "Nome da sala",
            "Peso (kg)",
            "Atividade Administrada",
            "Atividade específica (mCi/kg)",
            "Dose (mSv)",
        ]
    ]
    
    return cleaned_bi