import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 
from typing import Tuple,Union

class CombineAnalysis:
    def __init__(self,
                 data:pd.DataFrame,
                 number_col:str,
                 categorical_col:str,
                 figure_size:Tuple[int,int]=(12,6),
                 rotation:int=90,
                palette : Union[str,list,dict]="Blues_d",
                group_stats :str ="mean"
                 )->None:
        """
            Group a numerical column by a categorical column and display summary statistics
            (mean, median, std, count) with a bar plot of group means.

            Parameters:
            ----------
            df : pd.DataFrame
                The input DataFrame containing the data.

            num_col : str
                The name of the numeric column to aggregate.

            cat_col : str
                The name of the categorical column to group by.
            figure_size :Tuple[int,int]
                figure size of graph.
            rotation : int
                Adjust the rotation of name of x-axis (default it is set to  90 )
            palette : str | list | dict, optional
                Color palette for the plot, by default "Blues_d".
            group_stats : str, optional
                Which statistic to plot on the bar chart (e.g., "mean", "median", "std","count"), by default "mean".
            Returns:
            -------
            pd.DataFrame
                A DataFrame containing grouped summary statistics.
        """
        self.num_col=number_col
        self.cat_col=categorical_col
        self.data=data[[self.num_col,self.cat_col]].dropna()
        self.figure=figure_size
        self.rot=rotation
        self.palette=palette
        self.grp_stats=group_stats.lower()

    def PlotGroupedData(self)->pd.DataFrame:
        try :
            if self.num_col is None or self.cat_col is None:
                raise ValueError("Yours columns are None.")
            if self.num_col not in self.data.columns or self.cat_col not in self.data.columns:
                raise ValueError(f"One or both columns : [{self.num_col} and {self.cat_col}] ,are not found in data ")
            grouped=self.data.groupby(self.cat_col)[self.num_col].agg(['mean','median','std','count'])
            if self.grp_stats not in grouped.columns:
                raise ValueError(f"Invalid group_stats '{self.grp_stats}'. Must be one of {list(grouped.columns)}.")
            #plot figure
            plt.figure(figsize=self.figure)
            sns.barplot(x=grouped.index,y=grouped[self.grp_stats],palette=self.palette)
            plt.xlabel(self.cat_col)
            plt.ylabel(f"{self.grp_stats.capitalize()} of {self.num_col}")
            plt.xticks(rotation=self.rot,ha="right")
            plt.title(f"{self.grp_stats.capitalize()} of '{self.num_col}' by '{self.cat_col}'")
            plt.tight_layout()
            plt.show()
            return grouped
        except ValueError as e:
            raise ValueError(f"Error in  PlotGroupedData :{e}")