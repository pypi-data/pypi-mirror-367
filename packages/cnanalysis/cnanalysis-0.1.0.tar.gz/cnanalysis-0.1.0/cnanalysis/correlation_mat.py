import seaborn as sns 
import matplotlib.pyplot as plt 
import pandas as pd 
from typing import Tuple
class CorrelationMat:
    def __init__(
        self, 
        data: pd.DataFrame, 
        method: str = 'pearson',
        annot: bool = True,
        square: bool = True,
        linewidths: float = 0.5,
        cbar_kws: dict = {"shrink": .75},
        rotation: int = 45,
        ha: str = 'right',
        camera: str = 'coolwarm',
        title_fontsize: int = 14,
        figure_size:Tuple[int,int]=(10,8)
        ) -> None:
        
        self.data = data
        self.method = method
        self.annot = annot
        self.square = square
        self.linewidths = linewidths
        self.cbar_kws = cbar_kws
        self.rotation = rotation
        self.ha = ha
        self.fontsize = title_fontsize
        self.figure=figure_size
        if camera not in ['coolwarm', 'viridis', 'plasma', 'inferno', 'magma']:
            raise ValueError("Invalid camera value. Choose from 'coolwarm', 'viridis', 'plasma', 'inferno', or 'magma'.")
        self.camera = camera
    def plotCM(self)->None:
        """
            Plot a heatmap of the correlation matrix for selected numeric columns.

            Parameters:
            ----------
            data : pd.DataFrame
                The input DataFrame.

            method : str, optional (default='spearman')
                Correlation method to use: 'pearson', 'spearman', or 'kendall'.
            annot : bool, optional (default=True)
                Whether to annotate the heatmap with correlation coefficients.
            square : bool, optional (default=True)
                Whether to make the heatmap squares.
            linewidths : float, optional (default=0.5)
                Width of the lines that will divide each cell.
            cbar_kws : dict, optional (default={"shrink": .75})
                Keyword arguments for the color bar.
            rotation : int, optional (default=45)
                Rotation angle for x-axis labels.
            ha : str, optional (default='right')
                Horizontal alignment for x-axis labels.
            camera : str, optional (default='coolwarm') use any of 'coolwarm', 'viridis', 'plasma', 'inferno', 'magma'
                Color map for the heatmap.
            figure_size :Tuple[int,int]
                figure size of graph.
            Returns:
            -------
            None
                Displays the heatmap plot.
        """
    
        selected_columns = self.data.select_dtypes(include=['number']).columns.tolist()
        try:
            if not selected_columns:
                raise ValueError("No numeric columns found in the DataFrame.")
            corr_matrix = self.data[selected_columns].corr(method=self.method)
            plt.figure(figsize=self.figure)
            sns.heatmap(corr_matrix, annot=self.annot, fmt=".2f", 
                        cmap=self.camera, square=self.square, 
                        linewidths=self.linewidths,
                        cbar_kws=self.cbar_kws)
            plt.title(f'Correlation Matrix ({self.method.capitalize()} method)',fontsize=self.fontsize)
            plt.xticks(rotation=self.rotation, ha=self.ha)
            plt.yticks(rotation=0)
            plt.tight_layout()
            plt.show()
        except ValueError as e:
            print(f"Error: {e}")