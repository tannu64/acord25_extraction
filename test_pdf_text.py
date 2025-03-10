"""
Script to extract text from a PDF and use Gemini to analyze it.
"""

import os
import sys
import json
import PyPDF2
import google.generativeai as genai

# Configure the Gemini API
API_KEY = "AIzaSyABVyKdEdx0Wn1Tdk_elOvteyOQvFUfuWo"
genai.configure(api_key=API_KEY)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text

def analyze_text(text):
    """Analyze text using Gemini."""
    # Create the prompt for Gemini
    prompt = f"""
    You are an expert OCR system specialized in extracting checkbox data from ACORD 25 forms.
    
    TASK:
    Analyze the provided text extracted from an ACORD 25 Certificate of Liability Insurance form and extract all checkbox information.
    
    INSTRUCTIONS:
    1. Identify all checkboxes in the form based on the text.
    2. Determine whether each checkbox is checked (marked with X, ✓, or filled) or unchecked (empty).
    3. For each checkbox, provide:
       - The section it belongs to (e.g., "COVERAGES", "DESCRIPTION OF OPERATIONS")
       - The label or text associated with the checkbox
       - Whether it is checked (TRUE) or unchecked (FALSE)
    
    IMPORTANT CONSIDERATIONS:
    - Pay special attention to the "TYPE OF INSURANCE" section which contains many checkboxes.
    - Look for checkboxes in the "ADDL INSR", "SUBR WVD", and similar columns.
    - Some checkboxes may be indicated by 'X', '✓', or similar symbols in the text.
    
    FORMAT:
    Return the results as a JSON object with the following structure:
    {{
        "checkboxes": [
            {{
                "section": "section_name",
                "label": "checkbox_label",
                "is_checked": true/false
            }},
            ...
        ]
    }}
    
    ACCURACY REQUIREMENTS:
    - Precision must be ≥97% (minimize false positives)
    - Recall must be ≥90% (identify at least 90% of all checkboxes)
    
    Here is the extracted text from the ACORD 25 form:
    
    {text}
    """
    
    # Create the model
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Generate content
    response = model.generate_content(prompt)
    
    # Extract the JSON from the response
    try:
        # Find JSON in the response
        response_text = response.text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
        else:
            # If no JSON found, use the whole response
            result = {"error": "No JSON found in response", "raw_response": response_text}
    except Exception as e:
        result = {"error": str(e), "raw_response": response.text}
    
    return result

def main():
    """Main function."""
    # Check if a PDF file was provided
    if len(sys.argv) < 2:
        print("Usage: python test_pdf_text.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found")
        sys.exit(1)
    
    # Extract text from the PDF
    print(f"Extracting text from PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    # Save the extracted text
    text_path = "data/processed/extracted_text.txt"
    os.makedirs(os.path.dirname(text_path), exist_ok=True)
    
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Extracted text saved to {text_path}")
    
    # Analyze the text
    print("Analyzing text...")
    result = analyze_text(text)
    
    # Save the result
    output_path = "results/extraction_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Results saved to {output_path}")
    
    # Print the number of checkboxes found
    if "checkboxes" in result:
        print(f"Found {len(result['checkboxes'])} checkboxes")
        
        # Print the first 5 checkboxes
        print("\nSample checkboxes:")
        for i, checkbox in enumerate(result["checkboxes"][:5]):
            print(f"{i+1}. Section: {checkbox['section']}, Label: {checkbox['label']}, Checked: {checkbox['is_checked']}")
    else:
        print("No checkboxes found")
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Raw response: {result.get('raw_response', 'No response')}")

if __name__ == "__main__":
    main() 