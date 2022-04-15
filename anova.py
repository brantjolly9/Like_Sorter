from statistics import stdev, mean
import statsmodels.api as sm
from statsmodels.formula.api import ols
import numpy as np
import pandas as pd
import pingouin as po


dataframe = pd.read_csv('data.csv')
country1 = dataframe['Country1']
country2 = dataframe['Country2']
country3 = dataframe['Country3']
# a = po.anova(data=dataframe,between='Country1' )


for col in dataframe.columns:
    std = stdev(dataframe[col])
    m = mean(dataframe[col])
    print(m)
    print(std)
# print(dataframe)

# model = ols('model ~ Country1 + Country2 + Country3', data=dataframe).fit()
# result = sm.stats.anova_lm(model, type=2)
# print(result)
# o = sm.stats.anova_oneway(dataframe, groups=['Country1', 'Country2', 'Country3'])
# print(o)
