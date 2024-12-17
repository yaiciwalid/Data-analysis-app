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