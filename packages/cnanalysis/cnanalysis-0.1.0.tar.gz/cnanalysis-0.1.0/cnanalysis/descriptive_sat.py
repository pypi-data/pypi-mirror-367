import pandas as pd 
from typing import List

class DescriptiveSAT:
    def __init__(self,data:pd.DataFrame)-> None:
        self.data = data
    def get_descriptive_statistics(self, columns: List[str]) ->pd.DataFrame:
        """
        The descriptive_analysis function performs a detailed statistical summary and outlier analysis on selected numerical columns of a DataFrame.
        
        This includes summary statistics,skewness, kurtosis, and outlier detection using the IQR method.
        
        Paarameters:
        data : pd.DataFrame
            The input DataFrame containing the data to be analyzed.
        columns : List[str]
            A list of column names in the DataFrame for which the descriptive statistics are to be computed.
        Returns:
        pd.DataFrame
            A dataframe containing descriptive statistics for the specified columns, 
            including count, mean, std, min, 25%, 50%, 75%, max, skewness, kurtosis, and outlier detection.
        """
        self.columns = columns
        stats_df = self.data[self.columns].describe(percentiles=[0.25,0.5,0.75,0.95,0.99])
        stats_df.loc["skewness"]=self.data[self.columns].skew()
        stats_df.loc["kurtosis"]=self.data[self.columns].kurtosis()
        
        # Detect outlier using IQR method
        outlier_dect=self._detect_outliers(self.data, self.columns)
        outlier_count= outlier_dect.sum().rename("outlier_count")
        stats_df = pd.concat([stats_df, outlier_count.to_frame().T])
        return stats_df
        
    def _detect_outliers(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Detects outliers in the numerical columns of the DataFrame using the IQR method.
        
        Parameters:
        data : pd.DataFrame
            The input DataFrame containing the data to be analyzed.
        columns : List[str]
            A list of column names in the DataFrame for which outliers are to be detected.
        """
        q1=data[columns].quantile(0.25)
        q3=data[columns].quantile(0.75)
        IQR=q3-q1
        outlier_dect =((data[columns]< (q1 - 1.5 *IQR)) | (data[columns] > (q3 + 1.5 * IQR)))
        return outlier_dect