import os

def get_results_csv_file():
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    results_dir = os.path.join(parent_dir, 'results')
    return os.path.join(results_dir, 'results.csv')