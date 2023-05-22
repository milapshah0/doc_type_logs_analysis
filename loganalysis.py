import streamlit as st
import re
from io import StringIO

pattern_logdata = re.compile(r"\[([a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})\]\s+(.*?)\n")

# Result for document 'Andy_Test/Engine V2/Test classification v2 engine/Dev security.docx' : {'doc_type': 'legal_contract', 'confidence': 0.5}
pattern_result = re.compile(r"Result for document '(.*?)' : {'doc_type': (.*?)(?:, 'confidence': (.*?))?}")

# Time taken for 'processing Andy_Test/Engine V2/Test classification v2 engine/Dev security.docx using lib-document-type-detector v0.3.2' : 66.698 ms
pattern_time = re.compile(r"processing (.*?) using lib-document-type-detector (.*?)' : (.*?) ms")

class FileData:
    file_name: str = ''
    doc_type: str = ''
    confidence: str = ''
    duration: str = ''

    def __init__(self) -> None:
        pass
    
    def __repr__(self):
        return str(self.__dict__)
    
    def get_dict(self) -> dict:
        return self.__dict__
    
    def get_doc_type(self) -> str:
        return self.doc_type
    
class FileUploader:
    string_data: str = None

    def __init__(self) -> None:
        uploaded_file = st.file_uploader("Upload log file")
        if uploaded_file is not None:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            # To read file as string:
            self.string_data = stringio.read()

    def execute(self) -> None:
        if self.string_data is None:
            return
    
        results, model_version = self._calculate();
        model_col, total_col, resume_col, legal_col, sec_col, none_col = st.columns(6)

        model_col.metric(label="Model", value= model_version)
        total_col.metric(label="Total Count", value= len(results))
        
        resume_count = len([x for x in results.values() if x.get_doc_type() == "'resume'" ])
        resume_col.metric(label="Resume Count", value= resume_count)

        legal_count = len([x for x in results.values() if x.get_doc_type() == "'legal_contract'" ])
        legal_col.metric(label="Legal Count", value= legal_count)

        sec_count = len([x for x in results.values() if x.get_doc_type() == "'sec_filing'" ])
        sec_col.metric(label="sec filing Count", value= sec_count)

        none_count = len([x for x in results.values() if x.get_doc_type() is None or x.get_doc_type() == 'None'])
        none_col.metric(label="None of Above", value= none_count)
        
    
    def _calculate(self):
        matches_result = re.findall(pattern_result, self.string_data)
        matches_time = re.findall(pattern_time, self.string_data)
        text_data = {}

        for match in matches_result:
            file_data = FileData(); 
            file_data.file_name, file_data.doc_type, file_data.confidence = match 
            text_data[file_data.file_name] = file_data 
        model_version = ''
        for match in matches_time:
            file_name, model_version, _  = match 
            file_data = text_data.get(file_name) 
        return text_data, model_version
