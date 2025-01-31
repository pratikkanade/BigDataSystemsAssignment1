import pymupdf4llm
import fitz
import os
import pandas as pd
from pathlib import Path

def extract_and_save_images(pdf_path, image_dir):
    os.makedirs(image_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_map = {}
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
            image_path = os.path.join(image_dir, image_filename)
            
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            if page_num not in image_map:
                image_map[page_num] = []
            image_map[page_num].append(image_filename)
    
    return image_map

def extract_and_save_tables(pdf_path, table_dir):
    os.makedirs(table_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    table_map = {}
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        tables = page.find_tables()  # Find tables on the page
        
        for table_index, table in enumerate(tables):
            # Convert table to DataFrame
            df = pd.DataFrame(table.extract())
            
            # Save table as CSV
            table_filename = f"page{page_num + 1}_table{table_index + 1}.csv"
            table_path = os.path.join(table_dir, table_filename)
            df.to_csv(table_path, index=False)
            
            if page_num not in table_map:
                table_map[page_num] = []
            table_map[page_num].append(table_filename)
    
    return table_map


def create_markdown_with_images_and_tables(pdf_path):

    # Create a folder structure based on the PDF name
    pdf_name = Path(pdf_path).stem
    output_dir = Path(pdf_name) / "pymupdf"
    output_dir.mkdir(exist_ok=True)

    # Create subdirectories for images and tables
    image_dir = output_dir / "images"
    table_dir = output_dir / "tables"
    markdown_path = output_dir / f"{pdf_name}.md"

    # Extract and save images and tables
    image_map = extract_and_save_images(pdf_path, image_dir)
    table_map = extract_and_save_tables(pdf_path, table_dir)
    
    # Convert PDF to markdown
    doc = fitz.open(pdf_path)
    markdown_content = ""
    
    for page_num in range(len(doc)):
        # Get page content
        page_text = pymupdf4llm.to_markdown(pdf_path, pages=[page_num])
        #page_text = pymupdf4llm.to_markdown(pdf_path, pages=[page_num], exclude_tables=True)
        
        # Insert image references
        if page_num in image_map:
            for img_filename in image_map[page_num]:
                image_ref = f"\n\n![Image](./{image_dir}/{img_filename})\n\n"
                paragraphs = page_text.split('\n\n')
                if len(paragraphs) > 1:
                    for i, para in enumerate(paragraphs):
                        if para.strip():
                            paragraphs.insert(i + 1, image_ref)
                            break
                    page_text = '\n\n'.join(paragraphs)
                else:
                    page_text += image_ref
        
        # Insert table references
        if page_num in table_map:
            for table_filename in table_map[page_num]:
                # Create markdown table reference
                table_ref = f"\n\n[View Table: {table_filename}](./{table_dir}/{table_filename})\n\n"
                page_text += table_ref
        
        markdown_content += page_text + "\n\n"
    
    # Save the markdown file
    Path(markdown_path).write_text(markdown_content, encoding="utf-8")

# Usage
pdf_path = "Images and Tables PDF.pdf"
create_markdown_with_images_and_tables(pdf_path)
