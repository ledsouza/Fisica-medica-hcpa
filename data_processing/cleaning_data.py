import pandas as pd
import re

class DataCleaning:
    
    def __init__(self, bi_dataframe: pd.DataFrame):
        self.bi_dataframe = bi_dataframe
        
    def _fill_data(self):
        self.bi_dataframe['Data'] = self.bi_dataframe['Data'].fillna(method='ffill')
        self.bi_dataframe.drop(['Ano', 'Mês'], axis=1, inplace=True)
        self.bi_dataframe['Mês'] = self.bi_dataframe['Data'].dt.strftime('%B')
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
        self.bi_dataframe['Mês'] = self.bi_dataframe['Mês'].map(month_translation)
        self.bi_dataframe['Ano'] = self.bi_dataframe['Data'].dt.year
        
    def _cleaning_atividade_administrada(self):
        self.bi_dataframe['Atividade Administrada preenchida pelo USUÁRIO'] = self.bi_dataframe['Atividade Administrada preenchida pelo USUÁRIO'].astype(str)
        self.bi_dataframe['Atividade Administrada'] = (self.bi_dataframe['Atividade Administrada preenchida pelo USUÁRIO']
                                                       .apply(lambda x: str(x).replace(',', '.') if re.match(r'^\d*\,?\d*$', str(x)) else None))
        self.bi_dataframe['Atividade Administrada'] = self.bi_dataframe['Atividade Administrada'].astype(float)
        
    def _convert_to_correct_type(self):
        self.bi_dataframe['Idade do paciente'] = self.bi_dataframe['Idade do paciente'].astype(int)
        self.bi_dataframe['Código ID do Paciente'] = self.bi_dataframe['Código ID do Paciente'].astype(int)
        self.bi_dataframe['Peso (kg)'] = self.bi_dataframe['Peso (kg)'].astype(float)   
        
    def _drop_na(self):
        self.bi_dataframe.dropna(subset=['Código ID do Paciente'], inplace=True)
        self.bi_dataframe.dropna(subset=['Atividade Administrada'], inplace=True)
        self.bi_dataframe.dropna(subset=['Peso (kg)'], inplace=True)
        
    def _drop_columns(self):
        self.bi_dataframe.drop(['Atividade Administrada NUMÉRICO', 'Atividade Administrada preenchida pelo USUÁRIO'], axis=1, inplace=True) 

    def clean_data(self):
        self._fill_data()
        self._cleaning_atividade_administrada()
        self._drop_na()
        self._convert_to_correct_type()
        self._drop_columns()

        cleaned_bi = self.bi_dataframe.copy()[
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