import pandas as pd
from cnanalysis import DescriptiveSAT

def test_descriptive_sat_statistics_and_outliers():
    # Sample data
    df = pd.DataFrame({
        'math_score': [70, 80, 90, 100, 110, 120, 130, 140, 150, 300],  # last one is an outlier
        'reading_score': [65, 70, 72, 75, 78, 80, 82, 85, 88, 91]
    })

    # Initialize the class
    sat = DescriptiveSAT(data=df)

    # Select columns to analyze
    result = sat.get_descriptive_statistics(columns=['math_score', 'reading_score'])

    # Print result (optional)
    print(result)

test_descriptive_sat_statistics_and_outliers()