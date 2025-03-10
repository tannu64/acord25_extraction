"""
Improved script to extract text from a PDF and use Gemini to analyze it.
"""

import os
import sys
import json
import PyPDF2
import google.generativeai as genai
import base64
from PIL import Image
import tempfile
import subprocess
import re
import io

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

def convert_pdf_to_images(pdf_path, output_dir=None):
    """Convert PDF to images using PyPDF2 and PIL as a fallback."""
    try:
        # Try to use pdf2image if available
        from pdf2image import convert_from_path
        
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        try:
            images = convert_from_path(pdf_path)
            image_paths = []
            
            for i, image in enumerate(images):
                image_path = os.path.join(output_dir, f"page_{i+1}.png")
                image.save(image_path, "PNG")
                image_paths.append(image_path)
            
            return image_paths
        except Exception as e:
            print(f"Warning: pdf2image failed: {str(e)}")
            # Fall back to PyPDF2 + PIL
            return convert_pdf_to_images_with_pypdf2(pdf_path, output_dir)
    except ImportError:
        print("Warning: pdf2image not installed. Using PyPDF2 + PIL instead.")
        # Fall back to PyPDF2 + PIL
        return convert_pdf_to_images_with_pypdf2(pdf_path, output_dir)

def convert_pdf_to_images_with_pypdf2(pdf_path, output_dir=None):
    """Convert PDF to images using PyPDF2 and PIL."""
    try:
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            image_paths = []
            
            # Try to extract images from each page
            for i, page in enumerate(reader.pages):
                try:
                    # Create a blank white image for the page
                    width, height = 2000, 2800  # Default size, adjust as needed
                    img = Image.new('RGB', (width, height), 'white')
                    
                    # Try to extract images from the page
                    for image_file_object in page.images:
                        try:
                            image = Image.open(io.BytesIO(image_file_object.data))
                            # Paste the image onto the blank page
                            img.paste(image, (0, 0))
                        except Exception as e:
                            print(f"Warning: Could not extract image from page {i+1}: {str(e)}")
                    
                    # Save the image
                    image_path = os.path.join(output_dir, f"page_{i+1}.png")
                    img.save(image_path, "PNG")
                    image_paths.append(image_path)
                except Exception as e:
                    print(f"Warning: Could not process page {i+1}: {str(e)}")
            
            if not image_paths:
                print("Warning: Could not extract any images from the PDF.")
                return []
            
            return image_paths
    except Exception as e:
        print(f"Warning: PyPDF2 + PIL conversion failed: {str(e)}")
        return []

def encode_image_to_base64(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_text_and_images(text, image_paths=None):
    """Analyze text and images using Gemini."""
    # Create the prompt for Gemini
    prompt = f"""
    You are an expert OCR system specialized in extracting checkbox data from ACORD 25 Certificate of Liability Insurance forms.
    
    TASK:
    Analyze the provided text and images (if available) extracted from an ACORD 25 form and extract all checkbox information.
    
    INSTRUCTIONS:
    1. Identify all checkboxes in the form based on the text and images.
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
      4. DESCRIPTION OF OPERATIONS section
    
    - Checkboxes may be indicated by 'X', '✓', '■', '□', or similar symbols in the text.
    - Look for patterns like "[ ]" or "[X]" or "☐" or "☑" in the text.
    - In the images, look for filled or marked boxes versus empty boxes.
    - Pay special attention to the visual appearance of checkboxes in the images.
    - If you can't determine if a checkbox is checked from the text, use the image to make a determination.
    - If there's a conflict between text and image, prioritize the image.
    
    CHECKBOX DETECTION TIPS:
    - In ACORD forms, checkboxes are often square boxes that may be filled, contain an X, or be empty.
    - Checked boxes may appear as filled squares, squares with X marks, or squares with check marks.
    - Unchecked boxes appear as empty squares or outlined squares without any marks inside.
    - Some checkboxes might be partially filled or have faint marks - these should be considered checked.
    - Pay attention to the relative position of checkboxes and their labels.
    
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
    
    # If we have images, include them in the analysis
    if image_paths and len(image_paths) > 0:
        # For multimodal analysis with images
        contents = [prompt]
        
        # Add images to the prompt
        for image_path in image_paths:
            try:
                image_data = encode_image_to_base64(image_path)
                contents.append({
                    "mime_type": "image/png",
                    "data": image_data
                })
            except Exception as e:
                print(f"Warning: Could not process image {image_path}: {str(e)}")
        
        # Generate content with text and images
        try:
            response = model.generate_content(contents)
        except Exception as e:
            print(f"Error generating content with images: {str(e)}")
            # Fall back to text-only analysis
            response = model.generate_content(prompt)
    else:
        # Text-only analysis
        response = model.generate_content(prompt)
    
    # Extract the JSON from the response
    try:
        # Find JSON in the response
        response_text = response.text
        
        # Try to find JSON pattern using regex
        json_pattern = r'({[\s\S]*})'
        json_matches = re.findall(json_pattern, response_text)
        
        if json_matches:
            for json_str in json_matches:
                try:
                    result = json.loads(json_str)
                    if "checkboxes" in result:
                        return result
                except:
                    continue
        
        # If regex approach fails, try the traditional approach
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            try:
                result = json.loads(json_str)
                return result
            except:
                pass
        
        # If all attempts fail, return the error
        result = {"error": "No valid JSON found in response", "raw_response": response_text}
    except Exception as e:
        result = {"error": str(e), "raw_response": response.text}
    
    return result

def analyze_text(text):
    """Analyze text using Gemini (wrapper for backward compatibility)."""
    return analyze_text_and_images(text)

def main():
    """Main function."""
    # Check if a PDF file was provided
    if len(sys.argv) < 2:
        print("Usage: python test_pdf_text_improved.py <pdf_file>")
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
    
    # Try to convert PDF to images for visual analysis
    print("Attempting to convert PDF to images for visual analysis...")
    image_paths = convert_pdf_to_images(pdf_path)
    
    if image_paths and len(image_paths) > 0:
        print(f"Successfully converted PDF to {len(image_paths)} images")
        # Analyze the text and images
        print("Analyzing text and images with improved prompt...")
        result = analyze_text_and_images(text, image_paths)
    else:
        # Fall back to text-only analysis
        print("Falling back to text-only analysis...")
        result = analyze_text_and_images(text)
    
    # Save the result
    output_path = "results/improved_extraction_results.json"
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