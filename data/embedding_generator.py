"""
Author: Braxton VanGundy

Purpose:  This script will generate and save embeddings for the NIST SP800 series documents.
"""

from sentence_transformers import SentenceTransformer, util
import os
import re
import pickle
import re
import json
from typing import Final

# The path to the training data
TEXT_FILE_DIR: Final[str] = './data/full_text_data' 

# The path and name to save the embedding model
EMBEDDING_SAVE_FILE: Final[str] = './models/nist_sp800_embeddingsv1.pkl'

def clean_text_from_pdfs(input_text: str) -> str:
    """Cleans unwanted characters from the pdf files

    Args:
        input_text (str): The input text to be cleaned

    Returns:
        str: The cleaned input text
    """
    # strip out any characters besides alpha-numerics and some supported punctuation
    regex = re.compile('[^a-zA-Z0-9.?!-_\'] ')
    input_text: str = regex.sub('', input_text)

    # remove excessive whitespace, also removes newlines and tabs.
    input_text = " ".join(input_text.split())

    return input_text

def text_validator(input_text:str) -> bool:
    """
    Function to identify pages that are either full of junk or table of contents,
    these pages typically have many instances of repeated periods.

    Args:
        input_text (str): The input text to be cleaned

    Returns:
        bool: Indicates wether or not the text checked is valid (not junk). 
    """
    table_of_contents_regex = re.compile(r'\.{5}') # Pattern to remove pages that are just table of contents.
    if(len(re.findall(table_of_contents_regex, input_text)) > 0):
        return False # text is junk
    else:
        return True # text is okay

def generate_embeddings() -> list[str]:
    """
    Generates the embeddings for the NIST SP-800 dataset. 
    Having the embeddings already generated will make the overall response times
    of the final system slightly quicker. Embeddings are saved using pickle.
    """
    # specify how many characters need to be in a text file in order for it to be 
    # added to the corpus. 
    TEXT_FILE_MIN_LENGTH: Final[int] = 150

    # Download model
    # Using the all-MiniLM-L6-v2 model which is a good balance between model size and performance. 
    # Initially tried some of the larger models but could not load them on my system due to memory requirements.
    model = SentenceTransformer('all-MiniLM-L6-v2', trust_remote_code=True)

    # will hold the corpus that is used for training
    training_corpus: list[str] = []

    # will hold the JSON (string representation) version of the corpus that will be used by the LLM to extract information
    json_corpus: list[str] = []

    # tracks the number of items removed due to not having enough text of containing text flagged as invalid.
    items_filtered: int = 0

    # Add all of the data from our text files to the corpus. 
    for text_file in os.listdir(TEXT_FILE_DIR):
        with open(os.path.join(TEXT_FILE_DIR, text_file), 'r', encoding='utf-8', errors='ignore') as input_file:
            text: str = input_file.read()
            # Exclude entries from the corpus that are too short.
            if len(clean_text_from_pdfs(text)) > TEXT_FILE_MIN_LENGTH and text_validator(text):
                document_name: str = text_file.split('.pdf')[0]
                page_number: str = text_file.split('.pdf')[1]
                # compile the training corpus and JSON formatted corpus
                training_corpus.append(f"Document Name: {document_name} \nPage Number: {page_number}\n\n{clean_text_from_pdfs(text)}")
                json_corpus.append(json.dumps({'Document Name':document_name, 'Page Number':page_number.replace("::page_number::",""), 'text':clean_text_from_pdfs(text)}))
            else:
                items_filtered = items_filtered + 1

    print(f"{str(len(training_corpus))} pages ingested into corpus following filtering.\n")
    print(f"{str(items_filtered)} pages removed.")

    # encode text in the corpus to embeddings
    corpus_embeddings = model.encode(training_corpus)

    # Store sentences & embeddings on disc
    with open(EMBEDDING_SAVE_FILE, "wb") as fOut:
        pickle.dump({"sentences": json_corpus, "embeddings": corpus_embeddings}, fOut, protocol=pickle.HIGHEST_PROTOCOL)


generate_embeddings()