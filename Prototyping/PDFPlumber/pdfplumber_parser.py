import pdfplumber
import os
import json
from datetime import datetime

def pdf_parser_pdfplumber(pdf_path, output_base_folder="parsed_content_pdfplumber"):

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Create PDF-specific folders
    pdf_folder = os.path.join(output_base_folder, pdf_name)
    text_folder = os.path.join(pdf_folder, "text")
    image_folder = os.path.join(pdf_folder, "images")
    table_folder = os.path.join(pdf_folder, "tables")
    
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(text_folder, exist_ok=True)
    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(table_folder, exist_ok=True)
    
    content_index = {
        "pdf_name": pdf_name,
        "parse_date": datetime.now().isoformat(),
        "pages": [],
        "tables_summary": [],
        "images_summary": []
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        table_counter = 0
        image_counter = 0
        
        for page_num, page in enumerate(pdf.pages):

            # Extract and save text
            text_content = page.extract_text()
            text_filename = f'page_{page_num}.txt'
            text_path = os.path.join(text_folder, text_filename)
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            # Extract and save tables
            tables = page.extract_tables()
            page_tables = []
            
            for table_num, table in enumerate(tables):
                table_counter += 1
                table_filename = f'page_{page_num}_table_{table_num}.json'
                table_path = os.path.join(table_folder, table_filename)
                
                table_info = {
                    "table_id": table_counter,
                    "table_filename": table_filename,
                    "page_number": page_num,
                    "rows": len(table),
                    "columns": len(table[0]) if table else 0,
                    "preview": table[:3] if table else [],
                    "location": {
                        "page": page_num,
                        "relative_position": table_num
                    }
                }
                
                with open(table_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "table_info": table_info,
                        "table_data": table
                    }, f, indent=4)
                
                page_tables.append(table_info)
                content_index["tables_summary"].append(table_info)
            
            # Process images
            page_images = []
            for img_num, image in enumerate(page.images):
                image_counter += 1
                image_filename = f'page_{page_num}_img_{img_num}.png'
                image_path = os.path.join(image_folder, image_filename)
                
                with open(image_path, 'wb') as f:
                    f.write(image['stream'].get_data())
                
                image_info = {
                    "image_id": image_counter,
                    "image_filename": image_filename,
                    "page_number": page_num,
                    "width": image.get('width', 0),
                    "height": image.get('height', 0),
                    "location": {
                        "page": page_num,
                        "relative_position": img_num
                    }
                }
                
                page_images.append(image_info)
                content_index["images_summary"].append(image_info)
            
            # Add page information
            content_index["pages"].append({
                "page_number": page_num,
                "text_filename": text_filename,
                "tables": page_tables,
                "images": page_images,
                "table_count": len(page_tables),
                "image_count": len(page_images)
            })
    
    # Save index file
    index_path = os.path.join(pdf_folder, "content_index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(content_index, f, indent=4)
    
    return content_index


# Process a single PDF
pdf_path = r"C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Assignment 1\Images and Tables PDF.pdf"
result = pdf_parser_pdfplumber(pdf_path)

print(f"Processed PDF: {result['pdf_name']}")
print(f"Total pages processed: {len(result['pages'])}")