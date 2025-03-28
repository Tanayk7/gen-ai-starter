import os 
import traceback
import ollama
import numpy as np

from openai import OpenAI
from dotenv import load_dotenv
from utils.image import encode_image_b64, cv2_to_b64, url_to_b64
from dotenv import load_dotenv
from json_repair import repair_json

load_dotenv()

openai_client = OpenAI(
  organization=os.getenv('OPENAI_ORG_ID'),
  api_key=os.getenv('OPENAI_API_KEY'),
  max_retries=int(os.getenv('LLM_MAX_RETRIES', 3))
)

def generate_image(caption: str, size: str = "1024x1024", quality="standard", n=1):
    response = openai_client.images.generate(
        model=os.getenv('OPENAI_IMAGE_MODEL', 'dall-e-3'),
        prompt=caption,
        size=size,
        quality=quality,
        n=n,
    )
    image_url = response.data[0].url
    return image_url

def get_openai_embedding(text):
    text = text.replace("\n", " ")
    embedding = openai_client.embeddings.create(
        input = [text], 
        model=os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
    ).data[0].embedding
    return np.array(embedding)

'''
    Can handle either image urls, image paths or a cv2 image directly. Pass value in appropriate arguments 
    prompt = <str_value>
    system_msg = <str_value>
    cv2_image = <opencv_image> 
    image_path = <str_value>
'''
def process_gpt(prompt: str, system_msg: str, response_format: str = "json_object", cv2_images=None, image_paths=None, urls=None, model=None):
    total_cost = 0
    cost_per_1000_tokens = 0.03  # Example cost, adjust based on your pricing
    cost_per_image = 0.05  # Example image processing cost, adjust as needed
    images_b64 = None
    model = model if model != None else os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    user_message_content = [
        {
            "type": "text", 
            "text": prompt
        }
    ]
    
    if image_paths != None: 
        images_b64 = list(map(lambda image_path: encode_image_b64(image_path), image_paths))
    elif cv2_images != None: 
        images_b64 = list(map(lambda cv2_image: cv2_to_b64(cv2_image), cv2_images))
    elif urls != None: 
        images_b64 = list(map(lambda url: url_to_b64(url), urls))
    
    if images_b64 != None: 
        for image_b64 in images_b64: 
            user_message_content.append({
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/png;base64,{image_b64}"
                }
            }) 

    try:
        # print(f"sending request to {model}...")
        completion = openai_client.chat.completions.create(
            model=model,
            max_tokens=4096,
            temperature=0,
            messages=[
                { "role": "system", "content": system_msg },
                { "role": "user", "content": user_message_content },
            ],
            response_format={ "type": response_format }
        )
        # print(f"request to {model} complete!")

        text_output = completion.choices[0].message.content
        # completion_tokens = completion.usage.completion_tokens
        # prompt_tokens = completion.usage.prompt_tokens
        total_tokens = completion.usage.total_tokens
        cost_for_this_call = (total_tokens / 1000) * cost_per_1000_tokens + cost_per_image
        total_cost += cost_for_this_call
        # print(f"Cost for generating caption for {image_path}: ${cost_for_this_call:.5f}")
        return (text_output, total_tokens, total_cost)
    
    except Exception as e:
        print(f"Something went wrong while trying to get a response from the OpenAI API: {e}")
        traceback.print_exc()
        return None

def process_ollama(user_prompt, system_prompt, image_path): 
    res = ollama.chat(
        model="llava",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                'role': 'user',
                'content': user_prompt,
                'images': [image_path]
            }
        ]
    )
    print(f"Request to llava for image: {image_path} complete!")
    text_output = res['message']['content']
    return text_output, image_path