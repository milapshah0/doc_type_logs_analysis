import streamlit as st
import loganalysis

def main():
    st.set_page_config(page_title="Analysis Log", layout="wide")
    uploader = loganalysis.FileUploader()
    uploader.execute()

if __name__ == "__main__":
    main()    
