#! /bin/bash

# Author: Braxton VanGundy
# Now we need a seperate directory with only the first page of each document.  
#This will be used later to determine if the document has been deprecated or withdrawn and 
#should not be included in our model.  We only look at the first page because withdrawn 
#/ deprecated status always appears on the first page of the SP-800 series documents.

PDF_DIR="./full_pdf_dataset"
OUTPUT_DATA_DIR="./first_pages/"

for pdf_file in $PDF_DIR/*; do
    pages=$(pdfinfo $pdf_file | awk '/^Pages:/ {print $2}')
    {
        let p=0
        pdf_base_name=$(basename ${pdf_file})
        echo "outputing to: $OUTPUT_DATA_DIR$pdf_base_name.txt"
        pdftotext $pdf_file $OUTPUT_DATA_DIR$pdf_base_name.txt -f $p -l $p -layout

    }
done
