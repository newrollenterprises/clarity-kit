from flask import Flask, request, jsonify
import requests
import base64
import app_secrets

app = Flask(__name__)

ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages'
ANTHROPIC_API_KEY = app_secrets.api_key

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

        # extract json of interest
        addon_json = response_json['content'][0]['text']

        # TODO verify that this JSON won't break my frontend
        print(response_json)
        print(addon_json)

        return jsonify(addon_json)
    else:
        # TODO obfuscate status code, use generic instead of Claude
        return jsonify({'error': 'Failed to process image'}), response.status_code

def send_to_claude(image_base64, image_media_type):
    headers = {
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    }

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_media_type,
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": "Breakdown this page into react-style components. First, find the nearest red number in parentheses ABOVE THE COMPONENT so you can mark down its location on the page. Looking to the sides wll give you an INCORRECT LOCATION. This will be the positionMarker. Then give it a name like it is a react component. Then give it a short description. Then extract whatever text it has into textContent. Return all the components using a nested JSON tree structure. Each object has the following 5 attributes: positionMarker (integer), name (str), description (str), textContent (str), children. The root object is named \"Page\". MAKE SURE YOU INCLUDE ONE COMPONENT FOR EVERY INTERACTABLE / CLICKABLE ELEMENT. IT IS OF DIRE IMPORTANCE THAT YOU GET THIS PART RIGHT. Just return the JSON, no other words or text."
                    }
                ]
            }
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)

    return response

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8001)