import pandas as pd 
import numpy as np 
from scipy.stats import chi2_contingency

class ChiSquareTest:
    def __init__(self, 
                 data:pd.DataFrame,
                 col1:str,
                 col2:str)->None:
        
        """Perform a chi-sqaure test of independence between two categorical variable
        Also computes Cramer's V to measure the strenght of association.
        
        Parameters:
        data :pd.DataFrame
            Input DataFrame containing the categorical variable.
        col1: str
            Name of the first categorical column.
        col2 : str
            Name of the second categorical column.
        Returns:
        
        dict:
            Dictionary containing Chi-square statistic, p-value, degrees of freedom,
            Cramér's V value, and an interpretation of association strength.
        """
        self.data=data
        self.col1 = col1
        self.col2 = col2
    def test(self) -> dict:
        try:
            if self.col1 is None or self.col2 is None:
                raise ValueError("Yours columns are None.")
            if self.col1 not in self.data.columns or self.col2 not in self.data.columns:
                raise ValueError(f"One or both columns : [{self.col1} and {self.col2}] ,are not found in data ")
            df = self.data[[self.col1,self.col2]].dropna()
            #contigency table
            cont_table= pd.crosstab(df[self.col1],df[self.col2])
            
            chi2,p_val,dof,expected =chi2_contingency(cont_table)
            n= cont_table.sum().sum()
            
            min_dim =min(cont_table.shape) -1
            cramers_v=np.sqrt((chi2/n)/min_dim) if min_dim > 0 else np.nan
            return self._cramers_v_result(cramers_v,chi2,p_val,dof)
        except Exception as e:
            raise ValueError(f"Error :{e}")
    def _cramers_v_result(self,
                    cramers_v:float = None,
                    chi2:float = None,
                    p_value:float = None,
                    dof:float=None
                    ) -> dict:
        """
        Thresholds for Cramér’s V:

            ≥ 0.25 → Strong

            ≥ 0.10 → Moderate

            ≥ 0.05 → Weak

            < 0.05 → Negligible
        """
        if cramers_v >= 0.25:
            association = "Strong association"
        elif cramers_v >= 0.10:
            association = "Moderate association"
        elif cramers_v >=0.05:
            association ="Weak association"
        else:
            association = "Negligible association"
        return {
            "Chi2_statistic":round(chi2,4),
            "P_value" : round(p_value,4),
            "Deegree of freedom":dof,
            "Cramers_v": round(cramers_v,4),
            "Interpretation":association
        }