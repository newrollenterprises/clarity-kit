import globalPluginHandler
from scriptHandler import script
import ui
import api
import json
from .mss import mss, tools
import requests
import threading
import tones
import time

backend_url = 'http://localhost:5000/processScreen'

def in_order(node):
    context = [] # empty list we will populate

    def _in_order(node):
        context.append(node)
        for child in node.children:
            _in_order(child)

    _in_order(node)

    return context

def obj_dump(obj):
    dump_str = ""
    attributes_methods = dir(obj)
    entries = []
    print("Attributes and Methods and their values:")
    # Iterate over the list of attributes and methods
    for attr in attributes_methods:
        # Skip methods and private attributes
        # if not attr.startswith('_') and not callable(getattr(obj, attr)):
            # pass
        try:
            value = getattr(obj, attr) 
        except:
            value = 'ERROR'
        entries.append((attr, value))
    dump_str += str(entries)
    return dump_str
  
dummy_data = """
{
  "name": "Page",
  "description": "Main container for the entire Dollar Tree website",
  "children": [
    {
      "name": "Header",
      "description": "Contains top navigation and main site controls",
      "children": [
        {
          "name": "TopBar",
          "description": "Upper bar with store and order options",
          "children": [
            {
              "name": "LocationSelector",
              "description": "Option to set or choose a store location",
              "children": []
            },
            {
              "name": "CatalogQuickOrder",
              "description": "Quick access to catalog ordering",
              "children": []
            },
            {
              "name": "PhoneOrder",
              "description": "Phone number for placing orders",
              "children": []
            },
            {
              "name": "SameDayDelivery",
              "description": "Information about same-day delivery service",
              "children": []
            },
            {
              "name": "TrackOrders",
              "description": "Link to track existing orders",
              "children": []
            },
            {
              "name": "ShopFamilyDollar",
              "description": "Link to Family Dollar store",
              "children": []
            }
          ]
        },
        {
          "name": "MainHeader",
          "description": "Primary header with logo, search, and account functions",
          "children": [
            {
              "name": "Logo",
              "description": "Dollar Tree company logo",
              "children": []
            },
            {
              "name": "SearchBar",
              "description": "Search input field for the website",
              "children": []
            },
            {
              "name": "MoreChoices",
              "description": "Additional options or menu",
              "children": []
            },
            {
              "name": "Account",
              "description": "User account access",
              "children": []
            },
            {
              "name": "Cart",
              "description": "Shopping cart icon and access",
              "children": []
            }
          ]
        },
        {
          "name": "NavigationMenu",
          "description": "Main navigation menu for product categories",
          "children": [
            {
              "name": "AllDepartments",
              "description": "Dropdown for all store departments",
              "children": []
            },
            {
              "name": "CategoryLinks",
              "description": "Direct links to main product categories",
              "children": []
            }
          ]
        }
      ]
    },
    {
      "name": "Main",
      "description": "Main content area of the homepage",
      "children": [
        {
          "name": "AppDownloadBanner",
          "description": "Promotional banner for new mobile app download",
          "children": []
        },
        {
          "name": "BackToSchoolPromo",
          "description": "Featured promotion for back-to-school products",
          "children": [
            {
              "name": "PromoImage",
              "description": "Image showcasing back-to-school items",
              "children": []
            },
            {
              "name": "PromoText",
              "description": "Text promoting 'Return to Learn for Less' campaign",
              "children": []
            }
          ]
        }
      ]
    },
    {
      "name": "Footer",
      "description": "Page footer area",
      "children": [
        {
          "name": "TrustedSite",
          "description": "TrustedSite security certification seal",
          "children": []
        }
      ]
    }
  ]
}
"""

class Node:
    def __init__(self, name, description):
        self._name = name
        self._description = description
        self._children = []
        self._parent = None
        self._next = None
        self._previous = None

    # Getter and setter for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    # Getter and setter for description
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    # Getter for children
    @property
    def children(self):
        return self._children

    # Getter and setter for parent
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    # Getter and setter for next
    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        self._next = value

    # Getter and setter for previous
    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value):
        self._previous = value

    # No setter for children; use a method to add children
    def add_child(self, child):
        if isinstance(child, Node):
            if self._children:
                self._children[-1].next = child
                child.previous = self._children[-1]
            child.parent = self
            self._children.append(child)
        else:
            raise ValueError("Child must be an instance of Node")

    def __repr__(self):
        return f"Node(name={self.name}, description={self.description}, children={len(self.children)})"

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "children": [child.to_dict() for child in self.children]
        }


def json_to_tree(data):
    if isinstance(data, str):
        data = json.loads(data)

    def create_node(node_data):
        node = Node(node_data['name'], node_data['description'])
        for child_data in node_data.get('children', []):
            node.add_child(create_node(child_data))
        return node

    return create_node(data)

def loading_tone(stop_event):
  while not stop_event.is_set():
      tones.beep(640, 100)
      time.sleep(1)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    # class variables
    root = None # root of screen element tree, set later
    current = None # current element
    z_pressed_once = True # press twice to kick off another screen 

    @script(gestures=["kb:NVDA+z","kb:NVDA+upArrow","kb:NVDA+downArrow","kb:NVDA+leftArrow","kb:NVDA+rightArrow"])
    def script_clarity(self, gesture):

        api.copyToClip(obj_dump(gesture))

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
                  img = sct.grab(sct.monitors[1])
                img_bytes = tools.to_png(img.rgb, img.size)

                # Send the bytes to the backend endpoint
                response = requests.post(backend_url, files={'image': ('image.png', img_bytes, 'image/png')})

                # stop loading indicator
                stop_event.set()
                loading_task.join()

                # Print the response from the backend
                print(f'Status Code: {response.status_code}')
                if response.status_code == 200:
                    print('Response:', response.json())
                else:
                    print('Error:', response.text)
                              
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

            return


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