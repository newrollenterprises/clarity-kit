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

        return jsonify(addon_json)
    else:
        return jsonify({'error': 'Failed to process image'}), response.status_code

def send_to_claude(image_base64, image_media_type):
    headers = {
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    }

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1024,
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
                        "text": "Give me a high-level component-based representation of this image. Make sure you inlcude one component for each link/button. Name each component as if it is a react component. Write a short description for each component. The root component is named \"Page\". Return your answer as a JSON tree of nested objects each with 3 properties: name, description, children. Only reply with the JSON, nothing else. No other words."
                    }
                ]
            }
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)

    return response

if __name__ == '__main__':
    app.run(debug=True)