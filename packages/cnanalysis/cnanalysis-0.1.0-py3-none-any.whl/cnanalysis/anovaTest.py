import pandas as pd 
from scipy.stats import f_oneway

class AnovaTest:
    def __init__(self,
                 data:pd.DataFrame,
                 num_col:str,
                 cat_col:str
                 )->None:
        """
        Perform one-way ANOVA to test if there are significant differences
        in a numeric variable across groups defined by a categorical variable.

        Parameters
        ----------
        data : pd.DataFrame
            The input DataFrame.

        num_col : str
            The name of the numeric column (dependent variable).

        cat_col : str
            The name of the categorical column (grouping variable).
        """
        self.num_col=num_col
        self.cat_col=cat_col
        self.data=data[[self.num_col,self.cat_col]].dropna()
    def test(self)->dict:
        """
        Run the ANOVA test and return the results.

        Returns
        -------
        dict
            Dictionary containing F-statistic, p-value, and interpretation.
        """
        try :
            if self.num_col is None or self.cat_col is None:
                raise ValueError("Yours columns are None.")
            if self.cat_col not in self.data.columns or self.num_col not in self.data.columns:
                raise ValueError(f"One or both columns '{self.num_col}', '{self.cat_col}' not found in the DataFrame.")
            if not pd.api.types.is_numeric_dtype(self.data[self.num_col]):
                raise TypeError(f"The column {self.num_col} must be numeric.")
            if not pd.api.types.is_object_dtype(self.data[self.cat_col]):
                raise TypeError(f"The column : {self.cat_col} should be categorical.")
            return self._anova_test()
        except Exception as e:
            raise ValueError(f"Error occurred while testing : {e}")
        
    def _anova_test(self)->dict:
        
        groups=self.data.groupby(self.cat_col)[self.num_col].apply(list)
        f_stat,p_value=f_oneway(*groups)
        interpretation = "Significant difference" if p_value < 0.05 else "No significant difference"
        return {
            "F_statistic": round(f_stat,4),
            "P_value":round(p_value,4),
            "Interpretation":interpretation
        }