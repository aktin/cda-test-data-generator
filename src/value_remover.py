import pandas as pd
import numpy as np


class ValueRemover:
    @staticmethod
    def process_column(column: pd.Series, probability: float) -> pd.Series:
        """
        Remove elements from the column with a given probability.

        Args:
            column (pd.Series): The series of values from which elements will be removed.
            probability (float): The probability with which an element will be removed.

        Returns:
            pd.Series: A series with some elements replaced by an empty string based on the given probability.
        """
        return column.mask(np.random.random(len(column)) < probability, '')

    @classmethod
    def process_df(cls, df: pd.DataFrame, var_dict: dict) -> pd.DataFrame:
        """
        Remove values from the DataFrame based on the probabilities specified in var_dict.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            var_dict (dict): A dictionary where keys are concept IDs and values are tuples containing
                             information about each variable, including nullability and probability of missing values.

        Returns:
            pd.DataFrame: The DataFrame with values removed according to the specified probabilities.

        Raises:
            ValueError: If the probability is non-zero for a non-nullable concept ID or if the probability is not between 0 and 1.
        """
        for concept_id, (_, _, nullable, prob_missing) in var_dict.items():
            if nullable is False and prob_missing > 0:
                raise ValueError(
                    f"Probability of missing values is non-zero for a non-nullable conceptId: {concept_id}.")
            if prob_missing < 0 or prob_missing > 1:
                raise ValueError(f"Probability of missing values must be between 0 and 1 for conceptId: {concept_id}.")
            if nullable:
                df[concept_id] = cls.process_column(df[concept_id], prob_missing)
        return df
