import streamlit as st
import pandas as pd
import time
        
class FormMongoDB():
    def __init__(self, db) -> None:
        self.db = db
        self.collection = None
        self.list_tests_gc_periodicity = self._set_gc_tests()
        self.list_tests_pet_periodicity = self._set_pet_tests()
        
    def _set_gc_tests(self):
        list_tests_gc_periodicity = {
            'Uniformidade intrínseca para alta densidade de contagem': 'Mensal',
            'Resolução e linearidade espacial intrínseca': 'Mensal',
            'Centro de rotação': 'Mensal',
            'Resolução energética': 'Semestral',
            'Taxa máxima de contagem': 'Semestral',
            'Resolução espacial para fontes multi-energética': 'Semestral',
            'Corregistro espacial para fontes multi-energéticas': 'Semestral',
            'Sensibilidade planar': 'Semestral',
            'Uniformidade extrínseca para alta densidade de contagem': 'Semestral',
            'Velocidade da mesa em varreduras de corpo inteiro': 'Semestral',
            'Desempenho geral SPECT': 'Semestral',
            'Uniformidade para nuclídeos diferentes de Tc-99m': 'Anual',
            'Uniformidade intrínseca com janelas energéticas assimétricas': 'Anual',
            'Resolução e linearidade espacial extrínseca': 'Anual'
        }
        return list_tests_gc_periodicity
    
    def _set_pet_tests(self):
        list_tests_pet_periodicity = {
            'Uniformidade e verificação da calibração do sistema PET-CT': 'Mensal',
            'Normalização e Calibração cruzada': 'Trimestral',
            'Resolução espacial': 'Semestral',
            'Sensibilidade': 'Semestral',
            'Corregistro das imagens de PET e CT': 'Semestral',
            '''Desempenho da taxa de contagens (NECR), 
            taxa de eventos aleatórios, espalhados e verdadeiros, 
            fração de espalhamento e 
            exatidão das correções de eventos aleatórios e de perda de contagens''': 'Anual',
            'Desempenho geral e exatidão das correções de atenuação e espalhamento': 'Anual',
        }
        return list_tests_pet_periodicity
    
    def _set_curiometro_tests(self):
        list_tests_curiometro_periodicity = {
            'Reprodutibilidade': 'Mensal',
            'Precisão e exatidão': 'Semestral',
            'Linearidade': 'Semestral',
            'Geometria': 'Anual'
        }
        return list_tests_curiometro_periodicity
    
    def _next_test(self, name, date):
        list_tests_periodicity = {**self.list_tests_gc_periodicity, **self.list_tests_pet_periodicity}
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
                    test['Nome'] = st.selectbox('Nome do Teste', list(self.list_tests_gc_periodicity.keys()), key=type_form + '_nome')
                elif test['Equipamento'] == 'FMMNPETCT':
                    test['Nome'] = st.selectbox('Nome do Teste', list(self.list_tests_pet_periodicity.keys()), key=type_form + '_nome')
                    
                test['Data de realização'] = pd.to_datetime(st.date_input('Data de realização'), format='DD/MM/YYYY')
                
                submit_label = 'Remover teste' if type_form == 'removal' else 'Inserir Teste'
                submit_button = st.form_submit_button(label=submit_label)
                if submit_button:
                    test['Data da próxima realização'] = self._next_test(test['Nome'], test['Data de realização'])
                    test['Arquivado'] = False
                    
                    test['Data de realização'] = test['Data de realização'].strftime('%d/%m/%Y')
                    test['Data da próxima realização'] = test['Data da próxima realização'].strftime('%d/%m/%Y')
                    
                    self.collection = self.db['testes']
                    if type_form == 'registration':
                        insert_status = self.collection.insert_one(test)
                        if insert_status.acknowledged:
                            st.success('Teste inserido com sucesso!')
                            time.sleep(1)
                            st.rerun()
                    elif type_form == 'removal':
                        removal_status = self.collection.delete_one(test)
                        if removal_status.deleted_count > 0:
                            st.success('Teste removido com sucesso!')
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error('Erro ao remover o teste!')
                    else:
                        raise ValueError('Invalid type_form')
                    
        