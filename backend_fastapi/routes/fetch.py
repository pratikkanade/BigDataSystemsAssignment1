from fastapi import APIRouter, HTTPException, Query
from data_ingestion_processing.services.retrievers.content_retrieval_main import render_markdown_from_s3

router = APIRouter()

@router.get("/file")
def fetch_parsed_file(filename: str = Query(...), parser_type: str = Query(...)):

    bucket_name = 'bigdatasystems'

    try:
        # Choose parser based on parser_type                     
        if parser_type == "Beautiful Soup (Open Source)":
            if '/' in filename:
                filename = filename.replace('/', '_')
                file_path = f'{filename}/BeautifulSoup/{filename}.md'
        
        elif parser_type == "Apify (Enterprise)":
            if '/' in filename:
                filename = filename.replace('/', '_')
                file_path = f'{filename}/BeautifulSoup/{filename}.md'

        elif parser_type == "PyMuPDF (Open Source)":
                file_path = f'{filename}/PyMuPDF/{filename}.md'

        elif parser_type == "Adobe PDF Services (Enterprise)":
            file_path = f'{filename}/Adobe/{filename}.md'

        else:
            raise HTTPException(status_code=400, detail="Invalid parser type.")
        
        file_content = render_markdown_from_s3(bucket_name, file_path)
    
        return f'{filename} contents : {file_content}'
    

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found in S3.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching file: {str(e)}")
