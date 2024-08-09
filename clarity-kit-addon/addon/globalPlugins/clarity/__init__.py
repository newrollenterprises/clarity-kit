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

from .utils import in_order, obj_dump, dummy_data, Node, json_to_tree

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

backend_url = 'http://localhost:5000/processScreen'

def loading_tone(stop_event):
  while not stop_event.is_set():
      tones.beep(640, 100)
      time.sleep(1)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    # class variables
    root = None # root of screen element tree, set later
    current = None # current element
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
                custom_config = r'--oem 3 --psm 6'  # OEM 3: Default, PSM 6: Assume a single uniform block of text
                detection = pytesseract.image_to_data(pillow_img, config=custom_config, output_type=pytesseract.Output.DICT)
                # print(detection)

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
                return

            ui.message(GlobalPlugin.current.name)
            if len(GlobalPlugin.current.children) == 0:
                pass 
            elif len(GlobalPlugin.current.children) == 1:
                ui.message('1 child.') 
            else:
                ui.message(f"{len(GlobalPlugin.current.children)} children.")
            ui.message(GlobalPlugin.current.description)
            






    # @script(gesture="kb:NVDA+shift+v")
    # def script_announceNVDAVersion(self, gesture):
    #     obj = api.getNavigatorObject()

        
    #     # accumulate a number of nearby objects
    #     # context_thresh = 10 # number of objects for context
    #     # context.append(obj)
    #     # while len(context) < context_thresh:

    #     # # find root html element (not NVDA obj)
    #     # root = obj
    #     # while True:
    #     #     if not root.parent: # should never happen
    #     #         ui.message('Failed')
    #     #     root = root.parent
    #     #     if root.IA2Attributes:
    #     #         if 'tag' in root.IA2Attributes:
    #     #             if root.IA2Attributes['tag'] == 'body': break

    #     root = obj.parent.parent

    #     context = in_order(root) # in-order list of objs
        
    #     to_clip = ""
    #     for x in context:
    #         # if x.IA2Attributes: to_clip += "OBJECT" + obj_dump(x)
    #         # if x.IA2Attributes: to_clip += "OBJECT" + str(x.IA2Attributes)
    #         to_clip += " " + x.basicText
    #         # to_clip += "VALUE" + x.value
    #         # to_clip += "CHILDREN" + str(len(x.children))
    #     ui.message('Clarity: ')
    #     api.copyToClip(to_clip)

    #     # ui.message(obj.previous.name)
    #     # ui.message(obj.name)
    #     # ui.message(obj.next.name)
    #     if obj.HTMLNode:
    #         ui.message(obj.HTMLNode.text)