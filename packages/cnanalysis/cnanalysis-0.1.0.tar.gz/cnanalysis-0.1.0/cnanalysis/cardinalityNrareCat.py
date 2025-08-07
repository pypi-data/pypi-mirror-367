import pandas as pd 
class CardinalityAndRareCategoryAnalyzer:
    def __init__(self,
                 data:pd.DataFrame,
                 cat_cols:list[str]=None,
                 thresh:float|int=0.01
                 )-> None:
        """
        Initialize the analyzer with data, categorical column names, and rare category threshold.

        Parameters
        ----------
        data : pd.DataFrame
            Input DataFrame.

        cat_cols : list of str, optional
            List of categorical columns to analyze. If None, auto-detected.

        thresh : float or int, default=0.01
            Threshold (as a fraction) below which a category is considered rare.
        """
        self.data = data
        self.cat_cols = cat_cols   
        self.thresh = thresh

    def get_cardinality_n_rare_cat(self) -> pd.DataFrame:
        
        """
            Analyze the cardinality and rare category distribution of categorical columns in a DataFrame.

            Parameters:
            ----------
            df : pd.DataFrame
                Input DataFrame containing the categorical features.

            categorical_columns : list of str
                List of categorical column names to analyze.

            rare_threshold : float, optional (default=0.01)
                Threshold below which a category is considered rare (as a fraction of total).

            Returns:
            -------
            pd.DataFrame
                A DataFrame summarizing the number of unique values, rare categories,
                and suggestions for each categorical column.
        """
        report={}
        try:
            if self.cat_cols is None:
                self.cat_cols =self.data.select_dtypes(include=['object','category']).columns.tolist()
            if not self.cat_cols:
                raise ValueError("No categorical columns found in the DataFrame.")
            for col in self.cat_cols:
                if col not in self.data.columns:
                    raise ValueError(f"Column '{col}' not found in the DataFrame.")
                unique_values = self.data[col].dropna().nunique()
                freq_dist =self.data[col].dropna().value_counts(normalize=True)
                rare_categories = freq_dist[freq_dist < self.thresh].index.tolist()
                report[col] = {
                    'unique_values': unique_values,
                    'rare_categories': rare_categories,
                    'suggestion': self._suggest_rare_category_handling(rare_categories)
                }
            return pd.DataFrame(report).T
        except Exception as e:
            raise ValueError(f"An error occurred while analyzing categorical columns: {e}")
    def _suggest_rare_category_handling(self, rare_categories: list[str]) -> str:
        """
        Suggest handling for rare categories based on their count.

        Parameters:
        ----------
        rare_categories : list of str
            List of rare category names.

        Returns:
        -------
        str
            Suggestion for handling rare categories.
        """
        if not rare_categories:
            return "No rare categories found."
        else:
            return "Drop or bin rare categories" if rare_categories else "OK"