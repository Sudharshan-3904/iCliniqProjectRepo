## Modules
1. [Chatbot](#chatbot)
2. [File Storage](#file-storage)
3. [OCR](#ocr)
4. [Tabular OCR](#tabular-ocr)
5. [Translator](#translator)
6. [Filtering and Searching](#filtering-and-searching)

## Chatbot
Current Status:
1. Basic funcationality done
2. Can handle multiligual input and resond in the input language

Next Step:
1. Implement a RAG model
2. Try meditron model

Remarks:
- phi-4 model from LMStudio not good follow up questions, not able to upload file
- deepseek ( r1 and v2 code lite ) not enough resources for execution 


## File Storage
Current Status:
1. Can store and retrieve data from sqlite3 db based on username and filename
2. Can read store multiple input filetypes

Next Step:
1. Implement structured file storage
2. Ensure consistent storage and retrieval in both sqlite3 and MongoDB

Remarks:
- Uses both MongoDB and sqlite3

## OCR
Current Status:
1. Able to successfully read charecters from the file

Next Step:
1. Try to extract the structure of the table within the same module
2. Improve accuracy on the model
3. Implement an ML or DL model for OCR
4. Experimenting on yolo v5
    - Need to annotate the input documents

Remarks:
- Uses tressaract installed locally on the system


## Tabular OCR
Current Status:
1. Able to extract the structure of any table
2. Cannot extract the data from the table

Next Step:
1. Try improving data extraction
2. Try to create a un-structured data. Eg. Like reports and text summaries

Remarks:
- Uses Paddle OCR module


## Translator
Current Status:
1. Uses google translate
2. Use a set of prefed languages

Next Step:
1. Implement a local ML model for translation

Remarks:
- Try testing the model for flexibilyt and accuracy


## Filtering and Searching
Current Status:
1. Done using pandas
2. Able to handle complex querries and filtering criteria
3. Reformat to fint into module with file initialization and column exception handling

Next Step:
1. Inegration with both MongoDB and sqlite database
2. Integration with RAG model ( Chatbot )

Remarks:
- Completed for basic funcitonality


## Resources Neede
1. Compute Power
- Need compute resources for loading and processing files
- Like a virtual server like compute server
- Main needs are vRam, vCPUs, and storage
- EG. Amazon EC2

2. Data
- Need data for training a yolo v5 model
- Dataset needs to be annotated