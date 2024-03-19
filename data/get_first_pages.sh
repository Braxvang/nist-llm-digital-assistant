#! /bin/bash

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
