## CNAnalysis
    CNAnalysis is a Python package for comprehensive statistical and exploratory data analysis (EDA). It provides tools for performing ANOVA, Chi-square tests, correlation matrices, outlier handling, encoding categorical features, and visualizing distributions.

## 📦 Installation
```bash
pip install cnanalysis
```
## 📚 Modules Overview
1. AnovaTest – One-Way ANOVA
    ```bash
    from cnanalysis import AnovaTest
    anova = AnovaTest(data=df, num_col='score',cat_col='group')
    result = anova.test()
    print(result)
    ```
2. ChiSquareTest – Chi-Square Test with Cramér’s V
    ```bash
    from cnanalysis import ChiSquareTest
    chi_test = ChiSquareTest(data=df, col1='gender', col2='purchase')
    result = chi_test.test()
    print(result)
    ```
3. CombineAnalysis – Grouped Bar Plots with Stats
    ```bash
    from cnanalysis import CombineAnalysis

    plotter = CombineAnalysis(data=df, number_col='sales', categorical_col='region')
    summary_df = plotter.PlotGroupedData()
    ```
4. CorrelationMat – Correlation Matrix Plot
    ```bash
    from cnanalysis import CorrelationMat

    corr = CorrelationMat(data=df)
    corr.plotCM()`
    ```
5. DescriptiveSAT – Descriptive Statistics + Outlier Count
    ```bash
    from cnanalysis import DescriptiveSAT

    desc = DescriptiveSAT(data=df)
    stats = desc.get_descriptive_statistics(columns=['height', 'weight'])
    print(stats)
    ```
6. DistributionOutViz – Histogram + Boxplot for Outlier 
    ```bash
    from cnanalysis import DistributionOutViz

    dist_viz = DistributionOutViz(data=df, num_cols=['price','income'])
    dist_viz.PlotDAO()

    ```
7. EncodeCat – Label, One-Hot, and Ordinal Encoding
    ```bash
    from cnanalysis import EncodeCat

    encoder = EncodeCat(data=df, method='label')
    encoded_df = encoder.encode()

    ```
8. HandleOutlier – Winsorization (Cap Outliers)
    ```bash
    from cnanalysis import HandleOutlier

    out = HandleOutlier(data=df, lower=0.05, upper=0.95)
    winsorized_df = out.winsorize()

    ```
9. CardinalityAndRareCategoryAnalyzer – Rare Category 
    ```bash
    from cnanalysis import CardinalityAndRareCategoryAnalyzer

    analyzer = CardinalityAndRareCategoryAnalyzer(data=df, thresh=0.01)
    report = analyzer.get_cardinality_n_rare_cat()
    print(report)

    ```

## 🧑‍💻 Author
**Roshan Kumar**<br>
**🎓 Student, B.Sc. in Computer Science and Data Analytics (CSDA)**<br>
**🏫 Indian Institute of Technology Patna (IITP)**<br>
**📧 rk1861303@gmail.com**

## 📝 License
This project is licensed under the MIT License – see the LICENSE file for details.