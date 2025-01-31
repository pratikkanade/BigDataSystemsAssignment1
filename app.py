import streamlit as st
import requests

# Set FastAPI URL
API_BASE_URL = "http://127.0.0.1:8000"

st.title("PDF & Web Page Data Extractor")

# Sidebar input selection
input_source = st.sidebar.radio("Select Input Source", ["PDF Upload", "Web Page URL"])

uploaded_file = None
url = None

if input_source == "PDF Upload":
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

elif input_source == "Web Page URL":
    url = st.text_input("Enter Web Page URL")

# Select Extraction Method
extraction_method = st.selectbox(
    "Select Extraction Method",
    ["Adobe PDF Services (Enterprise)", "PyMuPDF (Open Source)"]
)

if st.button("Extract Data"):
    if input_source == "PDF Upload" and uploaded_file:
        st.info("Uploading PDF for processing...")

        parser_type = "Enterprise" if extraction_method == "Adobe PDF Services (Enterprise)" else "Open Source"

        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            params = {"parser_type": parser_type}
            response = requests.post(f"{API_BASE_URL}/upload/pdf", files=files, params=params)

            if response.status_code == 200:
                st.success("File uploaded and parsed successfully!")
                st.write(f"File URL: {response.json().get('file_url')}")
            else:
                st.error(response.json()["detail"])

        except Exception as e:
            st.error(f"Error during PDF upload: {str(e)}")

    elif input_source == "Web Page URL" and url:
        st.info("Processing Web Page...")
        parser_type = "Open Source"  # Only Open Source parser for Web Pages
        response = requests.post(f"{API_BASE_URL}/upload/webpage", json={"url": url, "parser_type": parser_type})

        if response.status_code == 200:
            st.success("Web page processed successfully!")
        else:
            st.error(response.json()["detail"])

    else:
        st.error("Please provide valid input before extraction.")

# Fetch Parsed Content
st.header("Fetch Extracted Content")
filename = st.text_input("Enter filename (without .pdf) to fetch parsed content")

if st.button("Fetch Extracted Content"):
    params = {"filename": filename, "parser_type": extraction_method}
    response = requests.get(f"{API_BASE_URL}/fetch/filename", params=params)

    if response.status_code == 200:
        st.success("File Fetched Successfully!")
        st.text_area("Extracted Content", response.text, height=300)
    else:
        st.error(response.json()["detail"])
