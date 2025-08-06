# ben-memre/ben-memre/functions.py
import numpy as np

def greet(name):
    """This function greets the person passed in as a parameter."""
    return f"Hello, {name}! This is a message from ben-memre."

def add_numbers(x, y):
    """This function adds two numbers and returns the result."""
    return x + y

def normalize(data):
    """
    Scales a list or numpy array of numerical data to a 0-1 range.
    Useful for preparing data for machine learning models.
    """
    arr = np.array(data)
    if arr.min() == arr.max():
        return np.zeros_like(arr)
    return (arr - arr.min()) / (arr.max() - arr.min())

def one_hot_encode(labels):
    """
    Converts a list of categorical labels into a one-hot encoded format.
    """
    unique_labels = sorted(list(set(labels)))
    label_map = {label: i for i, label in enumerate(unique_labels)}
    num_classes = len(unique_labels)
    
    encoded = np.zeros((len(labels), num_classes))
    for i, label in enumerate(labels):
        encoded[i, label_map[label]] = 1
    return encoded

def calculate_accuracy(y_true, y_pred):
    """
    Calculates the classification accuracy.
    :param y_true: A list of true labels.
    :param y_pred: A list of predicted labels.
    :return: The accuracy score as a float.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    correct_predictions = np.sum(y_true == y_pred)
    return correct_predictions / len(y_true)
