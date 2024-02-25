import cv2
import numpy as np
import pytesseract
import csv
from pdf2image import convert_from_path

def extract_table_from_image(image_path, output_csv):
    """
    Extract tables from an image and save the extracted data to a CSV file.

    Parameters:
    - image_path (str): The path to the input image file.
    - output_csv (str): The path to save the output CSV file.
    """
    # Define unwanted characters to be removed during text extraction
    unwanted_chars = ['|', '[', ']', '`', '~', ')', '(', '%']

    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Crop the image to remove the border
    w, h, _ = image.shape
    image = image[5:w-5, 5:h-5]

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to segment text
    _, thresh = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extract the largest contour (assuming it's the table region)
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Crop the table region
    table_region = image[y:y+h, x:x+w]

    # Perform OCR on the table region
    ocr_text = pytesseract.image_to_string(table_region, config=r'-c preserve_interword_spaces=1')

    # Remove unwanted characters from the OCR text
    for char in unwanted_chars:
        ocr_text = ocr_text.replace(char, " ")

    # Split the OCR text into lines
    lines = ocr_text.split('\n')

    # Identify rows and columns
    table = []
    for line in lines:
        # Split line into cells using regular expression
        cells = [cell.strip() for cell in line.split('  ') if cell.strip()]

        # Append non-empty cells
        if len(cells) > 1:
            table.append(cells)

    # Write to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(table)

    print(f"Table extracted and saved as {output_csv}")

if __name__ == "__main__":
    # Output CSV file
    output_csv = 'output0.csv'
    image_path = "style-zebra.png"

    # Extract tables from the image
    extract_table_from_image(image_path, output_csv)
