import cv2
import base64
import requests
import numpy as np

from io import BytesIO

def encode_image_b64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def url_to_cv2_image(url):
    response = requests.get(url)
    # logging.info(f"image response: {response}")
    image_bytes = BytesIO(response.content)
    image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
    return image

def url_to_b64(url): 
    cv2_image = url_to_cv2_image(url)
    b64_img = cv2_to_b64(cv2_image)
    return b64_img

def cv2_to_b64(cv2_image): 
    # Encode the image as a JPEG in memory
    ret, buffer = cv2.imencode('.jpg', cv2_image)
    # Convert the encoded image to a base64 string
    b64_img = base64.b64encode(buffer).decode('utf-8')
    return b64_img

def base64_to_cv2_img(base64_string):
    # Decode the base64 string to bytes
    img_data = base64.b64decode(base64_string)
    # Convert the bytes data to a numpy array
    nparr = np.frombuffer(img_data, np.uint8)
    # Decode the numpy array to a CV2 image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img