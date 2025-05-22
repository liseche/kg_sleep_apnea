import argparse
import pandas as pd

def make_dataframe(filepath):
    with open(filepath, "r") as f:
        lines = [line.strip().split("\t") for line in f]
        max_cols = max(len(line) for line in lines)
        standardized_lines = [line + [""] * (max_cols - len(line))for line in lines]
        df = pd.DataFrame(standardized_lines)
    return df

def compare_lines(filepath1, filepath2):
    
    df1 = make_dataframe(filepath1)
    df2 = make_dataframe(filepath2)
    
    print(df1)
    print(df2)
    
    if len(df1) == len(df2):
        print("The two files have the same LENGTH of entries!")
    else:
        print(f"Length of {filepath1}: {len(df1)}")
        print(f"Length of {filepath2}: {len(df2)}")
        
    col1_df1 = df1[0]
    col1_df2 = df2[0]

    # Identify missing entries
    missing_in_df1 = col1_df2[~col1_df2.isin(col1_df1)]
    missing_in_df2 = col1_df1[~col1_df1.isin(col1_df2)]
    
    print("Number of entries missing in ", filepath1, ":", len(missing_in_df1))
    print("Number of entries missing in ", filepath2, ":", len(missing_in_df2))
    
    # Print results
    if not missing_in_df1.empty:
        print("Entries in df2 missing from df1:")
        for index, value in missing_in_df1.items():
            print(f"Line {index}: {value}")

    if not missing_in_df2.empty:
        print("\nEntries in df1 missing from df2:")
        for index, value in missing_in_df2.items():
            print(f"Line {index}: {value}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='CompareEntries',
        description='Compares two files, and tells you what entries are missing in one of the files.'
    )
    
    parser.add_argument(
        '--file1',
        required=True,
        help = 'One of the two files you want to compare.')
    
    parser.add_argument(
        '--file2',
        required= True,
        help = 'The other one of the two files you want to compare.'
    )
    
    args = parser.parse_args()
    compare_lines(args.file1, args.file2)