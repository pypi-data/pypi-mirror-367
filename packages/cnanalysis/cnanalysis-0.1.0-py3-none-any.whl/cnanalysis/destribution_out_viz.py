import pandas as pd
import matplotlib.pyplot as plt
from typing import List,Tuple
import seaborn as sns

class DistributionOutViz:
    def __init__(
        self,
        data:pd.DataFrame,
        num_cols:List[str],
        bins:int=50,
        kde:bool=True,
        histcolor:str="skyblue",
        boxcolor:str ="lightgreen",
        y_label:str="Frequency",
        thresh:float|int=0,
        legend:bool=True,
        figure:Tuple[int,int]=(12,6)
        ) -> None:
        self.data = data
        self.num_cols = num_cols
        self.bins = bins
        self.kde=kde
        self.Hcolor = histcolor
        self.Bcolor=boxcolor
        self.y_label = y_label
        self.thresh = thresh
        self.legend = legend
        self.figure=figure
    def PlotDAO(self) -> None:
        """ Plot Distribution and Outliers for Numerical Columns
        
        Parameters:
        data : pd.DataFrame
            The input DataFrame containing the data to be visualized.
        num_cols : List[str]
            A list of numerical column names in the DataFrame for which the distribution and outliers are to be plotted.
        bins : int, optional
            The number of bins to use for the histogram (default is 50).
        Histcolor : str, optional
            The color to use for the histogram bars (default is "skyblue").
        boxcolor : str, optional
            The color to use for the boxplot  (default is "lightgreen").
        y_label : str, optional
            The label for the y-axis (default is "Frequency").
        thresh : float|int, optional
            Threshold for outlier detection (default is 0, which means no threshold is applied).
        legend : bool, optional
            Whether to display the legend (default is True).
        figure_size :Tuple[int,int]
            figure size of graph.
        Returns:
        None
            Displays the distribution and outlier plots for the specified numerical columns.
        """
        try:
            if not isinstance(self.data, pd.DataFrame):
                raise ValueError("Input data must be a pandas DataFrame.")
            else:
                if not all(col in self.data.columns for col in self.num_cols):
                    raise ValueError("Some columns are not present in the DataFrame.")
                
                for col in self.num_cols:
                    plt.figure(figsize=self.figure)
                    sns.histplot(self.data[col], kde=self.kde, bins=self.bins, color=self.Hcolor,thresh=self.thresh,legend=self.legend)
                    plt.title(f'Distribution of {col}')
                    plt.xlabel(col)
                    plt.ylabel(self.y_label)
                    
                    # Plotting boxplot to visualize outliers
                    plt.subplot(1, 2, 2)
                    sns.boxplot(x=self.data[col].dropna(), color=self.Bcolor)
                    plt.title(f'Boxplot of {col}')
                    plt.xlabel(col)
                    plt.tight_layout()
                    plt.show()
        except Exception as e:
            print(f"An error occurred: {e}")
