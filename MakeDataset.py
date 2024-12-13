"""
Script to make a dataset for NER processing from free text.
"""

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make a dataset for NER processing from free text.")
    
    parser.add_argument(
        '--input_file',
        type=str,
        required=True,
        help=""
    )

    parser.add_argument(
        '--output_file',
        type=str,
        default="dataset",
        help=""
    )

    parser.add_argument(
        '--split_strategy',
        type=str,
        choices=['sentence', 'paragraph', 'custom'],
        default='sentence',
        help=""
    )
    
    parser.add_argument(
        '--max_length',
        type=int,
        default=None,
        help="Maximum character length for each entry."
    )

    parser.add_argument(
        '--max_nr_entries',
        type=int,
        default=None,
        help="Maximum "
    )

    parser.add_argument(
        '--tokenize',
        action='store_true',
        help=""
    )

    args = parser.parse_args()

    if args.verbose:
        print("Parsed arguments:", args)
    print(f"Creating dataset with max entry length: {args.max_entry_length}")
    print(f"Maximum number of entries: {args.max_nr_entries if args.max_nr_entries else 'No limit'}")
    print(f"Input file: {args.input_file if args.input_file else 'Standard input'}")
    print(f"Output file: {args.output_file}")
    print(f"Split strategy: {args.split_strategy}")
    print(f"Tokenization enabled: {args.tokenize}")