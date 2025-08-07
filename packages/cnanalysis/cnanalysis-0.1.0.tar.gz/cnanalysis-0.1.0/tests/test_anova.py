import pandas as pd
from cnanalysis import AnovaTest

def test_anova_result():
    df = pd.DataFrame({
        'group': ['A', 'A', 'B', 'B', 'C', 'C'],
        'score': [85, 90, 78, 82, 89, 94]
    })

    anova = AnovaTest(data=df, num_col='score', cat_col='group')
    result = anova.test()
    print(result)

test_anova_result()