"""
Simple script to test the PDF file.
"""

import os
import sys
import base64
import json
from pdf2image import convert_from_path
from PIL import Image
import google.generativeai as genai

# Configure the Gemini API
API_KEY = "AIzaSyABVyKdEdx0Wn1Tdk_elOvteyOQvFUfuWo"
genai.configure(api_key=API_KEY)

def convert_pdf_to_images(pdf_path, output_dir=None):
    """Convert a PDF to images."""
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    image_paths = []
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"{base_filename}_page_{i+1}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)
        
    return image_paths

def encode_image_to_base64(image_path):
    """Encode an image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def extract_checkboxes(image_path):
    """Extract checkbox data from an image."""
    # Encode the image to base64
    base64_image = encode_image_to_base64(image_path)
    
    # Create the prompt for Gemini
    prompt = """
    You are an expert OCR system specialized in extracting checkbox data from ACORD 25 forms.
    
    TASK:
    Analyze the provided ACORD 25 Certificate of Liability Insurance form and extract all checkbox information.
    
    INSTRUCTIONS:
    1. Identify all checkboxes in the form.
    2. Determine whether each checkbox is checked (marked with X, ✓, or filled) or unchecked (empty).
    3. For each checkbox, provide:
       - The section it belongs to (e.g., "COVERAGES", "DESCRIPTION OF OPERATIONS")
       - The label or text associated with the checkbox
       - Whether it is checked (TRUE) or unchecked (FALSE)
    
    IMPORTANT CONSIDERATIONS:
    - Pay special attention to the "TYPE OF INSURANCE" section which contains many checkboxes.
    - Look for checkboxes in the "ADDL INSR", "SUBR WVD", and similar columns.
    - Some checkboxes may be small or have low contrast - examine the image carefully.
    - Checkboxes may be marked with different symbols (X, ✓, filled) - all these count as checked.
    
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
    
    Analyze the image thoroughly and provide accurate results.
    """
    
    # Create the model
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Generate content
    response = model.generate_content([prompt, {"mime_type": "image/png", "data": base64_image}])
    
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
    
    # Add the image path to the result
    result["image_path"] = image_path
    
    return result

def main():
    """Main function."""
    # Check if a PDF file was provided
    if len(sys.argv) < 2:
        print("Usage: python test_pdf.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found")
        sys.exit(1)
    
    # Convert the PDF to images
    print(f"Converting PDF to images: {pdf_path}")
    image_paths = convert_pdf_to_images(pdf_path, "data/processed")
    
    # Process the first page
    print(f"Processing page 1...")
    result = extract_checkboxes(image_paths[0])
    
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

if __name__ == "__main__":
    main() 