#!/usr/bin/env python
"""
ACORD 25 Checkbox Extraction - Main Entry Point

This script serves as the main entry point for the ACORD 25 Checkbox Extraction application.
It provides a command-line interface for extracting checkbox data from ACORD 25 forms,
evaluating performance, and optimizing prompts.
"""

import os
import sys
import json
import click
from dotenv import load_dotenv
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Import backend modules
from backend.core.extractor import ACORD25CheckboxExtractor
from backend.core.evaluator import evaluate_performance
from backend.core.optimizer import PromptOptimizer
from backend.utils.logger import setup_logger

# Set up logging
logger = setup_logger()

@click.group()
def cli():
    """ACORD 25 Checkbox Extraction Tool

    This tool extracts checkbox data from ACORD 25 Certificate of Liability Insurance forms
    using Google's Gemini 2.0 Flash model.
    """
    pass

@cli.command()
@click.option('--input', '-i', required=True, help='Path to the input image or PDF file')
@click.option('--output', '-o', default='results/extraction_results.json', help='Path to save the extraction results')
@click.option('--model', '-m', default=os.getenv('DEFAULT_MODEL', 'gemini-2.0-flash'), help='The name of the Gemini model to use')
def extract(input, output, model):
    """Extract checkbox data from a single ACORD 25 form."""
    logger.info(f"Extracting checkbox data from {input}")
    
    # Initialize the extractor
    extractor = ACORD25CheckboxExtractor(model_name=model)
    
    # Check if the input file exists
    if not os.path.exists(input):
        logger.error(f"Input file '{input}' not found")
        sys.exit(1)
    
    # Process the input file
    file_extension = os.path.splitext(input)[1].lower()
    
    if file_extension == ".pdf":
        # Convert PDF to images
        logger.info(f"Converting PDF to images: {input}")
        image_paths = extractor.convert_pdf_to_images(input, os.path.join(os.path.dirname(input), "temp"))
        
        # Process the images
        logger.info(f"Processing {len(image_paths)} pages...")
        results = extractor.batch_process(image_paths)
    else:
        # Process a single image
        logger.info(f"Processing image: {input}")
        result = extractor.extract_checkboxes(input)
        logger.info(json.dumps(result, indent=2))
    
    # Save the results
    os.makedirs(os.path.dirname(output), exist_ok=True)
    extractor.save_results(output)
    logger.info(f"Extraction complete! Results saved to {output}")

@cli.command()
@click.option('--input-dir', '-i', required=True, help='Directory containing ACORD 25 forms')
@click.option('--output-dir', '-o', default='results', help='Directory to save the extraction results')
@click.option('--model', '-m', default=os.getenv('DEFAULT_MODEL', 'gemini-2.0-flash'), help='The name of the Gemini model to use')
def batch_process(input_dir, output_dir, model):
    """Process multiple ACORD 25 forms in batch."""
    logger.info(f"Batch processing ACORD 25 forms from {input_dir}")
    
    # Initialize the extractor
    extractor = ACORD25CheckboxExtractor(model_name=model)
    
    # Check if the input directory exists
    if not os.path.exists(input_dir):
        logger.error(f"Input directory '{input_dir}' not found")
        sys.exit(1)
    
    # Get all image and PDF files in the input directory
    image_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    pdf_extension = '.pdf'
    
    image_files = []
    pdf_files = []
    
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                image_files.append(file_path)
            elif ext == pdf_extension:
                pdf_files.append(file_path)
    
    # Process image files
    if image_files:
        logger.info(f"Processing {len(image_files)} image files...")
        image_results = extractor.batch_process(image_files)
    
    # Process PDF files
    for pdf_file in pdf_files:
        logger.info(f"Processing PDF file: {pdf_file}")
        # Convert PDF to images
        image_paths = extractor.convert_pdf_to_images(pdf_file, os.path.join(input_dir, "temp"))
        
        # Process the images
        pdf_results = extractor.batch_process(image_paths)
    
    # Save the results
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "batch_results.json")
    extractor.save_results(output_path)
    logger.info(f"Batch processing complete! Results saved to {output_path}")

