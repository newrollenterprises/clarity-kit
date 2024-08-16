from flask import Flask, request, jsonify
import requests
import base64
import app_secrets
from xml_to_json_tree import react_xml_to_json

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
        addon_xml= response_json['content'][0]['text']

        # TODO verify that this JSON won't break my frontend
        print(response_json)
        print(addon_xml)

        addon_json = react_xml_to_json(addon_xml)
        
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
                        "text": "Breakdown this webpage into high-level XML components react-style. Every component should have all 4 attributes! Name each component based off what it does. If the component is outlined in red, give it a \"tagText\" attribute which contains the letters found in the yellow tag near the top of that component. If the component is not outlined in red set \"tagText\" = \"\" (the default value). Give every single component a brief \"description\" attribute of what it is/does. Extract the components text into a \"textContent\" attribute. The root component is <WebPage>. Respond only with the XML. No other words or text."
                    }
                ]
            }
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)

    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8001)