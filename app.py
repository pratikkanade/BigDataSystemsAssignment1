#import streamlit as st
#st.set_page_config(page_title="Streamlit App", layout="wide", initial_sidebar_state="expanded")
#df = st.file_uploader(label = "Upload your pdf", type = ['pdf'])


#if df is not None:
    #st.write("File uploaded successfully")
    #st.write(df)
    #st.write(df.read())
#else:
    #st.write("Upload a file")

import streamlit as st
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import requests

st.title("PDF and Web Page Data Extractor")

# Sidebar for input source selection
input_source = st.sidebar.radio("Select Input Source", ["PDF Upload", "Web Page URL"])

# Sidebar for extraction method selection
extraction_method = st.sidebar.selectbox(
    "Select Extraction Method",
    ["Adobe PDF Services (Enterprise)", "PyMuPDF (Open Source)", 
     "BeautifulSoup (Web Scraping)", "Enterprise Web Extraction Tool"]
)

if input_source == "PDF Upload":
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        st.success("PDF uploaded successfully!")
        
        if extraction_method == "Adobe PDF Services (Enterprise)":
            st.info("Using Adobe PDF Services for extraction...")
            # Implement Adobe PDF Services extraction here
        
        elif extraction_method == "PyMuPDF (Open Source)":
            st.info("Using PyMuPDF for extraction...")
            try:
                with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    st.text_area("Extracted Text", text, height=300)
            except Exception as e:
                st.error(f"Error in PDF extraction: {str(e)}")

else:  # Web Page URL
    url = st.text_input("Enter Web Page URL")
    if url:
        st.success("URL submitted successfully!")
        
        if extraction_method == "BeautifulSoup (Web Scraping)":
            st.info("Using BeautifulSoup for web scraping...")
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                st.text_area("Extracted Text", text, height=300)
            except Exception as e:
                st.error(f"Error in web scraping: {str(e)}")
        
        elif extraction_method == "Enterprise Web Extraction Tool":
           st.info("Using Enterprise Web Extraction Tool...")
            # Implement enterprise web extraction tool here

if st.button("Extract Data"):
    st.info("Data extraction initiated...")
    # Add any additional processing or display logic here
    st.success("Data extraction completed!")