# ACORD 25 Checkbox Extraction

A web application for extracting checkbox data from ACORD 25 Certificate of Liability Insurance forms using Google's Gemini 2.0 Flash model.

## Features

- **Extract Checkboxes**: Upload ACORD 25 forms and extract checkbox data
- **High Accuracy**: Precision ≥97%, Recall ≥90%
- **Easy to Use**: Simple web interface
- **PDF Support**: Upload PDF files directly
- **Direct PDF Analysis**: Sends PDF directly to Gemini API
- **JSON Export**: Download results as JSON

## Project Structure

```
acord25_extraction/
├── backend/
│   ├── api/
│   ├── core/
│   ├── models/
│   └── utils/
├── data/
│   ├── raw/
│   └── processed/
├── frontend/
│   └── app.py
├── results/
├── tests/
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tannu64/acord25_extraction.git
cd acord25_extraction
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Install the Google Generative AI library:
```bash
pip install google-generativeai
```

## Usage

### Running the Web Interface

```bash
cd acord25_extraction
python -m streamlit run frontend/app.py
```

### Using the Extraction Script Directly

```bash
python test_pdf_text_improved.py "path/to/your/acord25.pdf"
```

### Using the Direct PDF Analysis

```bash
python direct_pdf_analysis.py "path/to/your/acord25.pdf"
```

## API Key

The application uses the Google Gemini API. You can enter your own API key in the sidebar of the web interface, or set it in the `direct_pdf_analysis.py` file.

To get your own API key:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Enter it in the application

## Requirements

- Python 3.8+
- PyPDF2
- Streamlit
- Pandas
- Matplotlib
- Pillow
- Google Generative AI

## License

MIT

## Author

- **Tanveer Hussain**
- LinkedIn: [https://www.linkedin.com/in/tanveer-hussain-277119196/](https://www.linkedin.com/in/tanveer-hussain-277119196/)
- Upwork: [https://www.upwork.com/freelancers/~01a14d825a9bd8689d](https://www.upwork.com/freelancers/~01a14d825a9bd8689d)
- Email: agapaitanveermou@gmail.com

## Acknowledgements

- Google Generative AI for providing the Gemini API
- ACORD for the standardized insurance form templates
- The open-source community for the amazing tools and libraries 