import pandas as pd
from cnanalysis import DistributionOutViz

def test_distribution_outviz_plot():
    # Sample DataFrame
    df = pd.DataFrame({
        'math': [65, 70, 80, 85, 90, 95, 100, 105, 110, 150],  # outlier at 150
        'reading': [60, 65, 70, 75, 80, 85, 90, 95, 100, 105]
    })

    # Create an instance of the visualizer
    viz = DistributionOutViz(
        data=df,
        num_cols=['math', 'reading'],
        bins=10,
        kde=True,
        histcolor='skyblue',
        boxcolor='lightgreen',
        y_label='Frequency',
        thresh=0,
        legend=True,
        figure=(12, 5)
    )

    # Plot the distribution and outliers
    viz.PlotDAO()

# Run the test manually (for visual inspection)
if __name__ == "__main__":
    test_distribution_outviz_plot()
