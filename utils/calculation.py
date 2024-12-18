import numpy as np

def calculate_entropy(column):
    value_counts = column.value_counts(normalize=True)  
    probabilities = value_counts.values  

    entropy = -np.sum(probabilities * np.log2(probabilities))
    return entropy

def calculate_gini_index(column):
    value_counts = column.value_counts(normalize=True)  
    probabilities = value_counts.values  

    gini_index = 1 - sum(probabilities ** 2)
    return gini_index

def icc(df, value, group):
    grand_mean = df[value].mean()  
    group_means = df.groupby(group)[value].mean()  

    ssb = sum(df.groupby(group).size() * (group_means - grand_mean) ** 2)

    ssw = sum((df[value] - df.groupby(group)[value].transform('mean')) ** 2)

    k = len(group_means)

    n = len(df)

    msb = ssb / (k - 1)
    msw = ssw / (n - k)

    icc = (msb - msw) / (msb + (k - 1) * msw)
    return icc