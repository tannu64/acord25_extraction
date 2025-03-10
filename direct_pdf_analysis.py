"""
Direct PDF Analysis using Google Generative AI

This script uses the Google Generative AI client library to directly analyze PDF files
and extract checkbox information from ACORD 25 forms.
"""

import os
import sys
import json
import base64
from google import genai
from google.genai import types

# Configure the Gemini API
API_KEY = "AIzaSyASRuLY7yeWBRVFYFmc7Z93gL6HsPh21TE"
os.environ["GEMINI_API_KEY"] = API_KEY

def analyze_pdf(pdf_path):
    """
    Analyze a PDF file directly using Google Generative AI.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing the extracted checkbox information
    """
    # Initialize the client
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "exhausted" in error_msg.lower() or "429" in error_msg:
            return {
                "error": "API quota exceeded. Please try again later or use a different API key.",
                "details": error_msg
            }
        return {"error": f"Error initializing Gemini client: {error_msg}"}
    
    # Upload the file
    try:
        file = client.files.upload(file=pdf_path)
        print(f"Successfully uploaded file: {pdf_path}")
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "exhausted" in error_msg.lower() or "429" in error_msg:
            return {
                "error": "API quota exceeded. Please try again later or use a different API key.",
                "details": error_msg
            }
        return {"error": f"Error uploading file: {error_msg}"}
    
    # Create the prompt
    prompt = """
    You are an expert OCR system specialized in extracting checkbox data from ACORD 25 Certificate of Liability Insurance forms.
    
    TASK:
    Analyze this ACORD 25 form and extract all checkbox information with high accuracy.
    
    INSTRUCTIONS:
    1. Identify all checkboxes in the form.
    2. Determine whether each checkbox is checked (marked with X, ✓, or filled) or unchecked (empty).
    3. For each checkbox, provide:
       - The section it belongs to (e.g., "TYPE OF INSURANCE", "ADDL INSR", "SUBR WVD")
       - The label or text associated with the checkbox
       - Whether it is checked (TRUE) or unchecked (FALSE)
    
    IMPORTANT CONSIDERATIONS:
    - The ACORD 25 form has several main sections with checkboxes:
      1. TYPE OF INSURANCE section with options like:
         - COMMERCIAL GENERAL LIABILITY
         - CLAIMS-MADE
         - OCCUR
         - AUTOMOBILE LIABILITY
         - ANY AUTO
         - OWNED AUTOS ONLY
         - SCHEDULED AUTOS
         - HIRED AUTOS ONLY
         - NON-OWNED AUTOS ONLY
         - UMBRELLA LIAB
         - EXCESS LIAB
         - WORKERS COMPENSATION AND EMPLOYERS' LIABILITY
      2. ADDL INSR column (Additional Insured)
      3. SUBR WVD column (Subrogation Waived)
      4. GEN'L AGGREGATE LIMIT APPLIES PER section with options:
         - POLICY
         - PROJECT
         - LOC
      5. DESCRIPTION OF OPERATIONS section
    
    CHECKBOX DETECTION TIPS:
    - In ACORD forms, checkboxes are often square boxes that may be filled, contain an X, or be empty.
    - Checked boxes may appear as filled squares, squares with X marks, or squares with check marks.
    - Unchecked boxes appear as empty squares or outlined squares without any marks inside.
    - Some checkboxes might be partially filled or have faint marks - these should be considered checked.
    - Pay attention to the relative position of checkboxes and their labels.
    
    SPECIFIC CHECKBOXES TO LOOK FOR:
    1. In the "Commercial General Liability" section, look for "CLAIMS-MADE" and "OCCUR" checkboxes
    2. In the "Gen'l Aggregate Limit Applies Per" section, look for "POLICY", "PROJECT", and "LOC" checkboxes
    3. In the "Automobile Liability" section, look for "ANY AUTO", "OWNED AUTOS ONLY", "SCHEDULED AUTOS", "HIRED AUTOS ONLY", and "NON-OWNED AUTOS ONLY" checkboxes
    4. In the "Umbrella Liab" section, look for "OCCUR" and "CLAIMS-MADE" checkboxes
    5. In the "Excess Liab" section, look for "OCCUR" and "CLAIMS-MADE" checkboxes
    6. In the "Workers Compensation" section, look for "PER STATUTE" and "OTHER" checkboxes
    
    FORMAT:
    Return the results as a JSON object with the following structure:
    {
        "checkboxes": [
            {
                "section": "section_name",
                "label": "checkbox_label",
                "is_checked": true/false
            },
            ...
        ]
    }
    
    ACCURACY REQUIREMENTS:
    - Precision must be ≥97% (minimize false positives)
    - Recall must be ≥90% (identify at least 90% of all checkboxes)
    
    IMPORTANT: Be very careful to accurately determine if a checkbox is checked or not. Look closely at the visual appearance of each checkbox.
    """
    
    # Set up the model and content
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=file.uri,
                    mime_type=file.mime_type,
                ),
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    
    # Generate content configuration
    generate_content_config = types.GenerateContentConfig(
        temperature=0.1,  # Lower temperature for more deterministic results
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )
    
    try:
        # Generate content
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        # Extract JSON from the response
        response_text = response.text
        
        # Try to parse the JSON
        try:
            # Find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                return {"error": "No JSON found in response", "raw_response": response_text}
        except Exception as e:
            return {"error": f"Error parsing JSON: {str(e)}", "raw_response": response_text}
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "exhausted" in error_msg.lower() or "429" in error_msg:
            return {
                "error": "API quota exceeded. Please try again later or use a different API key.",
                "details": error_msg
            }
        return {"error": f"Error generating content: {error_msg}"}

def main():
    """Main function."""
    # Check if a PDF file was provided
    if len(sys.argv) < 2:
        print("Usage: python direct_pdf_analysis.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found")
        sys.exit(1)
    
    # Analyze the PDF
    print(f"Analyzing PDF: {pdf_path}")
    result = analyze_pdf(pdf_path)
    
    # Save the result
    output_path = "results/direct_extraction_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Results saved to {output_path}")
    
    # Print the number of checkboxes found
    if "checkboxes" in result:
        print(f"Found {len(result['checkboxes'])} checkboxes")
        
        # Print all checkboxes
        print("\nCheckboxes:")
        for i, checkbox in enumerate(result["checkboxes"]):
            checked_status = "✓" if checkbox.get("is_checked", False) else "☐"
            print(f"{i+1}. [{checked_status}] Section: {checkbox['section']}, Label: {checkbox['label']}")
    else:
        print("No checkboxes found")
        if "error" in result:
            print(f"Error: {result['error']}")
            if "details" in result:
                print(f"Details: {result['details']}")
        if "raw_response" in result:
            print(f"Raw response: {result['raw_response']}")

if __name__ == "__main__":
    main()