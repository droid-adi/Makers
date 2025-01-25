# PhonePe Statement Reader & Monthly Analysis Web App

This web application processes PhonePe statement PDFs, extracts transaction data, and provides monthly financial analysis in a user-friendly interface. It helps users understand their spending and earnings trends.

## Features

- **PDF Parsing**: Automatically reads and extracts data from PhonePe statement PDFs.
- **Monthly Analysis**: Summarizes transactions month-wise for better financial insights.
- **Category Breakdown**: Groups transactions into categories like payments, refunds, and transfers.
- **Visualization**: Displays data using charts and graphs for clear trend analysis.
- **Export Options**: Download analyzed data as CSV or PDF.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (or React.js)
- **Backend**: Python (Flask or FastAPI)
- **PDF Parsing**: `PyPDF2` or `pdfplumber`
- **Data Analysis**: `pandas`, `numpy`
- **Visualization**: `Matplotlib` or `Chart.js`
- **Database (Optional)**: SQLite or MySQL (to save processed data)

## Installation and Setup

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Steps to Install

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/phonepe-statement-reader.git
   cd phonepe-statement-reader
