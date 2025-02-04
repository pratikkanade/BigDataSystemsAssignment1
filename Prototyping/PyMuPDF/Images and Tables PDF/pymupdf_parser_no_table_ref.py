from pymupdf4llm import to_markdown
import fitz
import os
#import re
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
            
            # Create unique filename
            image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
            image_path = os.path.join(image_dir, image_filename)
            
            # Save image
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            # Store reference with page number and position
            if page_num not in image_map:
                image_map[page_num] = []
            image_map[page_num].append(image_filename)
    
    return image_map

def create_markdown_with_positioned_images(pdf_path):

    # Create a folder structure based on the PDF name
    pdf_name = Path(pdf_path).stem
    output_dir = Path(pdf_name) / "pymupdf no tables"
    output_dir.mkdir(exist_ok=True)

    # Create subdirectories for images and tables
    image_dir = output_dir / "images"
    markdown_path = output_dir / f"{pdf_name}.md"

    # Extract and save images
    image_map = extract_and_save_images(pdf_path, image_dir)
    
    # Convert PDF to markdown
    doc = fitz.open(pdf_path)
    markdown_content = ""

    for page_num in range(len(doc)):
        # Get page content
        page_text = to_markdown(pdf_path, pages=[page_num])
        
        # If page has images, insert their references
        if page_num in image_map:
            for img_filename in image_map[page_num]:
                # Insert image reference after the nearest paragraph
                image_ref = f"\n\n![Image](./{image_dir}/{img_filename})\n\n"
                # Split content into paragraphs and insert image
                paragraphs = page_text.split('\n\n')
                if len(paragraphs) > 1:
                    # Insert after first non-empty paragraph
                    for i, para in enumerate(paragraphs):
                        if para.strip():
                            paragraphs.insert(i + 1, image_ref)
                            break
                    page_text = '\n\n'.join(paragraphs)
                else:
                    page_text += image_ref
        
        markdown_content += page_text + "\n\n"
    
    # Save the markdown file
    Path(markdown_path).write_text(markdown_content, encoding="utf-8")

# Usage
pdf_path = "Images and Tables PDF.pdf"
create_markdown_with_positioned_images(pdf_path)
