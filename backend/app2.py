from flask import Flask, request, jsonify
import requests
import base64
import app_secrets

app = Flask(__name__)

API_KEY = app_secrets.openai_api_key

@app.route('/processScreen', methods=['POST'])
def process_screen():

    # for debugging only, bypasses claude API
    # return "debugging", 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    image_media_type = image_file.content_type

    response = send_to_claude(image_base64, image_media_type)

    if response.status_code == 200:
        response_json = response.json()
        
        print(response_json)

        # extract json of interest
        addon_json = response_json['choices'][0]['message']['content']

        # TODO verify that this JSON won't break my frontend
        print(addon_json)

        return jsonify(addon_json)
    else:
        # TODO obfuscate status code, use generic instead of Claude
        return jsonify({'error': 'Failed to process image'}), response.status_code

def send_to_claude(image_base64, image_media_type):
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
    "model": "gpt-4o",
    "response_format": {"type": "json_object"},
    "temperature": 0,
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Breakdown this page into react-style components. First, find the nearest red number in parentheses ABOVE THE COMPONENT so you can mark down its location on the page. Looking to the sides wll give you an INCORRECT LOCATION. This will be the positionMarker. Then give it a name like it is a react component. Then give it a short description. Then extract whatever text it has into textContent. Return all the components using a nested JSON tree structure. Each object has the following 5 attributes: positionMarker (integer), name (str), description (str), textContent (str), children. The root object is named \"Page\". MAKE SURE YOU INCLUDE ONE COMPONENT FOR EVERY INTERACTABLE / CLICKABLE ELEMENT. IT IS OF DIRE IMPORTANCE THAT YOU GET THIS PART RIGHT. Just return the JSON, no other words or text."
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_base64}",
                "detail": "high"
            }
            }
        ]
        }
    ],
    "max_tokens": 4096 
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8001)
