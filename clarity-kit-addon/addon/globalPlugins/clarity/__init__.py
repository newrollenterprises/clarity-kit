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

# TODO delete path entry
pytesseract.pytesseract.tesseract_cmd = os.path.join(deps_dir, 'tesseract', 'tesseract.exe')

backend_url = 'http://localhost:5000/processScreen'

def loading_tone(stop_event):
  while not stop_event.is_set():
      tones.beep(640, 100)
      time.sleep(1)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    # class variables
    root = None # root of screen element tree, set later
    current = None # current element
    detection = None # stores OCR results
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
                # TODO black and white to improve OCR and claude
                with mss() as sct:
                  img = sct.grab(sct.monitors[1])
                img_bytes = tools.to_png(img.rgb, img.size)

                # Send the bytes to the backend endpoint
                response = requests.post(backend_url, files={'image': ('image.png', img_bytes, 'image/png')})

                # stop loading indicator
                stop_event.set()
                loading_task.join()

                # run text OCR
                img_bytes_obj = io.BytesIO(img_bytes)
                pillow_img = Image.open(img_bytes_obj)
                # TODO read man page and change custom_config to better params
                custom_config = r'--oem 3 --psm 3'  # OEM 3: Default, PSM 6: Assume a single uniform block of text
                GlobalPlugin.detection = pytesseract.image_to_data(pillow_img, config=custom_config, output_type=pytesseract.Output.DICT)

                # TODO package tesseract into /deps and specify it

                # Print the response from the backend
                print(f'Status Code: {response.status_code}')
                # TODO robust to errors
                if response.status_code == 200:
                    print('Response:', response.json())
                else:
                    print('Error:', response.text)
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
                ui.message(GlobalPlugin.current.name)
                if len(GlobalPlugin.current.children) == 1:
                    ui.message('1 child.') 
                else:
                    ui.message(f"{len(GlobalPlugin.current.children)} children.")
                ui.message(GlobalPlugin.current.description)
                
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
                ui.message('Click')
                
                # create clusters from OCR
                clusters = []
                for i in range(2, len(GlobalPlugin.detection['level'])):
                    clusters.append(
                        {
                            'text': GlobalPlugin.detection['text'][i-2] + ' ' + GlobalPlugin.detection['text'][i-1] + ' ' + GlobalPlugin.detection['text'][i],
                            'idxs': [i-2, i-1, i]
                        }
                    )

                elem_text = GlobalPlugin.current.textContent.lower()

                best_match_idx_list = None
                best_score = 0

                for cluster in clusters:
                  cluster_text = cluster['text'].lower()
                  curr_score = similarity_score(elem_text, cluster_text) 
                  if curr_score > best_score:
                      best_score = curr_score
                      best_match_idx_list = cluster['idxs'] 

                print('Best cluster match')
                print(' '.join([GlobalPlugin.detection['text'][x] for x in best_match_idx_list]))

                # now search cluster to find box to click
                best_match_idx = None
                best_score = 0

                for idx in best_match_idx_list:
                    curr_text = GlobalPlugin.detection['text'][idx]
                    curr_score = similarity_score(elem_text, curr_text)
                    if curr_score > best_score:
                        best_score = curr_score
                        best_match_idx = idx

                print('Best match within cluster')
                print(GlobalPlugin.detection['text'][best_match_idx])

                # TODO click item
                top = GlobalPlugin.detection['top'][best_match_idx]
                left = GlobalPlugin.detection['left'][best_match_idx]
                height = GlobalPlugin.detection['height'][best_match_idx]
                width = GlobalPlugin.detection['width'][best_match_idx]
                click_on_element(top, left, height, width)
                  
                return

            ui.message(GlobalPlugin.current.name)
            if len(GlobalPlugin.current.children) == 0:
                pass 
            elif len(GlobalPlugin.current.children) == 1:
                ui.message('1 child.') 
            else:
                ui.message(f"{len(GlobalPlugin.current.children)} children.")
            ui.message(GlobalPlugin.current.description)