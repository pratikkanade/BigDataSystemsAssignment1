import logging
import fitz
import pandas as pd
import boto3
from io import BytesIO
import os
from dotenv import load_dotenv

def upload_file_to_s3(file_content, bucket_name, s3_path):

    #load_dotenv()
    load_dotenv(r's3_adobe_access.env')

    #s3 = boto3.client('s3')
    s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
    )
    s3.upload_fileobj(file_content, bucket_name, s3_path)

def process_pdf_s3_upload(file_name, file_stream, bucket_name):
    
    # Convert bytes into a file-like object
    #doc = BytesIO(file_content)

    #pdf_name = Path(pdf_path).stem
    #file_name = 'Text PDF'
    parser_prefix = f"{file_name}/PyMuPDF"
    image_prefix = f"{parser_prefix}/images/"
    table_prefix = f"{parser_prefix}/tables/"
    markdown_path = f"{parser_prefix}/{file_name}.md"

    try:
        doc = fitz.open(stream=file_stream, filetype="pdf")
        markdown_content = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text("text")

            # Process images
            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                xref = img[0]  # Get reference number
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                s3_image_path = f"{image_prefix}{image_filename}"

                # Direct upload to S3
                upload_file_to_s3(BytesIO(image_bytes), bucket_name, s3_image_path)
                image_ref = f"\n\n![Image](./images/{image_filename})\n\n"
                page_text += image_ref

            # Process tables
            tables = page.find_tables()
            for table_index, table in enumerate(tables):
                df = pd.DataFrame(table.extract())
                table_filename = f"page{page_num + 1}_table{table_index + 1}.csv"
                s3_table_path = f"{table_prefix}{table_filename}"

                # Direct upload to S3
                csv_buffer = BytesIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                upload_file_to_s3(csv_buffer, bucket_name, s3_table_path)
                table_ref = f"\n\n[View Table: {table_filename}](./tables/{table_filename})\n\n"
                page_text += table_ref

            markdown_content += page_text + "\n\n"

        # Upload markdown directly to S3
        markdown_buffer = BytesIO(markdown_content.encode("utf-8"))
        upload_file_to_s3(markdown_buffer, bucket_name, markdown_path)
        return markdown_path

    except Exception as e:
        logging.error(f"Error during PDF extraction: {str(e)}")

# Usage
#pdf_path = r"C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Assignment 1\Images and Tables PDF.pdf"
#bucket_name = "bigdatasystems"

#process_pdf_s3_upload(pdf_path, bucket_name)