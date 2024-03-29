import pandas as pd
import re

class DataCleaning:
    
    def __init__(self, bi_dataframe: pd.DataFrame):
        self.bi_dataframe = bi_dataframe
        
    def _fill_data(self):
        self.bi_dataframe['Data'] = self.bi_dataframe['Data'].ffill()
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
        
    def _cleaning_sala_nao_definida(self):
        self.bi_dataframe['Nome da sala'] = self.bi_dataframe['Nome da sala'].replace('Nao_definida', 'Não definida').replace('NOT SPECIFIED', 'Não definida')
        
    def _convert_to_correct_type(self):
        self.bi_dataframe['Idade do paciente'] = self.bi_dataframe['Idade do paciente'].astype(int)
        self.bi_dataframe['Código ID do Paciente'] = self.bi_dataframe['Código ID do Paciente'].astype(str).replace('\.0', '', regex=True)
        self.bi_dataframe['Número do Prontuário'] = self.bi_dataframe['Número do Prontuário'].astype(str).replace('\.0', '', regex=True)
        self.bi_dataframe['Peso (kg)'] = self.bi_dataframe['Peso (kg)'].astype(float)
        self.bi_dataframe['Número de imagens e instâncias do estudo armazenadas no PACS'] = self.bi_dataframe['Número de imagens e instâncias do estudo armazenadas no PACS'].astype(int)
        
    def _drop_na(self):
        self.bi_dataframe.dropna(subset=['Código ID do Paciente'], inplace=True)
        self.bi_dataframe.dropna(subset=['Atividade Administrada'], inplace=True)
        
    def _drop_columns(self):
        self.bi_dataframe.drop(['Atividade Administrada NUMÉRICO', 'Atividade Administrada preenchida pelo USUÁRIO'], axis=1, inplace=True) 

    def _remove_outliers(self):
        self.bi_dataframe = self.bi_dataframe[self.bi_dataframe['Peso (kg)'].isna() | (self.bi_dataframe['Peso (kg)'] <= 200)]
        self.bi_dataframe = self.bi_dataframe[self.bi_dataframe['Peso (kg)'].isna() | (self.bi_dataframe['Peso (kg)'] >= 30)]
    
    def _replace_sexo(self):
        self.bi_dataframe['Sexo'] = self.bi_dataframe['Sexo'].replace('M', 'Masculino').replace('F', 'Feminino')
    
    def clean_data(self):
        self._fill_data()
        self._cleaning_atividade_administrada()
        self._cleaning_sala_nao_definida()
        self._drop_na()
        self._convert_to_correct_type()
        self._drop_columns()
        self._remove_outliers()
        self._replace_sexo()

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