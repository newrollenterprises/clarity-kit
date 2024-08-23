import requests
import base64
import datetime
import os
import threading
import json
import time

from flask import Flask, request, jsonify

from xml_to_json_tree import react_xml_to_json
import app_secrets

app = Flask(__name__)

ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages'
ANTHROPIC_API_KEY = app_secrets.api_key

file_lock = threading.Lock()

@app.route('/logger', methods=['POST'])
def logger():
    # Get the JSON data from the request
    data = request.get_json()
    
    # Extract fields from the JSON data
    uuid = data.get('uuid')
    sid = data.get('sid')
    level = data.get('level')
    message = data.get('message')
    timestamp = data.get('timestamp')
    source = data.get('source')
    
    # Validate required fields
    if not all([uuid, sid, level, message, timestamp, source]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Convert epoch timestamp to human-readable format
    timestamp_human_readable = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    millis = int((timestamp % 1) * 1000)
    timestamp_human_readable = f"{timestamp_human_readable}:{millis:03d}"
    sid_human_readable = datetime.datetime.fromtimestamp(sid).strftime('%Y-%m-%d %H_%M_%S')
    
    # Create the directory path if it doesn't exist
    log_dir = os.path.join('logs', uuid)
    os.makedirs(log_dir, exist_ok=True)
    
    # Define the file path
    log_file_path = os.path.join(log_dir, f'{sid_human_readable}.txt')
    
    # Append the log message to the file
    with file_lock:
        with open(log_file_path, 'a') as log_file:
            log_file.write(f'[{timestamp_human_readable}] [{level}] [{source}] {message}\n')
    
    return jsonify({"status": "success"}), 200

@app.route('/processScreen', methods=['POST'])
def process_screen():

    # for debugging only, bypasses claude API
    # return {'error': 'fake error for debugging purposes'}, 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    uuid = request.form.get('uuid')
    sid = request.form.get('sid')

    if not all([uuid, sid]):
        return jsonify({'error': 'Missing parameters'}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    image_media_type = image_file.content_type

    # log screenshot async
    screenshot_log_thread = threading.Thread(
        target=log_screenshot,
        args=(image_file, uuid, sid)
    )
    screenshot_log_thread.start()

    response = send_to_claude(image_base64, image_media_type)

    if response.status_code == 200:
        response_json = response.json()

        # async log response JSON
        remote_resp_log_thread = threading.Thread(
            target = log_remote_response,
            args = (response_json, uuid, sid)
        )
        remote_resp_log_thread.start()
        

        # extract json of interest
        addon_xml = response_json['content'][0]['text']

        # TODO verify that this JSON won't break my frontend
        # print(response_json)
        # print(addon_xml)

        addon_json = react_xml_to_json(addon_xml)
        
        # print(addon_json)

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
                        "text": "Breakdown this webpage into high-level XML components react-style. Make lots and lots of components. Tons. Long XML. Every component should have all 4 attributes! Name each component based off what it does. If the component is outlined in red, give it a \"tagText\" attribute which contains the letters found in the yellow tag below that component. If the component is not outlined in red set \"tagText\" = \"\" (the default value). Give every single component a brief \"description\" attribute of what it is/does. Extract the components text into a \"textContent\" attribute. The root component is <WebPage>. Make lots and lots of components. Tons. Long XML. Respond only with the XML. No other words or text."
                    }
                ]
            }
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)

    return response

def log_screenshot(screenshot, uuid, sid):

    sid_human_readable = datetime.datetime.fromtimestamp(float(sid)).strftime('%Y-%m-%d %H_%M_%S')

    screenshot.seek(0) # some weird bug fix, otherwise image corrupts
    screenshot.save(f"logs/{uuid}/{sid_human_readable}.png")
    return

def log_remote_response(response, uuid, sid):

    timestamp = time.time()
    timestamp_human_readable = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    millis = int((timestamp % 1) * 1000)
    timestamp_human_readable = f"{timestamp_human_readable}:{millis:03d}"
    sid_human_readable = datetime.datetime.fromtimestamp(float(sid)).strftime('%Y-%m-%d %H_%M_%S')

    with file_lock:
        with open(f"logs/{uuid}/{sid_human_readable}.txt", 'a') as f:
            f.write(f'[{timestamp_human_readable}] [INFO] [flask] Remote returned JSON: {json.dumps(response)}\n')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8001)