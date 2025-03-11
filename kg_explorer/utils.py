import pandas as pd

def make_dataframe(filepath : str) -> pd.DataFrame:
    """Makes a dataframe from a CoNLL-file (tsv-file with first column for tokens/words and second column for annotations.

    Args:
        filepath (str): path to file containing annotations on CoNLL-format.

    Returns:
        pd.DataFrame: file as pandas dataframe.
    """
    with open(filepath, "r") as f:
        lines = [line.rstrip().split("\t") for line in f]
        max_cols = max(len(line) for line in lines)
        standardized_lines = [line + [""] * (max_cols - len(line))for line in lines]
        df = pd.DataFrame(standardized_lines)
    return df

def get_sentences_from_path(file_path: str) -> list:
    """Get sentences from a input file pointed to by file_path. Interprets a blank line as the sentence separator.

    Args:
        file_path (str): path to input

    Returns:
        list(str): list of sentences.
    """
    sentences = []
    with open(file_path, 'r', encoding='utf-8') as file:
        sentence = []
        for line in file:
            if line.strip():
                sentence.append(line.strip())
            else:
                if sentence: 
                    sentences.append(sentence)
                sentence = []
        if sentence: 
            sentences.append(sentence)
    return sentences