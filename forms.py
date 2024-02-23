import streamlit as st
import pandas as pd
import time
from tests_periodicity import TestsPeriodicity
        
class FormMongoDB():
    def __init__(self, client) -> None:
        self.client = client
        self.db = client['cq_gestao']
        self.collection = None
        self.tests_periodicity = TestsPeriodicity()
    
    def _next_test(self, name, date):
        list_tests_periodicity = self.tests_periodicity.full_list()
        periodicity = list_tests_periodicity[name]
        if periodicity == 'Mensal':
            return date + pd.DateOffset(months=1)
        elif periodicity == 'Trimestral':
            return date + pd.DateOffset(months=3)
        elif periodicity == 'Semestral':
            return date + pd.DateOffset(months=6)
        elif periodicity == 'Anual':
            return date + pd.DateOffset(years=1)
        
    def form_widget(self, type_form):
        """
        Creates a form widget for inserting or removing a test.

        Parameters:
        - type_form (str): The type of form, either 'registration' or 'removal'.

        Returns:
        None
        """
        test = {}
        self.collection = self.db['equipamentos']
        equipamentos = self.collection.find({}, {'_id': 0, 'Identificação': 1})
        
        
        with st.container(border=True):
            test['Equipamento'] = st.selectbox('Equipamento', [equipamento['Identificação'] for equipamento in equipamentos], key=type_form + '_equipamento')
            
            with st.form(key=type_form, clear_on_submit=True, border=False):
                
                if test['Equipamento'] in ['FMMNINFINIA', 'FMMNMILLENNIUM', 'FMMNVENTRI']:
                    test['Nome'] = st.selectbox('Nome do Teste', list(self.tests_periodicity.list_tests_gc_periodicity.keys()), key=type_form + '_nome')
                elif test['Equipamento'] == 'FMMNPETCT':
                    test['Nome'] = st.selectbox('Nome do Teste', list(self.tests_periodicity.list_tests_pet_periodicity.keys()), key=type_form + '_nome')
                elif test['Equipamento'] in ['GM 1', 'GM 2', 'GM 3', 'GM 4', 'GM 5']:
                    test['Nome'] = st.selectbox('Nome do Teste', list(self.tests_periodicity.list_tests_gm_periodicity.keys()), key=type_form + '_nome')
                elif test['Equipamento'] in ['Gamma Probe Verde', 'Gamma Probe Amarela', 'Gamma Probe Branca']:
                    test['Nome'] = st.selectbox('Nome do Teste', list(self.tests_periodicity.list_tests_gp_periodicity.keys()), key=type_form + '_nome')
                elif test['Equipamento'] in ['Curiômetro MN', 'Curiômetro PET']:
                    test['Nome'] = st.selectbox('Nome do Teste', list(self.tests_periodicity.list_tests_curiometro_periodicity.keys()), key=type_form + '_nome')
                    
                test['Data de realização'] = pd.to_datetime(st.date_input('Data de realização'), format='DD/MM/YYYY')
                
                submit_label = 'Remover teste' if type_form == 'removal' else 'Inserir teste'
                submit_button = st.form_submit_button(label=submit_label)
                if submit_button:
                    test['Data da próxima realização'] = self._next_test(test['Nome'], test['Data de realização'])
                    test['Arquivado'] = False
                    
                    test['Data de realização'] = test['Data de realização']
                    test['Data da próxima realização'] = test['Data da próxima realização']
                    
                    self.collection = self.db['testes']
                    if type_form == 'registration':
                        # Removing 'Arquivado' key to check if the test is already inserted
                        check_test = test.fromkeys(['Equipamento', 'Nome', 'Data de realização'])
                        check_test['Equipamento'] = test['Equipamento']
                        check_test['Nome'] = test['Nome']
                        check_test['Data de realização'] = test['Data de realização']
                        if self.collection.find_one(test) is not None:
                            st.error('Teste já inserido!')
                            self.client.close()
                        else:
                            insert_status = self.collection.insert_one(test)
                            if insert_status.acknowledged:
                                st.success('Teste inserido com sucesso!')
                                time.sleep(1)
                                self.client.close()
                                st.rerun()
                    elif type_form == 'removal':
                        removal_status = self.collection.delete_one(test)
                        if removal_status.deleted_count > 0:
                            st.success('Teste removido com sucesso!')
                            time.sleep(1)
                            self.client.close()
                            st.rerun()
                        else:
                            st.error('Erro ao remover o teste!')
                    else:
                        raise ValueError('Invalid type_form')
                    
        