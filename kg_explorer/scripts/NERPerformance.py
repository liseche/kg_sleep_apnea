"""Script to calculate performance of NER"""
import pandas as pd
import argparse
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support, ConfusionMatrixDisplay
import random
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("/Users/lisechen/thesis_code")
from kg_explorer.config import annotation_labels, annotated_lines_icsd3
from kg_explorer.utils import make_dataframe

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
            subsets.append(df.iloc[i-1:j+1])
        filtered_df_list.append(pd.concat(subsets))
    
    gold_subsets = []
    for indices in index_ranges:
        i = indices[0]
        j = indices[1]
        gold_subsets.append(gold_df.iloc[i-1:j+1])
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

def get_io_bio_disease_filtered_gold(gold_df):
    filtered_gold_io = []
    filtered_gold_bio = []
    
    # convert all other labels in gold other than disease to outside, and add B and I
    bio_labels = [label.upper() for label in gold_df.iloc[:,2]]
    entity_labels = [label for label in gold_df.iloc[:,1]]
    assert len(bio_labels)==len(entity_labels), "target and pred not same length"
    
    for i in range(len(entity_labels)):
        if str(entity_labels[i]) and("condition" in str(entity_labels[i]) or "CONDITION" in str(entity_labels[i])):
            bio_label = str(bio_labels[i]) + "-DISEASE"
            filtered_gold_bio.append(bio_label)
            filtered_gold_io.append("DISEASE")
        else:
            filtered_gold_io.append("O")
            filtered_gold_bio.append("O")
    return filtered_gold_io, filtered_gold_bio

def convert_0_to_o(y_pred_flat):
    y_pred1 = []
    for y_pred in y_pred_flat:
        if y_pred == "0":
            y_pred1.append("O")
        else:
            y_pred1.append(y_pred)
    assert len(y_pred1) == len(y_pred_flat), "len of converted predictions are not the same."
    return y_pred1

def remove_labels_other_than_disease(y_pred_flat):
    y_pred_flat_new = []
    for y_pred in y_pred_flat:
        if "DISEASE" not in y_pred:
            y_pred_flat_new.append("O")
        else:
            y_pred_flat_new.append(y_pred)
    assert len(y_pred_flat_new) == len(y_pred_flat), "len not the same"
    return y_pred_flat_new

