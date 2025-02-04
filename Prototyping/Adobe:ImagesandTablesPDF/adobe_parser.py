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

from io import BytesIO
logging.basicConfig(level=logging.INFO)

# Define input and output directories
input_pdf = r"/Users/nikhilshejwal/Downloads/PDFServicesSDK-PythonSamples/adobe-dc-pdf-services-sdk-python/src/resources/ImagesandTables.pdf"
output_dir = "./extracted_content"
images_dir = os.path.join(output_dir, "images")
tables_dir = os.path.join(output_dir, "tables")

load_dotenv(r'/Users/nikhilshejwal/Downloads/PDFServicesSDK-PythonSamples/adobe-dc-pdf-services-sdk-python/src/extractpdf/setup.env')


    
    #load_dotenv()
    #load_dotenv(r'C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Assignment 1\environment\s3_adobe_access.env')

    #s3 = boto3.client('s3')
    #s3 = boto3.client(
        #'s3',
        #aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        #aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        #region_name=os.getenv('AWS_REGION')
    #)
    #s3.upload_fileobj(file_content, bucket_name, s3_path

# Create output directories if they don't exist
for directory in [output_dir, images_dir, tables_dir]:
    os.makedirs(directory, exist_ok=True)


image_counter = 0
table_counter = 0 
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

#def process_pdf_adobe_s3_upload(file_name, file_stream, bucket_name):
#def process_pdf_adobe_s3_upload(pdf_path, bucket_name):
    
    filename = Path(pdf_path).stem
    output_dir = f"{filename}/Adobe"
    images_dir = f"{output_dir}/images/"
    tables_dir = f"{output_dir}/tables/"
    markdown_path = f"{output_dir}/{filename}.md"

# Create output directories if they don't exist
    for directory in [output_dir, images_dir, tables_dir]:
        os.makedirs(directory, exist_ok=True)


try:
    # Read the input PDF
    with open(input_pdf, 'rb') as file:
        input_stream = file.read()

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
    
    extracted_images = []
    extracted_tables = []

    # Process the ZIP content directly in memory
    with ZipFile(io.BytesIO(zip_bytes)) as zip_file:
        # Extract and process JSON
        json_data = json.loads(zip_file.read('structuredData.json').decode('utf-8'))
        markdown_content = json_to_markdown(json_data, extracted_images, extracted_tables)
        
        # Save markdown content
        markdown_buffer = BytesIO(markdown_content.encode("utf-8"))
       
        #with open(os.path.join(output_dir, 'output.md'), 'w', encoding='utf-8') as md_file:
            #md_file.write(markdown_content

        # Extract images and tables
        for file_name in zip_file.namelist():
            if file_name.startswith('figures/'):
                # Save images
                with open(os.path.join(images_dir, os.path.basename(file_name)), 'wb') as f:
                    f.write(zip_file.read(file_name))
            elif file_name.startswith('tables/'):
                # Save tables
                with open(os.path.join(tables_dir, os.path.basename(file_name)), 'wb') as f:
                    f.write(zip_file.read(file_name))
         # Convert extracted content to Markdown
        markdown_content = json_to_markdown(json_data, extracted_images, extracted_tables)
        
        # Save markdown content
        with open(os.path.join(output_dir, 'output.md'), 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
    
    print(f"Extraction completed successfully!")
    print(f"Markdown file saved to: {os.path.join(output_dir, 'output.md')}")
    print(f"Images saved to: {images_dir}")
    print(f"Tables saved to: {tables_dir}")

except Exception as e:
    logging.error(f"Error during PDF extraction: {str(e)}")
