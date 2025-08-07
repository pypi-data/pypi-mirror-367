import matplotlib.pyplot as plt
import pandas as pd
from cnanalysis import CorrelationMat

def test_correlation_matrix_plot():
    # Manually override plt.show()
    df = pd.DataFrame({
        'math': [70, 80, 90, 85, 75],
        'reading': [65, 78, 88, 84, 74],
        'writing': [60, 79, 89, 83, 73]
    })

    cm = CorrelationMat(data=df)
    cm.plotCM()

# Only run if not imported
if __name__ == "__main__":
    test_correlation_matrix_plot()
