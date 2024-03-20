#! /bin/bash

# Author: Braxton VanGundy
# This script converts every page of the PDFs found in the PDF dataset to a text file.

PDF_DIR="./full_pdf_dataset"
OUTPUT_DATA_DIR="./full_text_data/"

for pdf_file in $PDF_DIR/*; do
    pages=$(pdfinfo $pdf_file | awk '/^Pages:/ {print $2}')
    {
        let p=1
        while [ $p -lt $pages ]; do
            pdf_base_name=$(basename ${pdf_file})
            echo "outputing to: $OUTPUT_DATA_DIR$pdf_base_name"::page_number::"$p"
            pdftotext $pdf_file $OUTPUT_DATA_DIR$pdf_base_name"::page_number::"$p -f $p -l $p -layout
            let p++
        done
    }
done
