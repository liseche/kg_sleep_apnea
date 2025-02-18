"""Script to calculate performance of NER"""
import pandas as pd
import argparse
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import random
import numpy as np

annotation_labels = ["SYMPTOM", "CONDITION", "RISKFACTOR", "TEST", "TREATMENT", "OUTCOME", "CONCEPT", "DOCUMENT"]

annotated_lines_icsd3 = [
    [18835, 21250],
    [22416, 22742],
    [25168, 25995],
    [26277, 26434],
    [27743, 28324],
    [28875, 29003],
    [30922, 31266],
    [31413, 31489],
    [32394, 32820],
    [33090, 33197],
    [35077, 35522],
    [35844, 35879],
    [36851, 37206],
    [37311, 37631],
    [39394, 40004],
    [40319, 40385],
    [41074, 41431],
    [41680, 41790],
    [42580, 42915],
    [43186, 43443]
]

def make_dataframe(filepath):
    with open(filepath, "r") as f:
        lines = [line.strip().split("\t") for line in f]
        max_cols = max(len(line) for line in lines)
        standardized_lines = [line + [""] * (max_cols - len(line))for line in lines]
        df = pd.DataFrame(standardized_lines)
    return df

def make_dataframes(gold, file_list, index_ranges):
    df_list = []
    for file in file_list:
        df_list.append(make_dataframe(file))
        
    gold_df = make_dataframe(gold)
    
    # we have all the dataframes. Now reduce them to the annotated parts
    filtered_df_list = []
    for df in df_list:
        subsets = []
        for indices in index_ranges:
            i = indices[0]
            j = indices[1]
            subsets.append(df.iloc[i:j+1])
        filtered_df_list.append(pd.concat(subsets))
    
    gold_subsets = []
    for indices in index_ranges:
        i = indices[0]
        j = indices[1]
        gold_subsets.append(gold_df.iloc[i:j+1])
    filtered_gold = pd.concat(gold_subsets)
    
    return filtered_gold, filtered_df_list

def get_flattened_y(gold_df, df_list):
    y_true_flat = gold_df.iloc[:, 1]
    y_true_flat = [label.upper() for label in y_true_flat]
    y_true_flat = [("O" if label == "" else label) for label in y_true_flat]
    
    y_pred_list_flat = []
    
    for df in df_list:
        y_pred_flat = df.iloc[:, 1]
        y_pred_flat = [label.upper() for label in y_pred_flat]
        y_pred_flat = [("O" if label == "" else label) for label in y_pred_flat]
    
        assert len(y_true_flat) == len(y_pred_flat), "y_t and y_pred do not have the same length"
        
        y_pred_list_flat.append(y_pred_flat)
        
    return y_true_flat, y_pred_list_flat

def metrics_df(y_true_flat: list, y_pred_flat: list, labels: list):
    precision_micro, recall_micro, f1_micro, _ = precision_recall_fscore_support(y_true_flat, y_pred_flat, average='micro', labels=labels, zero_division=0)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(y_true_flat, y_pred_flat, average='macro', labels=labels, zero_division=0)
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(y_true_flat, y_pred_flat, average='weighted', labels=labels, zero_division=0)

    accuracy = accuracy_score(y_true_flat, y_pred_flat)

    metrics_df = pd.DataFrame({
        "Metric": ["Precision", "Recall", "F1-Score"],
        "Micro": np.round([precision_micro, recall_micro, f1_micro], 6),
        "Macro": np.round([precision_macro, recall_macro, f1_macro], 6),
        "Weighted": np.round([precision_weighted, recall_weighted, f1_weighted],6),
        "Accuracy": [accuracy, None, None]
    })
    return metrics_df

def compare2gold(gold_df, df_list):
    
    y_true_flat, y_pred_list_flat = get_flattened_y(gold_df, df_list)
    
    for y_pred_flat in y_pred_list_flat:
        # check what kind of labels the evaluated model contains.
        
        all_labels = set(y_pred_flat)
        labels = list(all_labels)
        labels.remove("O")
        print(labels)
        
        if set(labels) == set(annotation_labels):
            y_random = [random.choice(["O"] + labels) for i in range(len(y_pred_flat))]
            assert len(y_random) == len(y_pred_flat)
        
            print(metrics_df(y_true_flat, y_pred_flat, labels))
            print("\nRandom:")
            print(metrics_df(y_true_flat, y_random, labels))
            print("\n")
            # classification_report(y_true_flat, y_pred_flat, labels=annotation_labels, zero_division=0)
        
        elif len(labels) == 1:
            # only I or O
            # convert y_gold
            y_t = [labels[0] if label != "O" else "O" for label in y_true_flat]
            
            y_random = [random.choice(["O"] + labels) for i in range(len(y_pred_flat))]
            assert len(y_random) == len(y_pred_flat)
            
            print(metrics_df(y_t, y_pred_flat, labels))
            print("\nRandom:")
            print(metrics_df(y_t, y_random, labels))
            print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to evaluate performance of NER. Arguments are all files which should be evaluated.")
    
    parser.add_argument(
        "--gold",
        type=str,
        required=True,
        help="File containing target annotations."
    )
    
    parser.add_argument(
        "files",
        nargs="+",
        help="List of files which should be evaluated (at least one required)"
    )
    
    args = parser.parse_args()
    gold, df_list = make_dataframes(args.gold, args.files, annotated_lines_icsd3)
    compare2gold(gold, df_list)