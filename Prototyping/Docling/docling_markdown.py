import os
from docling.document_converter import DocumentConverter

def convert_and_save_document(file_path, output_folder):
    # Initialize converter
    converter = DocumentConverter()
    
    # Convert document
    result = converter.convert(file_path)
    
    # Generate filename based on original file
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"{base_name}.md"
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Create full path
    output_path = os.path.join(output_folder, output_file)
    
    # Save markdown content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.document.export_to_markdown())
    
    return output_path

# Example usage
file_path = r"C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Assignment 1\Images and Tables PDF.pdf"
output_folder = "docling_output_md"
output_path = convert_and_save_document(file_path, output_folder)
print("Markdown file saved")
