from fastapi import APIRouter, HTTPException
from data_ingestion_processing.services.retrievers.content_retrieval_main import render_markdown_from_s3

router = APIRouter()

@router.get("/filename")
def fetch_parsed_file(filename: str, parser_type: str):

    bucket_name = 'bigdatasystems'

    try:
        # Choose parser based on parser_type
        if parser_type == "Open Source":
            file_path = f'{filename}/PyMuPDF/{filename}.md'
        #elif parser_type == "enterprise":
        #    parsed_content = parse_with_enterprise(file)
        #elif parser_type == "selenium":
        #    parsed_content = parse_with_selenium(file)
        else:
            raise HTTPException(status_code=400, detail="Invalid parser type.")
        
        file_content = render_markdown_from_s3(bucket_name, file_path)
        #return {"filename": filename}
    
        return f'{filename} retrieved. Total size in bytes: {len(file_content)}'
    

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found in S3.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching file: {str(e)}")
