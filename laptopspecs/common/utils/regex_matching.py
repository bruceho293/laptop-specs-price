import re

def text_to_seq_pattern(text):
    # Get rif of the space character
    non_space_texts = text.split(' ')
    
    # Append \b and \b to each word for matching seq
    append_regex = [r'\b{}\b'.format(word) for word in non_space_texts]

    # Create the final matching sequence pattern
    seq_pattern = r'.*'.join(append_regex)
    seq_pattern = r'.*{}.*'.format(seq_pattern)

    return seq_pattern