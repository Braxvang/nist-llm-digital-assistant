"""
Author: Braxton VanGundy

This script looks at the first page of each PDF that was parsed out using a bash script and 
looks for the phrases "Withdrawn NIST Technical Series Publication","Withdrawn Draft", and
"Archived NIST Technical Series Publication".  These phrases indicate that the document 
has been supersceded by another document and should be ignored.
"""

import os
from typing_extensions import Final

# Path to the folder with all of the text files from each PDF's first page
TEXT_FILES: Final[str] = "./first_pages"
# Path to the parent (to the text files) PDF files. 
FULL_PDF_FILES: Final[str] = "./full_pdf_dataset"
# Phrases that indicate a document has been removed from the core dataset and should be ignored. 
LIST_OF_KEY_PHRASES: Final[list[str]] = ["Withdrawn NIST Technical Series Publication",
                                         "Withdrawn Draft",
                                         "Archived NIST Technical Series Publication"]

files_removed: int = 0

# Loop through each of the text files and check for the phrases in LIST_OF_KEY_PHRASES
# If a key phrases is found, then that file's parent PDF file needs to be removed. 
for first_page_file in os.listdir(TEXT_FILES):
    with open(os.path.join(TEXT_FILES, first_page_file)) as text_file:
        text_contents: str = text_file.read()
        for phrase in LIST_OF_KEY_PHRASES:
            # if the phrase is found in one of the files, delete the parent PDF file. 
            if phrase in text_contents:
                os.remove(os.path.join(FULL_PDF_FILES,first_page_file.replace(".txt", "")))
                print(f"File deleted: {first_page_file.replace('.txt', '')}")
                files_removed = files_removed + 1
                break

print(f"Total files removed: {files_removed}")

