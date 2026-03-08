# MDAC
Automated analysis of PDF documents using OCR and assisted processing

1. **This project proposes the implementation of an automated system** that analyzes declarations in PDF format, extracts relevant personal information (especially the Personal Numeric Code – CNP), performs derived processing (sex, age), and generates statistics and summary reports similar to the requirements encountered in practical laboratory assignments.

2. **Project Objectives**
   The general objective of the project is to automate the process of analyzing administrative PDF documents, regardless of whether they are text-based documents or scanned documents.

Specific objectives include: automatically identifying the type of PDF document (text/scanned), applying OCR for scanned documents, automatically extracting the CNP from the text, determining sex and age based on the CNP, centralizing the information in a structured format (CSV/Excel), and generating a PDF report containing relevant statistics.

3. **Methodology**
   The application is implemented in Python and structured as an automated pipeline. For each PDF file, the system first attempts to extract the text directly; if the result is insufficient, the document is considered scanned, the pages are converted into images, and OCR is applied. The obtained text is analyzed using regular expressions to identify the CNP, and from the CNP structure the sex and age are calculated. The results are centralized in a table and exported to CSV/Excel, while the statistics are summarized in a PDF report.

4. **Obtained Results**
   After running the application on a set of documents, the system automatically processed both text-based PDFs and scanned PDFs. The CNPs were extracted, the sex and age of individuals were determined, and statistics were generated such as: the total number of processed documents, the number of female individuals, the number of individuals over 50 years old, and the number of documents processed using OCR.
