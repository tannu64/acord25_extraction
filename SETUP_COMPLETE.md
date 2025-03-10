# ACORD 25 Checkbox Extraction - Setup Complete

## Project Overview

You have successfully set up the ACORD 25 Checkbox Extraction project. This project uses Google's Gemini 2.0 Flash model to extract checkbox data from ACORD 25 Certificate of Liability Insurance forms with high precision and recall.

## What's Included

### Project Structure
```
acord25_extraction/
├── data/                  # Directory for storing ACORD 25 form images and PDFs
│   └── sample_ground_truth.json  # Sample ground truth data for testing
├── results/               # Directory for storing extraction results and metrics
├── scripts/               # Python scripts for extraction and evaluation
│   ├── acord25_extractor.py     # Main extraction script
│   ├── evaluate_performance.py  # Script for evaluating extraction performance
│   ├── prompt_optimizer.py      # Script for optimizing extraction prompts
│   ├── test_gemini_api.py       # Script to test the Gemini API connection
│   └── ai_studio_guide.md       # Guide for using Google AI Studio
├── install.bat            # Installation script
├── requirements.txt       # Python dependencies
├── run_extraction.bat     # Script to run the extraction
└── README.md              # Project documentation
```

### Key Components

1. **Extraction Engine**: The `acord25_extractor.py` script contains the main logic for extracting checkbox data from ACORD 25 forms using Gemini 2.0 Flash.

2. **Performance Evaluation**: The `evaluate_performance.py` script calculates precision and recall metrics to evaluate the extraction performance.

3. **Prompt Optimization**: The `prompt_optimizer.py` script helps optimize the prompt for better extraction results.

4. **Google AI Studio Guide**: The `ai_studio_guide.md` file provides instructions for using Google AI Studio to test and optimize prompts.

## Next Steps

1. **Install Dependencies**: Run `install.bat` to create a virtual environment and install the required dependencies.

2. **Prepare Sample Data**: Place sample ACORD 25 form images or PDFs in the `data` directory.

3. **Test the API Connection**: Run `python scripts/test_gemini_api.py` to verify that the Gemini API is working correctly.

4. **Extract Checkbox Data**: Run `run_extraction.bat data/your_form.pdf` to extract checkbox data from a form.

5. **Evaluate Performance**: Use the `evaluate_performance.py` script to calculate precision and recall metrics.

6. **Optimize the Prompt**: Use the `prompt_optimizer.py` script to improve extraction accuracy.

## Performance Requirements

The project aims to achieve:
- Precision: ≥97%
- Recall: ≥90%

## API Key

The project is currently configured with the provided API key:
```
AIzaSyABVyKdEdx0Wn1Tdk_elOvteyOQvFUfuWo
```

## Additional Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs/gemini_api)
- [ACORD Forms](https://www.acord.org/standards-architecture/acord-forms)

## Support

If you encounter any issues or have questions, please refer to the documentation or contact the project maintainer.

Happy extracting! 