import spacy
import argparse
import chardet
import re
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make a dataset for (NER) processing from free text. Divides the text using the split strategy and generates a file where each dataset entry (sentence/paragraph) is on one line.")
    
    parser.add_argument(
        '--input_file',
        type=str,
        required=True,
        help="Path to input file containing free form text you want to transform to a dataset."
    )

    parser.add_argument(
        '--output_file',
        type=str,
        default="dataset",
        help="Name of generated output file containing the dataset."
    )

    parser.add_argument(
        '--split_strategy',
        type=str,
        choices=['sentence', 'paragraph'],
        default='sentence',
        help="Type of method used to split the free form text for the dataset creation."
    )

    # This one is not implemented. Note to self: tried, but code in thesis_trash.
    # parser.add_argument(
    #     '--max_entry_length',
    #     type=int,
    #     default=100,
    #     help="Maximum character length for each entry in the dataset."
    # )

    parser.add_argument(
        '--max_nr_entries',
        type=int,
        default=None,
        help="Upper limit for number of entries in the dataset."
    )

    args = parser.parse_args()

    # print(f"Creating dataset with max entry length: {args.max_entry_length}")
    print(f"Maximum number of entries: {args.max_nr_entries if args.max_nr_entries else 'No limit'}")
    print(f"Input file: {args.input_file}")
    print(f"Output file: {args.output_file}")
    print(f"Split strategy: {args.split_strategy}")
    
    # Detect the encoding of the file
    with open(args.input_file, 'rb') as file:
        raw_data = file.read()
        encoding = chardet.detect(raw_data)
        print("Input file encoding: ", encoding['encoding'])
    
    with open(args.input_file, mode="r", encoding=encoding['encoding']) as input_file:
        text = input_file.read()
        
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    # check for page numbers. Removes some, but not all. Also remove new lines and blank lines in a sentence (unnecessary for dataset)
    pattern = re.compile(r'\n\s*\d*\s*\n*')
    sentences = []
    counter = 0
    for sent in doc.sents:
        if args.max_nr_entries and (counter >= args.max_nr_entries):
            break
        if sent.text:
            if pattern.search(sent.text):
                sentences.append(re.sub(pattern, ' ', sent.text))
            else:
                sentences.append(sent.text)
            counter+=1
    
    with open(args.output_file, "w+") as output_file:
        for sent in sentences:
            output_file.write(sent + "\n")