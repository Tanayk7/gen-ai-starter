import os 
import requests 
import json 
from utils.image import cv2_to_b64 
from dotenv import load_dotenv

load_dotenv()

def group_words_by_lines(words):
    lines = {}

    # Group words by y-coordinate
    for word in words:
        if not 'y' in word['boundingPoly']['vertices'][0]: 
            continue 
    
        if not 'x' in word['boundingPoly']['vertices'][0]: 
            continue
        
        y = word['boundingPoly']['vertices'][0]['y']

        if any(abs(y - line_y) <= 6 for line_y in lines):
            # Find the closest line
            closest_line_y = min(lines.keys(), key=lambda line_y: abs(y - line_y))
            lines[closest_line_y].append(word)
        else:
            lines[y] = [word]

    # Sort words within each line by x-coordinate
    for line in lines.values():
        line.sort(key=lambda word: word['boundingPoly']['vertices'][0]['x'])

    # Generate list of lines
    grouped_lines = [' '.join([word['description'] for word in line]) for line in lines.values()]

    return grouped_lines

def batch_text_detection(images, concat_by=" "):
    api_key = os.getenv("GOOGLE_API_KEY")
    endpoint = os.getenv('GOOGLE_CLOUD_VISION_ENDPOINT')

    # Create a list to store the image request objects
    image_requests = []

    # Process each image
    for image in images:
        # Convert the image to base64 encoding
        image_content = cv2_to_b64(image)
        # Create an image request object
        image_request = {
            "image": {
                "content": image_content
            },
            "features": [
                {
                    "type": "TEXT_DETECTION"
                }
            ]
        }
        # Add the image request object to the list
        image_requests.append(image_request)

    # Prepare the batch request payload
    payload = {
        "requests": image_requests
    }

    # Send the batch request to the Vision API
    params = {'key': api_key}
    response = requests.post(endpoint, params=params, json=payload)
    response_data = json.loads(response.text)
    # logging.info(f"Response from ocr: {response_data}")

    # Process the batch response and extract the detected text for each image
    lines_concat = []

    if 'responses' in response_data:
        for image_response in response_data['responses']:
            annotations = image_response.get('textAnnotations', [])
            lines = group_words_by_lines(annotations[1:])
            lines_concat.append(concat_by.join(lines))

    concatenated_text = ' '.join(lines_concat)
    # print("Generated lines: ", concatenated_text, '\n') 

    return concatenated_text