def compare2gold(gold_df, df_list, files_list):
    fig_counter = 1
    
    y_true_flat, y_pred_list_flat = get_flattened_y(gold_df, df_list)
    filtered_gold_io, filtered_gold_bio = get_io_bio_disease_filtered_gold(gold_df)
    
    for df_index in range(len(df_list)):
        y_pred_flat = y_pred_list_flat[df_index]
        print(files_list[df_index])
        # check what kind of labels the evaluated model contains.
        all_labels = list(set(y_pred_flat))
        labels = list(all_labels)
        labels.remove("O")
        if "0" in all_labels:
            all_labels.remove("0")
            labels.remove("0")
        print(labels)
        print(all_labels)
        y_all_o = ["O" for i in range(len(y_pred_flat))]
        
        if set(labels) == set(annotation_labels):
            y_random = [random.choice(["O"] + labels) for i in range(len(y_pred_flat))]
            assert len(y_random) == len(y_pred_flat)
        
            print(metrics_df(y_true_flat, y_pred_flat, labels))
            cm = confusion_matrix(y_true_flat, y_pred_flat, labels=all_labels)
            ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=all_labels).plot()
            filename = "cm" + str(fig_counter)
            fig_counter = fig_counter + 1
            plt.savefig(filename)
            print("\nRandom:")
            print(metrics_df(y_true_flat, y_random, labels))
            print("\n")
            print("All 'O':")
            print(metrics_df(y_true_flat, y_all_o, labels))
            print("\n")
        
        elif set(labels) == set(["LABEL_0", "LABEL_1"]):
            y_temp = ["LABEL_0" if (label == "O" or label =="LABEL_0") else "LABEL_1" for label in y_true_flat]
            y_t1 = []
            y_p1 = []
            
            assert len(y_temp) == len(y_pred_flat), "Length of target and pred is not the same"
            # remove all blank lines (marked with "O")
            for i in range(len(y_pred_flat)):
                if y_pred_flat[i] != "O":
                    y_t1.append(y_temp[i])
                    y_p1.append(y_pred_flat[i])
            
            y_random = [random.choice(labels) for i in range(len(y_p1))]
            y_all_o_l1_l0 = ["LABEL_0" for o in y_all_o[:len(y_t1)]]
            assert len(y_random) == len(y_p1)
            labels_wo_o = labels.copy()
            labels_wo_o.remove("LABEL_0")
            
            print(metrics_df(y_t1, y_p1, labels_wo_o))
            cm = confusion_matrix(y_true=y_t1, y_pred=y_p1, labels=labels)
            ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels).plot()
            filename = "cm" + str(fig_counter)
            fig_counter = fig_counter + 1
            plt.savefig(filename)
            print("\nRandom:")
            print(metrics_df(y_t1, y_random, labels_wo_o))
            print("\n")
            print("All 'O':")
            print(metrics_df(y_t1, y_all_o_l1_l0, labels_wo_o))
            print("\n")
            
        elif len(labels) == 1:
            # only I or O
            # convert y_gold
            y_t = [labels[0] if label != "O" else "O" for label in y_true_flat]
            
            y_random = [random.choice(["O"] + labels) for i in range(len(y_pred_flat))]
            assert len(y_random) == len(y_pred_flat)
            
            print(metrics_df(y_t, y_pred_flat, labels))
            cm = confusion_matrix(y_true=y_t, y_pred=y_pred_flat, labels=all_labels)
            ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=all_labels).plot()
            filename = "cm" + str(fig_counter)
            fig_counter = fig_counter + 1
            plt.savefig(filename)
            print("\nRandom:")
            print(metrics_df(y_t, y_random, labels))
            print("\n")
            print("All 'O':")
            print(metrics_df(y_t, y_all_o, labels))
            print("\n")
        
        elif set(labels) == set(['B-DISEASE', 'I-DISEASE']):
            y_pred1 = convert_0_to_o(y_pred_flat)
            y_pred1 = remove_labels_other_than_disease(y_pred1)
            y_random = [random.choice(["O"] + labels) for i in range(len(y_pred1))]
            print(metrics_df(filtered_gold_bio, y_pred1, labels))
            cm = confusion_matrix(y_true=filtered_gold_bio, y_pred=y_pred1, labels=all_labels)
            ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=all_labels).plot()
            filename = "cm" + str(fig_counter)
            fig_counter = fig_counter + 1
            plt.savefig(filename)
            print("\nRandom:")
            print(metrics_df(filtered_gold_bio, y_random, labels))
            print("\n")
            print("All 'O':")
            print(metrics_df(filtered_gold_bio, y_all_o, labels))
            print("\n")
            
        else:
            for label in labels:
                if "DISEASE" in label:
                    if 'CHEMICAL' in all_labels:
                        all_labels.remove('CHEMICAL')
                    print("Converted to", str(all_labels))
                    y_pred2 = convert_0_to_o(y_pred_flat)
                    y_pred2 = remove_labels_other_than_disease(y_pred2)
                    y_random = [random.choice(all_labels) for i in range(len(y_pred2))]
                    print(metrics_df(filtered_gold_io, y_pred2, [la for la in all_labels if la != "O"]))
                    cm = confusion_matrix(y_true=filtered_gold_io, y_pred=y_pred2, labels=all_labels)
                    ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=all_labels).plot()
                    filename = "cm" + str(fig_counter)
                    fig_counter = fig_counter + 1
                    plt.savefig(filename)
                    print("\nRandom:")
                    print(metrics_df(filtered_gold_io, y_random, [la for la in all_labels if la != "O"]))
                    print("\n")
                    print("All 'O':")
                    print(metrics_df(filtered_gold_io, y_all_o, [la for la in all_labels if la != "O"]))
                    print("\n")
                    break
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
    print("Printing evaluation of files: ", args.files)
    gold, df_list = make_dataframes(args.gold, args.files, annotated_lines_icsd3)
    compare2gold(gold, df_list, args.files)