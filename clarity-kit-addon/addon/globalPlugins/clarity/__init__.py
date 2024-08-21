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
import asyncio
import logging
import tempfile

from .utils import in_order, obj_dump, dummy_data, Node, json_to_tree, click_on_element

# trick to import from local /deps 
curr_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(curr_dir)
deps_dir = os.path.join(parent_dir, 'deps')
sys.path.insert(0, deps_dir)
# end trick

from mss import mss, tools
import websockets

# TODO delete path entry

# Configure logging
log_str = "" # will hold log data to send to backend
class logger():

    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    level=logging.DEBUG  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL

    def debug(self, message):

        response = requests.post(f"{backend_url}/logger", json={'level': 'DEBUG', 'message':message})


logger.debug("Loading Clarity Kit")

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
    z_pressed_once = True # press twice to kick off another screen 
    server_started = False
    click_id_buffer = None # str that hold elem id

    @script(gestures=["kb:NVDA+z","kb:NVDA+upArrow","kb:NVDA+downArrow","kb:NVDA+leftArrow","kb:NVDA+rightArrow","kb:NVDA+enter"])
    def script_clarity(self, gesture):

        logger.debug(f"Script called with gesture {gesture._get_mainKeyName()}")

        if not GlobalPlugin.server_started:

            GlobalPlugin.server_started = True

            async def handler(websocket, path):
                async for message in websocket:
                    if GlobalPlugin.click_id_buffer is not None:
                        logger.debug(f"WebSocket message received: {message}")
                        # await websocket.send(f"Echo: {message}")
                        await websocket.send(GlobalPlugin.click_id_buffer)
                        GlobalPlugin.click_id_buffer = None # free up buffer

            def start_server():
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Start the WebSocket server
                start_server = websockets.serve(handler, "localhost", 8765)
                loop.run_until_complete(start_server)
                loop.run_forever()

            # Start the WebSocket server in a new thread
            logger.debug("Starting WebSocket server")
            server_thread = threading.Thread(target=start_server)
            server_thread.start()

        # api.copyToClip(obj_dump(sys.path))

        main_key_name = gesture._get_mainKeyName()

        if main_key_name == 'z':

            if GlobalPlugin.z_pressed_once: # kick off another screen

                # reset for next time
                GlobalPlugin.z_pressed_once = False

                ui.message('Clarity Kit processing.')
                logger.debug("Processing a new screen")

                # loading indicator
                logger.debug("Starting loading indicator")
                stop_event = threading.Event()
                loading_task = threading.Thread(target=loading_tone, args=(stop_event,))
                loading_task.start()

                # take screenshot
                logger.debug("Taking screenshot")
                with mss() as sct:
                  img = sct.grab(sct.monitors[1])
                img_bytes = tools.to_png(img.rgb, img.size)

                # Send the bytes to the backend endpoint
                logger.debug("Sending screenshot to backend")
                response = requests.post(backend_url, files={'image': ('image.png', img_bytes, 'image/png')})

                # stop loading indicator
                logger.debug("Stopping loading indicator")
                stop_event.set()
                loading_task.join()

                # Print the response from the backend
                # print(f'Status Code: {response.status_code}')
                # TODO robust to errors
                logger.debug(f"Response code {response.status_code}")
                logger.debug(f"Response JSON: {response.json()}")

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
                              
                logger.debug("Converting JSON to tree")
                GlobalPlugin.root = json_to_tree(response.json())
                GlobalPlugin.current = GlobalPlugin.root

                logger.debug("Announcing root")
                ui.message(GlobalPlugin.root.name)
                if len(GlobalPlugin.root.children) == 1:
                    ui.message('1 child.') 
                else:
                    ui.message(f"{len(GlobalPlugin.root.children)} children.")
                ui.message(GlobalPlugin.root.description)
            
            else: # first time z was pressed

                logger.debug(f"Announcing current element: {GlobalPlugin.current.name}")
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
            logger.debug("User tried to navigate an unprocessed screen")
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

                    if GlobalPlugin.click_id_buffer is None: 
                        logger.debug(f"Attempting to click {GlobalPlugin.current.name} with ID {GlobalPlugin.click_id_buffer}")
                        GlobalPlugin.click_id_buffer = GlobalPlugin.current.box_idx

                    ui.message(GlobalPlugin.current.box_idx)
                
                else:

                    ui.message('Not clickable')
                    logger.debug(f"Element {GlobalPlugin.current.name} not clickable")
                  
                return

            # if GlobalPlugin.current.box_idx: ui.message('Clickable')

            ui.message(GlobalPlugin.current.name)
            logger.debug(f"Announcing element {GlobalPlugin.current.name}")
            if len(GlobalPlugin.current.children) == 0:
                pass 
            elif len(GlobalPlugin.current.children) == 1:
                ui.message('1 child.') 
            else:
                ui.message(f"{len(GlobalPlugin.current.children)} children.")
            ui.message(GlobalPlugin.current.description)
            if GlobalPlugin.current.textContent: ui.message(GlobalPlugin.current.textContent)