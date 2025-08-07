import pandas as pd
from cnanalysis import HandleOutlier

def test_handle_outlier_basic_and_auto_columns():
    # Sample data with clear outliers
    df = pd.DataFrame({
        'math': [45, 50, 55, 60, 65, 1000],       # 1000 is an upper outlier
        'science': [70, 72, 74, 76, 78, -999]     # -999 is a lower outlier
    })

    print("Original DataFrame:")
    print(df)

    # 1️⃣ Winsorize specific columns
    handler_specific = HandleOutlier(
        data=df.copy(),
        columns=['math', 'science'],
        lower=0.05,
        upper=0.95,
        inplace=False
    )
    result_specific = handler_specific.winsorize()
    print("\nWinsorized DataFrame (specified columns):")
    print(result_specific)

    # 2️⃣ Winsorize all numeric columns (auto-detected)
    handler_auto = HandleOutlier(
        data=df.copy(),
        columns=None,  # auto-detect numeric columns
        lower=0.05,
        upper=0.95,
        inplace=False
    )
    result_auto = handler_auto.winsorize()
    print("\nWinsorized DataFrame (auto-detected columns):")
    print(result_auto)

# Run manually
if __name__ == "__main__":
    test_handle_outlier_basic_and_auto_columns()
