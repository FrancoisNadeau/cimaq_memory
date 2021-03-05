# Overview of the eprime2events directory

## Python Scripts (in usage order)
  - cimaq_utils.py
  - extract_all_events.py
  - fetch_cimaq_utils.py
  - clean_all_events.py

### cimaq_utils.py
  - Utility functions meant to be transferable (WIP)

### extract_all_events.py
  - Unzip, eprime files
  - Sort wanted files from archives
    - Only files containing Prefixes
      (more like suffixes, but anyway...) shared
      between all wanted files
  - Returns 3 '.txt' files (following are the "suffixes")
    - Onset-Event-Encoding_CIMAQ_*.txt
    - Output_Retrieval_CIMAQ_*.txt
    - Output-Responses-Encoding_CIMAQ*.txt

### fetch_cimaq_utils.py
  - Utility functions specific to CIMA-Q
  - Helps fetching data like a Nilearn/BIDS dataset

### clean_all_events.py
  - Creates BIDS compliant 'events' and 'behavioural' files
    - Merges the divided encoding sheets
  - Returns encoding & retrieval '.tsv' sheets
    - **_task-Memory_events.tsv**
    - **_task-Retrieval_behavioural.tsv**
  - Only needs CIMA-Q dataset location path as parameter
#### Output stored in 'cimaq_enc_ret2021'

## JSON  files
    - PostScanBehav_CIMAQ_memory.json
      - Headers, metrics and values description (Retrieval)
      - Usage:
        - Create event files in Nistats/Nilearn (to label fMRI frames)
        - Create BIDS compliant "task_description.json" file

    - TaskFile_headers_CIMAQ_memory.json
      -  Headers, metrics and values description (Encoding)
      - Create BIDS compliant post-scan behavioral task files

## Notebook
### testing_fetch.ipynb
  - Test each 'fetch_cimaq_utils.py' function in
    an individual cell and display outputs

#### Notes from St-Laurent, M. (2019):
  - Participants identifiers:
    - 6-digit: 'dccid'
    - 7-digit: 'pscid'
