from datetime import timedelta
import pandas as pd
import pymongo
from pymongo.collection import Collection
from pymongo import MongoClient
import streamlit as st

from tests_periodicity import TestsPeriodicity
class Indicadores:
    def __init__(self, client: MongoClient, collection: Collection):
        self.client = client
        self.collection = collection

    @st.cache_data(ttl=timedelta(hours=1), show_spinner="Obtendo os dados...")
    def current_month_due(_self, query: dict) -> pd.DataFrame:
        """
        Retrieves the tests that are due in the current month based on the given query.

        Args:
            query (dict): The query to filter the tests.

        Returns:
            pd.DataFrame: A DataFrame containing the tests that are due in the current month.
        """
        tests_to_due = _self.collection.find(
            query,
            {"_id": 0, "Equipamento": 1, "Nome": 1, "Data da próxima realização": 1},
        ).sort("Data da próxima realização", pymongo.DESCENDING)
        df_tests_to_due = pd.DataFrame(list(tests_to_due))
        df_tests_to_due.drop_duplicates(
            subset=["Equipamento", "Nome"], keep="first", inplace=True
        )
        return df_tests_to_due

    @st.cache_data(ttl=timedelta(hours=1), show_spinner="Obtendo os dados...")
    def current_month_done(_self, query: dict) -> pd.DataFrame:
        """
        Retrieves and processes data for the current month.

        Args:
            query (dict): The query to filter the data.

        Returns:
            pd.DataFrame: A DataFrame containing the processed data.
        """
        tests_now = _self.collection.find(
            query, {"_id": 0, "Data da próxima realização": 0}
        ).sort("Data de realização", pymongo.DESCENDING)
        df_tests_now = pd.DataFrame(list(tests_now))
        df_tests_now.drop_duplicates(
            subset=["Equipamento", "Nome"], keep="first", inplace=True
        )
        return df_tests_now

    @staticmethod
    @st.cache_data(ttl=timedelta(hours=1), show_spinner="Processando os dados...")
    def get_tests_need_to_do(
        df_tests_to_due: pd.DataFrame, df_tests_now: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Returns a DataFrame containing the tests that need to be done based on the given data.

        Parameters:
        - df_tests_to_due (pd.DataFrame): DataFrame containing the tests that are due.
        - df_tests_now (pd.DataFrame): DataFrame containing the tests that are currently done.

        Returns:
        - pd.DataFrame: DataFrame containing the tests that need to be done and are done.

        """
        df_last_to_due_and_done = pd.merge(
            df_tests_to_due, df_tests_now, how="inner", on=["Equipamento", "Nome"]
        )
        tests_periodicity = TestsPeriodicity().full_list()
        df_last_to_due_and_done["not_done"] = True

        def get_keys_by_value(dict_obj, value):
            return [k for k, v in dict_obj.items() if v == value]

        monthyl_tests = get_keys_by_value(tests_periodicity, "Mensal")
        trimestral_tests = get_keys_by_value(tests_periodicity, "Trimestral")
        semestral_tests = get_keys_by_value(tests_periodicity, "Semestral")
        anual_tests = get_keys_by_value(tests_periodicity, "Anual")

        df_undone_monthly = df_last_to_due_and_done.iloc[
            df_last_to_due_and_done[
                df_last_to_due_and_done["Nome"].isin(monthyl_tests)
            ].index,
            :,
        ]
        df_undone_monthly["not_done"] = df_undone_monthly[
            "Data da próxima realização"
        ] - df_undone_monthly["Data de realização"] >= pd.Timedelta(days=29)
        df_undone_trimestral = df_last_to_due_and_done.iloc[
            df_last_to_due_and_done[
                df_last_to_due_and_done["Nome"].isin(trimestral_tests)
            ].index,
            :,
        ]
        df_undone_trimestral["not_done"] = df_undone_trimestral[
            "Data da próxima realização"
        ] - df_undone_trimestral["Data de realização"] >= pd.Timedelta(days=91)
        df_undone_semestral = df_last_to_due_and_done.iloc[
            df_last_to_due_and_done[
                df_last_to_due_and_done["Nome"].isin(semestral_tests)
            ].index,
            :,
        ]
        df_undone_semestral["not_done"] = df_undone_semestral[
            "Data da próxima realização"
        ] - df_undone_semestral["Data de realização"] >= pd.Timedelta(days=182)
        df_undone_anual = df_last_to_due_and_done.iloc[
            df_last_to_due_and_done[
                df_last_to_due_and_done["Nome"].isin(anual_tests)
            ].index,
            :,
        ]
        df_undone_anual["not_done"] = df_undone_anual[
            "Data da próxima realização"
        ] - df_undone_anual["Data de realização"] >= pd.Timedelta(days=366)

        df_last_to_due_and_done = pd.concat(
            [
                df_undone_monthly,
                df_undone_trimestral,
                df_undone_semestral,
                df_undone_anual,
            ]
        )

        return df_last_to_due_and_done

    @staticmethod
    def check_materials(df_tests_need_to_do: pd.DataFrame) -> pd.DataFrame:
        """
        Checks the materials required for performing tests and updates the DataFrame accordingly.

        Args:
            df_tests_need_to_do (pd.DataFrame): The DataFrame containing the tests that need to be done.

        Returns:
            pd.DataFrame: The updated DataFrame with a new column indicating if the test can be performed without the required materials.
        """
        df_tests_need_to_do["Sem material"] = False
        with st.sidebar:
            st.markdown("Materiais ausentes para realização dos testes:")
            materials = {}
            materials["Ga-67"] = st.toggle("Ga-67", value=True)
            materials["Tl-201"] = st.toggle("Tl-201", value=True)
            materials["I-131"] = st.toggle("I-131", value=False)

        if materials["Ga-67"] and materials["Tl-201"] and materials["I-131"]:
            df_tests_need_to_do["Sem material"] = df_tests_need_to_do["Nome"].apply(
                lambda x: (
                    True if "Ga-67" in x or "Tl-201" in x or "I-131" in x else False
                )
            )

        if materials["Ga-67"] and materials["Tl-201"] and not materials["I-131"]:
            df_tests_need_to_do["Sem material"] = df_tests_need_to_do["Nome"].apply(
                lambda x: True if "Ga-67" in x or "Tl-201" in x else False
            )

        if materials["Ga-67"] and not materials["Tl-201"] and materials["I-131"]:
            df_tests_need_to_do["Sem material"] = df_tests_need_to_do["Nome"].apply(
                lambda x: True if "Ga-67" in x or "I-131" in x else False
            )

        if not materials["Ga-67"] and materials["Tl-201"] and materials["I-131"]:
            df_tests_need_to_do["Sem material"] = df_tests_need_to_do["Nome"].apply(
                lambda x: True if "Tl-201" in x or "I-131" in x else False
            )

        if materials["Ga-67"] and not materials["Tl-201"] and not materials["I-131"]:
            df_tests_need_to_do["Sem material"] = df_tests_need_to_do["Nome"].apply(
                lambda x: True if "Ga-67" in x else False
            )

        if not materials["Ga-67"] and materials["Tl-201"] and not materials["I-131"]:
            df_tests_need_to_do["Sem material"] = df_tests_need_to_do["Nome"].apply(
                lambda x: True if "Tl-201" in x else False
            )

        if not materials["Ga-67"] and not materials["Tl-201"] and materials["I-131"]:
            df_tests_need_to_do["Sem material"] = df_tests_need_to_do["Nome"].apply(
                lambda x: True if "I-131" in x else False
            )

        return df_tests_need_to_do

    @staticmethod
    def calculate_indicadores(df_tests_need_to_do: pd.DataFrame) -> tuple:
        """
        Calculate indicators based on the given DataFrame.

        Parameters:
        - df_tests_need_to_do (pd.DataFrame): DataFrame containing test data.

        Returns:
        - tuple: A tuple containing the calculated indicators:
            - indicador_realizacao (float): Percentage of tests done.
            - indicador_arquivado (float): Percentage of tests done and archived.
            - total_to_do (int): Total number of tests to be done.
        """
        total = df_tests_need_to_do.query("`Sem material` == False").shape[0]
        total_done = df_tests_need_to_do.query(
            "not_done == False and `Sem material` == False"
        ).shape[0]
        total_to_do = total - total_done
        indicador_realizacao = total_done / total * 100

        total_done_and_archived = df_tests_need_to_do.query(
            "not_done == False and `Sem material` == False and Arquivado == True"
        ).shape[0]
        indicador_arquivado = total_done_and_archived / total * 100

        return (indicador_realizacao, indicador_arquivado, total_to_do)
