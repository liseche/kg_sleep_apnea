"""Script to calculate performance of NER"""
import csv

def compare_tsv_columns(file1, file2):
    # Read the first column from the first file
    with open(file1, 'r') as f1:
        reader1 = csv.reader(f1, delimiter='\t')
        column1_file1 = {row[0] for row in reader1}

    # Read the first column from the second file
    with open(file2, 'r') as f2:
        reader2 = csv.reader(f2, delimiter='\t')
        column1_file2 = {row[0] for row in reader2}

    # Compare the two sets of entries
    if column1_file1 == column1_file2:
        print("The first columns of both files have the same entries.")
    else:
        print("The first columns of the files are different.")

        # Identify differences
        only_in_file1 = column1_file1 - column1_file2
        only_in_file2 = column1_file2 - column1_file1

        if only_in_file1:
            print("Entries only in file 1:")
            print(only_in_file1)

        if only_in_file2:
            print("Entries only in file 2:")
            print(only_in_file2)

# Example usage
file1 = 'NER+RE/PyTorch/knowledgator_gliner-multitask-large-v0.5_7.tsv'
file2 = 'NER+RE/spaCy/TraditionalNER_results/en_ner_bionlp13cg_md.tsv'
compare_tsv_columns(file1, file2)