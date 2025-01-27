import os
import json
from PyPDF2 import PdfReader
from datetime import datetime

def pdf_parser_pypdf2(pdf_path, output_base_folder="parsed_content_PyPDF2"):

    # Get PDF name without extension for folder naming
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Create PDF-specific folders
    pdf_folder = os.path.join(output_base_folder, pdf_name)
    text_folder = os.path.join(pdf_folder, "text")
    image_folder = os.path.join(pdf_folder, "images")
    
    # Create all required directories
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(text_folder, exist_ok=True)
    os.makedirs(image_folder, exist_ok=True)
    
    # Initialize PDF reader and index
    reader = PdfReader(pdf_path)
    content_index = {
        "pdf_name": pdf_name,
        "parse_date": datetime.now().isoformat(),
        "pages": []
    }
    
    # Process each page
    for page_num, page in enumerate(reader.pages):

        # Save text content
        text_content = page.extract_text()
        text_filename = f'page_{page_num}.txt'
        text_path = os.path.join(text_folder, text_filename)
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Save images
        page_images = []
        for img_num, image in enumerate(page.images):
            image_filename = f'page_{page_num}_img_{img_num}.png'
            image_path = os.path.join(image_folder, image_filename)
            
            with open(image_path, 'wb') as f:
                f.write(image.data)
            
            page_images.append({
                "image_filename": image_filename,
                "position": img_num
            })
        
        # Add to index
        content_index["pages"].append({
            "page_number": page_num,
            "text_filename": text_filename,
            "images": page_images
        })
    
    # Save index file in PDF's folder
    index_path = os.path.join(pdf_folder, "content_index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(content_index, f, indent=4)
    
    return content_index


# Parse PDF and get content index
pdf_path = r"C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Assignment 1\Images and Tables PDF.pdf"
content_index = pdf_parser_pypdf2(pdf_path)

# Print summary
print(f"Processed PDF: {content_index['pdf_name']}")
print(f"Total pages: {len(content_index['pages'])}")