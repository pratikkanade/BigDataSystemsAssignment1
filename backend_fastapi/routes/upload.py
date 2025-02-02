import os
from io import BytesIO
from typing import Dict
from fastapi import APIRouter, File, Query, UploadFile, HTTPException
from pydantic import BaseModel, HttpUrl
from data_ingestion_processing.services.parsers.pymupdf_parser_s3 import process_pdf_s3_upload
from data_ingestion_processing.services.parsers.adobe_parser_s3 import process_pdf_adobe_s3_upload
from data_ingestion_processing.services.parsers.bs_parser_s3 import parse_with_bs


router = APIRouter()

# Define size limit (3MB in bytes)
MAX_FILE_SIZE = 3 * 1024 * 1024

class URLInput(BaseModel):
    url: HttpUrl

bucket_name='bigdatasystems'

@router.post("/pdf")
async def upload_pdf(parser_type: str = Query(...), file: UploadFile = File(...)):

    
    pdf_name = file.filename

    if not pdf_name.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    try:
        # Read the uploaded file's content
        file_content = await file.read()

        #pdf_name = file.filename
        file_name = os.path.splitext(pdf_name)[0]

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File size exceeds the 3MB limit")
   
        # Choose parser based on parser_type
        if parser_type == "PyMuPDF (Open Source)":
            s3_path = process_pdf_s3_upload(file_name, BytesIO(file_content), bucket_name)

        elif parser_type == "Adobe PDF Services (Enterprise)":
            s3_path = process_pdf_adobe_s3_upload(file_name, BytesIO(file_content), bucket_name)

        else:
            raise HTTPException(status_code=400, detail="Invalid parser type.")

        # Store parsed content in S3
        #file_url = process_pdf_s3_upload(parsed_content, file.filename)
        return {"message": "File parsed and uploaded successfully", "file_url": s3_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        file.close()
    

@router.post("/webpage")
async def process_webpage(url_input: URLInput, parser_type: str = Query(...)) -> Dict:
    try:
        # Call the scraping function
        if parser_type == "Beautiful Soup (Open Source)":
            scraped_content = parse_with_bs(str(url_input.url), bucket_name)
        return {"url parsed": str(url_input.url), "parsed at" : scraped_content }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error scraping webpage: {str(e)}")
