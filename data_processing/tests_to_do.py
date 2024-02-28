import pandas as pd
from tests_periodicity import TestsPeriodicity
import pymongo
from pymongo.cursor import Cursor
from pymongo.collection import Collection
from datetime import datetime, timedelta
from typing import Tuple
import streamlit as st

@st.cache_data(ttl=timedelta(hours=1), show_spinner='Obtendo os dados...')
def current_month_due(_collection: Collection, query) -> pd.DataFrame:
    tests_to_due = _collection.find(query, {'_id': 0, 'Equipamento': 1, 'Nome': 1, 'Data da próxima realização': 1}).sort('Data da próxima realização', pymongo.DESCENDING)
    df_tests_to_due = pd.DataFrame(list(tests_to_due))
    df_tests_to_due.drop_duplicates(subset=['Equipamento', 'Nome'], keep='first', inplace=True)
    return df_tests_to_due

@st.cache_data(ttl=timedelta(hours=1), show_spinner='Obtendo os dados...')
def current_month_done(tests_to_due: pd.DataFrame, begin_period: datetime, end_period: datetime, _collection: Collection) -> Tuple[pd.DataFrame, list, list]:
    """
    Retrieves the tests that have been done in the current month.

    Args:
        tests_to_due (DataFrame): The dataframe containing the tests to be done.
        begin_period (datetime): The start date of the current month.
        end_period (datetime): The end date of the current month.
        collection (Collection): The MongoDB collection to query.

    Returns:
        Tuple[pd.DataFrame, list, list]: A tuple containing:
            - tests_to_do_current_month (pd.DataFrame): The tests that need to be done in the current month.
            - tests_done_current_month (list): The tests that have been done in the current month.
            - tests_to_due_current_month (list): The tests that are due in the current month.
    """
    tests_to_do_current_month = pd.DataFrame()
    tests_to_due_current_month = []
    tests_done_current_month = []
    # for test in tests_to_due:
    #     data_da_proxima_realizacao = test.pop('Data da próxima realização') # Armazenar a data de realização prevista para o teste
    #     tests_to_due_current_month.append(test)
    #     query = {
    #         "Data de realização": {
    #             "$gte": begin_period,
    #             "$lt": end_period
    #         },
    #         **test
    #     }
    #     result = _collection.find(query, {'_id': 0, 'Data da próxima realização': 0})
    #     test_done = pd.DataFrame(list(result))
        
    #     if not test_done.empty:
    #         # Ordenar os testes realizados por data de realização
    #         # O teste mais recente é o primeiro da lista
    #         test_done.sort_values(by='Data de realização', ascending=False, inplace=True)
    #         test_done['Data da próxima realização'] = data_da_proxima_realizacao
    #         test_done = test_done.iloc[[0]]
            
    #         # Verificar se o teste precisa ser realizado
    #         tests_periodicity = TestsPeriodicity().full_list()
    #         if tests_periodicity[test['Nome']] == 'Mensal':
    #             test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=29)
    #         elif tests_periodicity[test['Nome']] == 'Trimestral':
    #             test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=91)
    #         elif tests_periodicity[test['Nome']] == 'Semestral':
    #             test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=182)
    #         elif tests_periodicity[test['Nome']] == 'Anual':
    #             test_done['is_expired'] = (test_done['Data da próxima realização'] - test_done['Data de realização']) >= pd.Timedelta(days=366)            
            
    #         # Adicionar o teste que precisa ser realizado no mês corrente
    #         if test_done['is_expired'].values[0]:
    #             test_done.drop(columns='is_expired', inplace=True)
    #             tests_to_do_current_month = pd.concat([tests_to_do_current_month, test_done])
    #         else:
    #             tests_done_current_month.append(test_done.to_dict('records')[0])
    #     else:
    #         continue
            
    # return tests_to_do_current_month, tests_done_current_month, tests_to_due_current_month