@cli.command()
@click.option('--predictions', '-p', required=True, help='Path to the predictions JSON file')
@click.option('--ground-truth', '-g', required=True, help='Path to the ground truth JSON file')
@click.option('--output', '-o', default='results/performance_metrics.json', help='Path to save the metrics')
@click.option('--plot', '-pl', default='results/performance_plot.png', help='Path to save the plot')
def evaluate(predictions, ground_truth, output, plot):
    """Evaluate the performance of the checkbox extraction."""
    logger.info(f"Evaluating performance")
    
    # Check if the files exist
    if not os.path.exists(predictions):
        logger.error(f"Predictions file '{predictions}' not found")
        sys.exit(1)
    
    if not os.path.exists(ground_truth):
        logger.error(f"Ground truth file '{ground_truth}' not found")
        sys.exit(1)
    
    # Load predictions and ground truth
    with open(predictions, 'r') as f:
        pred_data = json.load(f)
    
    with open(ground_truth, 'r') as f:
        gt_data = json.load(f)
    
    # Evaluate performance
    metrics = evaluate_performance(pred_data, gt_data)
    
    # Print metrics
    logger.info("\nPerformance Metrics:")
    logger.info(f"Precision: {metrics['precision']:.2%}")
    logger.info(f"Recall: {metrics['recall']:.2%}")
    logger.info(f"F1 Score: {metrics['f1_score']:.2%}")
    logger.info(f"True Positives: {metrics['true_positives']}")
    logger.info(f"False Positives: {metrics['false_positives']}")
    logger.info(f"False Negatives: {metrics['false_negatives']}")
    
    # Check if the performance meets the requirements
    precision_requirement = float(os.getenv('MIN_PRECISION', 0.97))
    recall_requirement = float(os.getenv('MIN_RECALL', 0.90))
    
    if metrics["precision"] >= precision_requirement and metrics["recall"] >= recall_requirement:
        logger.info("\n✅ Performance meets the requirements!")
        logger.info(f"Required Precision: ≥{precision_requirement:.0%}, Achieved: {metrics['precision']:.2%}")
        logger.info(f"Required Recall: ≥{recall_requirement:.0%}, Achieved: {metrics['recall']:.2%}")
    else:
        logger.info("\n❌ Performance does not meet the requirements.")
        if metrics["precision"] < precision_requirement:
            logger.info(f"Required Precision: ≥{precision_requirement:.0%}, Achieved: {metrics['precision']:.2%}")
        if metrics["recall"] < recall_requirement:
            logger.info(f"Required Recall: ≥{recall_requirement:.0%}, Achieved: {metrics['recall']:.2%}")
    
    # Save metrics
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"\nMetrics saved to {output}")
    
    # Plot metrics
    from backend.utils.visualization import plot_metrics
    plot_metrics(metrics, plot)

@cli.command()
@click.option('--sample-image', '-i', required=True, help='Path to the sample image')
@click.option('--ground-truth', '-g', required=True, help='Path to the ground truth JSON file')
@click.option('--iterations', '-n', default=3, help='Number of optimization iterations')
@click.option('--output', '-o', default='results/optimized_prompt.txt', help='Path to save the optimized prompt')
@click.option('--metrics-output', '-m', default='results/optimization_metrics.json', help='Path to save the optimization metrics')
def optimize_prompt(sample_image, ground_truth, iterations, output, metrics_output):
    """Optimize the prompt for better checkbox extraction."""
    logger.info(f"Optimizing prompt for checkbox extraction")
    
    # Check if the files exist
    if not os.path.exists(sample_image):
        logger.error(f"Sample image '{sample_image}' not found")
        sys.exit(1)
    
    if not os.path.exists(ground_truth):
        logger.error(f"Ground truth file '{ground_truth}' not found")
        sys.exit(1)
    
    # Initialize the prompt optimizer
    optimizer = PromptOptimizer()
    
    # Optimize the prompt
    optimized_prompt, final_metrics = optimizer.optimize_prompt(
        sample_image, ground_truth, iterations
    )
    
    # Save the optimized prompt
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, 'w') as f:
        f.write(optimized_prompt)
    
    logger.info(f"Optimized prompt saved to {output}")
    
    # Save the final metrics
    os.makedirs(os.path.dirname(metrics_output), exist_ok=True)
    with open(metrics_output, 'w') as f:
        json.dump(final_metrics, f, indent=2)
    
    logger.info(f"Final metrics saved to {metrics_output}")
    
    # Plot the final metrics
    from backend.utils.visualization import plot_metrics
    plot_metrics(final_metrics)
    
    # Check if the performance meets the requirements
    precision_requirement = float(os.getenv('MIN_PRECISION', 0.97))
    recall_requirement = float(os.getenv('MIN_RECALL', 0.90))
    
    if final_metrics["precision"] >= precision_requirement and final_metrics["recall"] >= recall_requirement:
        logger.info("\n✅ Optimized prompt meets the requirements!")
        logger.info(f"Required Precision: ≥{precision_requirement:.0%}, Achieved: {final_metrics['precision']:.2%}")
        logger.info(f"Required Recall: ≥{recall_requirement:.0%}, Achieved: {final_metrics['recall']:.2%}")
    else:
        logger.info("\n❌ Optimized prompt does not meet the requirements.")
        if final_metrics["precision"] < precision_requirement:
            logger.info(f"Required Precision: ≥{precision_requirement:.0%}, Achieved: {final_metrics['precision']:.2%}")
        if final_metrics["recall"] < recall_requirement:
            logger.info(f"Required Recall: ≥{recall_requirement:.0%}, Achieved: {final_metrics['recall']:.2%}")

if __name__ == "__main__":
    cli() 