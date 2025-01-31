import logging
import os
import json
import io
from pathlib import Path
from zipfile import ZipFile
from adobe.pdfservices.operation.auth.credentials import Credentials
#from adobe.pdfservices.operation.pdfjobs.options import PDFServicesMediaType
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
#from adobe.pdfservices.operation.pdfjobs.jobs import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_renditions_element_type import ExtractRenditionsElementType
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult
#from adobe.pdfservices.operation.pdfjobs.services import PDFServices
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from dotenv import load_dotenv
import boto3
from io import BytesIO

def json_to_markdown(json_data, images, tables):
    markdown_content = "# Extracted Content\n\n"
    
    for element in json_data.get("elements", []):
        if element.get("Path", "").startswith("//Document"):
            text = element.get("Text", "").strip()
            markdown_content += text + "\n\n"    
               
        if element.get("Path", "").endswith("/Figure"):
                
                image_filename = f"image_{image_counter + 1}.png"
                
                image_ref = f"\n\n![Image](./images/{image_filename})\n\n"
                markdown_content += image_ref + "\n\n"
        
        if element.get("Path", "").endswith("/Table"):
                
                table_filename = f"table_{table_counter + 1}.xlsx"
                
                table_ref = f"\n\n[View Table: {table_filename}](./tables/{table_filename})\n\n"
                markdown_content += table_ref + "\n\n"
     
    return markdown_content


load_dotenv(r'C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Assignment 1\environment\s3_adobe_access.env')

def upload_file_to_s3(file_content, bucket_name, s3_path):

    #load_dotenv()
    #load_dotenv(r'C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Assignment 1\environment\s3_adobe_access.env')

    #s3 = boto3.client('s3')
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    s3.upload_fileobj(file_content, bucket_name, s3_path)



def json_to_markdown(json_data):
    markdown_content = ""

    for element in json_data.get("elements", []):
        if element.get("Path", "").startswith("//Document"):
            text = element.get("Text", "").strip()
            if text:
                markdown_content += text + "\n\n"            

    return markdown_content


def process_pdf_adobe_s3_upload(file_name, file_stream, bucket_name):
#def process_pdf_adobe_s3_upload(pdf_path, bucket_name):

    # Define input and output directories
    #output_dir = "./extracted_content"
    #images_dir = os.path.join(output_dir, "images")
    #tables_dir = os.path.join(output_dir, "tables")


    #filename = Path(pdf_path).stem
    output_dir = f"{file_name}/Adobe"
    images_dir = f"{output_dir}/images/"
    tables_dir = f"{output_dir}/tables/"
    markdown_path = f"{output_dir}/{file_name}.md"


    # Create output directories if they don't exist
    for directory in [output_dir, images_dir, tables_dir]:
        os.makedirs(directory, exist_ok=True)


    try:
        # Read the input PDF
        #with open(file_stream, 'rb') as newfile:
        #    input_stream = newfile.read()

        input_stream = file_stream.read()

        # Initialize credentials
        credentials = ServicePrincipalCredentials(
                    client_id=os.getenv('CLIENT_ID'),
                    client_secret=os.getenv('CLIENT_SECRET')
                )

        # Create PDF Services instance
        pdf_services = PDFServices(credentials=credentials)

        # Upload the PDF
        input_asset = pdf_services.upload(
            input_stream=input_stream, 
            mime_type=PDFServicesMediaType.PDF
        )

        # Configure extraction parameters
        extract_pdf_params = ExtractPDFParams(
                elements_to_extract=[ExtractElementType.TEXT, ExtractElementType.TABLES],
                elements_to_extract_renditions=[ExtractRenditionsElementType.TABLES, ExtractRenditionsElementType.FIGURES],
            )

        # Create and execute the extraction job
        extract_job = ExtractPDFJob(
            input_asset=input_asset,
            extract_pdf_params=extract_pdf_params
        )

        # Submit job and get results
        location = pdf_services.submit(extract_job)
        result = pdf_services.get_job_result(location, ExtractPDFResult)

        # Get the extracted content as bytes
        result_asset = result.get_result().get_resource()
        stream_asset = pdf_services.get_content(result_asset)
        zip_bytes = stream_asset.get_input_stream()

        # Process the ZIP content directly in memory
        with ZipFile(io.BytesIO(zip_bytes)) as zip_file:

            # Extract and process JSON
            json_data = json.loads(zip_file.read('structuredData.json').decode('utf-8'))
            markdown_content = json_to_markdown(json_data)

            # Save markdown content
            markdown_buffer = BytesIO(markdown_content.encode("utf-8"))
            upload_file_to_s3(markdown_buffer, bucket_name, markdown_path)

            #with open(os.path.join(output_dir, 'output.md'), 'w', encoding='utf-8') as md_file:
            #    md_file.write(markdown_content)

            image_counter = 0
            table_counter = 0 

            # Extract images and tables
            for file in zip_file.namelist():

                if file.startswith('figures/'):
                    # Save images
                    image_filename = f"image_{image_counter + 1}.png"
                    s3_image_path = f"{images_dir}{image_filename}"
                    upload_file_to_s3(BytesIO(zip_file.read(file)), bucket_name, s3_image_path)
                    image_counter += 1

                    #with open(os.path.join(images_dir, os.path.basename(file_name)), 'wb') as f:
                    #    f.write(zip_file.read(file_name))

                elif file.startswith('tables/') and file.endswith('.xlsx'):
                    # Save tables
                    table_filename = f"table_{table_counter + 1}.xlsx"
                    s3_table_path = f"{tables_dir}{table_filename}"
                    upload_file_to_s3(BytesIO(zip_file.read(file)), bucket_name, s3_table_path)
                    table_counter += 1

                    #with open(os.path.join(tables_dir, os.path.basename(file_name)), 'wb') as f:
                    #    f.write(zip_file.read(file_name))

        print(f"Extraction completed and uploaded to S3 successfully!")
        #print(f"Markdown file saved to: {os.path.join(output_dir, 'output.md')}")
        #print(f"Images saved to: {images_dir}")
        #print(f"Tables saved to: {tables_dir}")
        return markdown_path

    except Exception as e:
        logging.error(f"Error during PDF extraction: {str(e)}")

    #finally:
    #    file_stream.close()


#bucket_name = 'bigdatasystems'
#pdf_path = r"C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Assignment 1\Images and Tables PDF.pdf"

#process_pdf_adobe_s3_upload(pdf_path, bucket_name)
