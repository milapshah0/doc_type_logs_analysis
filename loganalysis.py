import streamlit as st
import re
from io import StringIO
import pandas as pd

pattern_logdata = re.compile(
    r"\[([a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})\]\s+(.*?)\n"
)

# Result for document 'Andy_Test/Engine V2/Test classification v2 engine/Dev security.docx' : {'doc_type': 'legal_contract', 'confidence': 0.5}
pattern_result = re.compile(
    r"\[([a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})\] Result for document '(.*?)' : {'doc_type': (.*?)(?:, 'confidence': (.*?))?}"
)

# Time taken for 'processing Andy_Test/Engine V2/Test classification v2 engine/Dev security.docx using lib-document-type-detector v0.3.2' : 66.698 ms
pattern_time = re.compile(
    r"\[([a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})\] Time taken for 'processing (.*?) using lib-document-type-detector (.*?)' : (.*?) ms"
)

patterns_job_request = re.compile(
    r"\[([\w-]+)\] Request recevied\. Document metadata : {'job_id': '(\d+)', .*?"
)

pattern_documents = re.compile(
    r"\[.*?\] \[.*?\] \[.*?\] \[.*?\] \[.*?\] Request recevied\. Document metadata : \{.*? '.*?', '.*?', '.*?', '.*?', 'document_xpath': '(.*?)', '.*?'"
)


class FileData:
    request_id: str = ""
    document_name: str = ""
    doc_type: str = ""
    confidence: str = ""
    duration: str = ""
    job_id: str = ""
    model_version: str = ""

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
    input_file_name: str = ""

    def __init__(self) -> None:
        uploaded_file = st.file_uploader("Upload log file")
        if uploaded_file is not None:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            # To read file as string:
            self.string_data = stringio.read()
            self.input_file_name = uploaded_file.name

    def execute(self) -> None:
        if self.string_data is None:
            return

        run_stats_dict, model_version = self._calculate()
        jobid_runstats_dict = {}

        for value in run_stats_dict.values():
            if value.job_id in jobid_runstats_dict:
                jobid_runstats_dict[value.job_id].append(value)
            else:
                jobid_runstats_dict[value.job_id] = [value]

        job_id_list = []
        model_version_list = []
        total_count_list = []
        resume_count_list = []
        legal_count_list = []
        sec_count_list = []
        none_count_list = []
        for job_id, stats_list in jobid_runstats_dict.items():
            job_id_list.append(job_id)
            model_version_list.append(stats_list[0].model_version)
            total_count_list.append(len(stats_list))
            resume_count = len(
                [x for x in stats_list if x.get_doc_type() == "'resume'"]
            )
            resume_count_list.append(resume_count)
            legal_count = len(
                [x for x in stats_list if x.get_doc_type() == "'legal_contract'"]
            )
            legal_count_list.append(legal_count)
            sec_count = len(
                [x for x in stats_list if x.get_doc_type() == "'sec_filing'"]
            )
            sec_count_list.append(sec_count)
            none_count = len([x for x in stats_list if x.get_doc_type() == "None"])
            none_count_list.append(none_count)

        df = pd.DataFrame(
            {
                "Job": job_id_list,
                "Model": model_version_list,
                "Total": total_count_list,
                "Resumes": resume_count_list,
                "Sec Filings": sec_count_list,
                "Legals": legal_count_list,
                "None": none_count_list,
            }
        )

        st.divider()

        st.table(df)

        st.divider()

    def _calculate(self):
        matches_result = re.findall(pattern_result, self.string_data)
        matches_time = re.findall(pattern_time, self.string_data)
        matches_job_request = re.findall(patterns_job_request, self.string_data)
        run_stats_dict = {}
        requestid_jobid_dict = {}

        for match in matches_job_request:
            request_id, job_id = match
            requestid_jobid_dict[request_id] = job_id

        for match in matches_result:
            file_data = FileData()
            (
                file_data.request_id,
                file_data.document_name,
                file_data.doc_type,
                file_data.confidence,
            ) = match
            file_data.job_id = requestid_jobid_dict.get(file_data.request_id)
            run_stats_dict[file_data.request_id] = file_data

        model_version = ""
        for match in matches_time:
            request_id, _, model_version, duration = match
            file_data = run_stats_dict.get(request_id)
            file_data.duration = duration
            file_data.model_version = model_version

        return run_stats_dict, model_version
