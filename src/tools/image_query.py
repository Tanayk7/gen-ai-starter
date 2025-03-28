import requests
import openai

# Replace with your Unsplash API Key
UNSPLASH_API_KEY = 'zAoXQH-7BSUSvt_9LlIslQ5nezWPfexbharDIwjuBow'

# Function to fetch images from Unsplash API
def fetch_images_from_unsplash(query, per_page=5):
    url = f"https://api.unsplash.com/search/photos"
    params = {
        'query': query,
        'client_id': UNSPLASH_API_KEY,  # API Key
        'per_page': per_page
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        images = []
        # print("response data: ", data)
        for result in data['results']:
            image_url = result['urls']['regular']  # You can also choose other sizes like 'full', 'small', etc.
            images.append(image_url)

        print("images: ", images)
        return images
    else:
        print(f"Error fetching images: {response.status_code}")
        return []
    

if __name__ == "__main__": 
    fetch_images_from_unsplash("Focus enhancing pills")