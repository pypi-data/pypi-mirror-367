import pandas as pd 
from typing import List, Union

class HandleOutlier:
    def __init__(self,
                 data:pd.DataFrame,
                 columns:Union[List[str],None]=None,
                 lower:Union[float,int]=0.05,
                 upper:Union[float,int]=0.95,
                 inplace : bool =False
                 )->None:
        """ Apply winsorization to numeric columns by capping values at specified quantiles.

            Parameters:
            ----------
            df : pd.DataFrame
                Input DataFrame containing numeric columns.

            columns : list of str
                List of column names to apply winsorization to.

            lower : float, optional (default=0.05)
                Lower quantile threshold (e.g., 0.05 means 5th percentile).

            upper : float, optional (default=0.95)
                Upper quantile threshold (e.g., 0.95 means 95th percentile).

            inplace : bool, optional (default=False)
                Whether to modify the DataFrame in-place.
        """
        self.data=data
        self.columns=columns
        self.lower=lower
        self.upper= upper
        self.inplace=inplace
    def winsorize(self)->pd.DataFrame:
        """
        Run the Handle Outlier  and return the results.

        Returns
        -------
        pd.DataFrame
            DataFrame with winsorized values (new or modified).
        """
        try :
            if not 0 <=self.lower < self.upper <=1:
                raise ValueError("Quantile bounds (Lower and upper) must be between 0 to 1")
            if not self.inplace:
                self.data =self.data.copy()
            if self.columns is None:
                self.columns = self._Allcolumns()
            
            for col in self.columns:
                if col not in self.data.columns:
                    raise ValueError(f"Column : '{col}' not found in DataFrame.")
                if not pd.api.types.is_numeric_dtype(self.data[col]):
                    raise TypeError(f"This column : '{col}' is not numeric,it should be numeric.")
                lower_bound =self.data[col].quantile(self.lower)
                upper_bound =self.data[col].quantile(self.upper)
                self.data[col]=self.data[col].clip(lower=lower_bound,upper=upper_bound)
            return self.data
        except Exception as e:
            raise ValueError(f"Error during Winsorization:{e}")
    def _Allcolumns(self)->List[str]:
        return self.data.select_dtypes(include=['number']).columns.to_list()