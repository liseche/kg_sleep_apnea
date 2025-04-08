"""
Script to get the annotated lines, and make a new document for this. 
"""
import argparse

import numpy as np
from kg_explorer.config import annotated_lines_icsd3
from kg_explorer.utils import make_dataframe
import pandas as pd

def filtered_dataframe(file, index_ranges):
    df = make_dataframe(file)

    subsets = []
    for indices in index_ranges:
        i = indices[0]
        j = indices[1]
        subsets.append(df.iloc[i-1:j+1])
    filtered_df = pd.concat(subsets)

    return filtered_df

def print_df(df : pd.DataFrame, output_name : str):
    """Print a pandas dataframe out as tab separated file.

    Args:
        output_name (_type_): name of generated output file
    """
    df.to_csv(output_name, sep="\t", index=False, header=False)
    
def print_to_CoNLL(df : pd.DataFrame, output_name : str):
    # Combine second and third columns with a hyphen, after converting to uppercase
    combined_col = np.where(
        df.iloc[:, 2] == "",
        "",
        df.iloc[:, 2].astype(str).str.upper() + "-" + df.iloc[:, 1].astype(str).str.upper()
    )
    combined_col = pd.DataFrame(combined_col)
    
    # Replace the second column with the combined one
    print(df.iloc[:,0].shape)
    print(combined_col.iloc[:,0].shape)
    df_out = pd.concat([df.iloc[:,0].reset_index(drop=True), combined_col.iloc[:,0].reset_index(drop=True)], axis=1)
    print(df_out.shape)

    # Save to CoNLL format (tab-separated, no header or index)
    df_out.to_csv(output_name, sep="\t", index=False, header=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to filter out annotated lines from a documents where small parts have been annotated")
    
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="File containing smaller annotated parts."
    )
    
    parser.add_argument(
        "--output_name",
        type=str,
        default="output.tsv",
        help="Name of output file, where only annotated lines are printed to."
    )
    
    parser.add_argument(
        "--conll",
        type=bool,
        default=False,
        help="Print output to CoNLL format"
    )
    
    args = parser.parse_args()
    
    filtered_df = filtered_dataframe(args.file, annotated_lines_icsd3)
    if args.conll:
        print_to_CoNLL(filtered_df, args.output_name)
    else:
        print_df(filtered_df, args.output_name)