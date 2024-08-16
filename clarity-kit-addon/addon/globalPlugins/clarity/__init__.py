import sys
import os
import globalPluginHandler
from scriptHandler import script
import ui
import api
import json
import requests
import threading
import tones
import time
import io

from .utils import in_order, obj_dump, dummy_data, Node, json_to_tree, similarity_score, click_on_element

# trick to import from local /deps 
curr_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(curr_dir)
deps_dir = os.path.join(parent_dir, 'deps')
sys.path.insert(0, deps_dir)
# end trick

from mss import mss, tools
import pytesseract
from PIL import Image
import numpy as np
import cv2

# TODO delete path entry
pytesseract.pytesseract.tesseract_cmd = os.path.join(deps_dir, 'tesseract', 'tesseract.exe')

# backend_url = 'http://clarity.newrollenterprises.com/processScreen'
backend_url = 'http://localhost:8001/processScreen'

def loading_tone(stop_event):
  while not stop_event.is_set():
      tones.beep(640, 100)
      time.sleep(1)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    # class variables
    root = None # root of screen element tree, set later
    current = None # current element
    detection = None # for storing OCR results
    z_pressed_once = True # press twice to kick off another screen 

    @script(gestures=["kb:NVDA+z","kb:NVDA+upArrow","kb:NVDA+downArrow","kb:NVDA+leftArrow","kb:NVDA+rightArrow","kb:NVDA+enter"])
    def script_clarity(self, gesture):

        # api.copyToClip(obj_dump(sys.path))

        main_key_name = gesture._get_mainKeyName()

        if main_key_name == 'z':

            if GlobalPlugin.z_pressed_once: # kick off another screen

                # reset for next time
                GlobalPlugin.z_pressed_once = False

                ui.message('Clarity Kit processing.')

                # loading indicator
                stop_event = threading.Event()
                loading_task = threading.Thread(target=loading_tone, args=(stop_event,))
                loading_task.start()

                # take screenshot
                with mss() as sct:
                  screenshot = sct.grab(sct.monitors[1])
                  img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
                  img_np = np.array(img)

                # Convert image to RGB (if not already)
                # TODO black and white to improve OCR and claude
                img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
                
                # # Perform OCR on the image
                # # TODO look for segment only mode, so no work wasted
                # custom_config = r'--oem 3 --psm 6'  # OEM 3: Default, PSM 6: Assume a single uniform block of text
                # # TODO read man page and change custom_config to better params
                # detection = pytesseract.image_to_data(img_rgb, config=custom_config, output_type=pytesseract.Output.DICT)
                # GlobalPlugin.detection = detection # store globally
                # # boxes = pytesseract.image_to_boxes(img_rgb, config=custom_config)
                
                # # Draw bounding boxes and labels
                # for i in range(len(detection['level'])):
                #     x, y, w, h = detection['left'][i], detection['top'][i], detection['width'][i], detection['height'][i]
                #     # cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (0, 0, 255), 2)
                #     cv2.putText(img_rgb, f"({i})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # # Resize the image to fit within a window, maintaining aspect ratio
                # max_height = 800
                # max_width = 1200

                # height, width = img_rgb.shape[:2]
                # scaling_factor = min(max_width / width, max_height / height)

                # new_size = (int(width * scaling_factor), int(height * scaling_factor))
                # resized_image = cv2.resize(img_rgb, new_size, interpolation=cv2.INTER_AREA)

                # # Display the resized image with bounding boxes
                # cv2.imshow('Image with Text Bounding Boxes', resized_image)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()               
                
                # Send the bytes to the backend endpoint
                success, img_bytes = cv2.imencode('.png', img_rgb)
                response = requests.post(backend_url, files={'image': ('image.png', img_bytes, 'image/png')})

                # stop loading indicator
                stop_event.set()
                loading_task.join()

                # Print the response from the backend
                # print(f'Status Code: {response.status_code}')
                # TODO robust to errors
                if response.status_code == 200:
                    pass
                    # print('Response:', response.json())
                elif response.status_code == 529:
                    GlobalPlugin.z_pressed_once = True
                    print(response.text)
                    print(response.status_code)
                    ui.message('Overloaded. Please wait a moment and try again.')
                    return
                else:
                    # print('Error:', response.text)
                    GlobalPlugin.z_pressed_once = True
                    print(response.text)
                    print(response.status_code)
                    ui.message('An error occurred. Please try again')
                    return
                              
                GlobalPlugin.root = json_to_tree(response.json())
                GlobalPlugin.current = GlobalPlugin.root

                ui.message(GlobalPlugin.root.name)
                if len(GlobalPlugin.root.children) == 1:
                    ui.message('1 child.') 
                else:
                    ui.message(f"{len(GlobalPlugin.root.children)} children.")
                ui.message(GlobalPlugin.root.description)
            
            else: # first time z was pressed

                ui.message('Current element')

                # if GlobalPlugin.current.box_idx: ui.message('Clickable')

                ui.message(GlobalPlugin.current.name)
                if len(GlobalPlugin.current.children) == 1:
                    ui.message('1 child.') 
                else:
                    ui.message(f"{len(GlobalPlugin.current.children)} children.")
                ui.message(GlobalPlugin.current.description)
                if GlobalPlugin.current.textContent: ui.message(GlobalPlugin.current.textContent)
                
                GlobalPlugin.z_pressed_once = True
                ui.message('Repeat that command to process a new screen')

            return # end handling of z

        if GlobalPlugin.root is None:
            ui.message('You must first process the screen.')
        else:

            GlobalPlugin.z_pressed_once = False

            if main_key_name == 'upArrow':
                if GlobalPlugin.current.previous is None:
                    ui.message('No previous sibling')
                    return
                else:
                    GlobalPlugin.current = GlobalPlugin.current.previous

            if main_key_name == 'downArrow':
                if GlobalPlugin.current.next is None:   
                    ui.message('No next sibling')
                    return
                else:
                    GlobalPlugin.current = GlobalPlugin.current.next

            if main_key_name == 'rightArrow':
                if len(GlobalPlugin.current.children) == 0:
                    ui.message('No children')
                    return
                else:
                    ui.message('First child')
                    GlobalPlugin.current = GlobalPlugin.current.children[0]

            if main_key_name == 'leftArrow':
                if GlobalPlugin.current.parent is None:
                    ui.message('No parent')
                    return
                else:
                    ui.message('Parent')
                    GlobalPlugin.current = GlobalPlugin.current.parent

            if main_key_name == 'enter':
                if GlobalPlugin.current.box_idx != "":

                    ui.message('Click')

                    # box_idx = GlobalPlugin.current.box_idx 

                    # top = GlobalPlugin.detection['top'][box_idx]
                    # left = GlobalPlugin.detection['left'][box_idx]
                    # height = GlobalPlugin.detection['height'][box_idx]
                    # width = GlobalPlugin.detection['width'][box_idx]

                    # click_on_element(top, left, height, width)
                    ui.message(GlobalPlugin.current.box_idx)
                
                else:

                    ui.message('Not clickable')
                  
                return

            # if GlobalPlugin.current.box_idx: ui.message('Clickable')

            ui.message(GlobalPlugin.current.name)
            if len(GlobalPlugin.current.children) == 0:
                pass 
            elif len(GlobalPlugin.current.children) == 1:
                ui.message('1 child.') 
            else:
                ui.message(f"{len(GlobalPlugin.current.children)} children.")
            ui.message(GlobalPlugin.current.description)
            if GlobalPlugin.current.textContent: ui.message(GlobalPlugin.current.textContent)