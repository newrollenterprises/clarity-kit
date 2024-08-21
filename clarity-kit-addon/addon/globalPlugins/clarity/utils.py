import json
import sys
import os
import asyncio

# trick to import from local /deps 
curr_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(curr_dir)
deps_dir = os.path.join(parent_dir, 'deps')
sys.path.insert(0, deps_dir)
# end trick

import websockets

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
    # print("Attributes and Methods and their values:")
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
    def __init__(self, name, description, textContent, id):
        self._name = name
        self._description = description
        self._textContent = textContent
        self._children = []
        self._parent = None
        self._next = None
        self._previous = None
        self._box_idx = id 

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

    # Getter and setter for textContent
    @property
    def textContent(self):
        return self._textContent
    
    @textContent.setter
    def textContent(self, value):
        self._textContent = value

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
    
    # Getter and setter for box_idx, maps Claude's node to OCR text element from screen
    @property
    def box_idx(self):
        return self._box_idx

    @box_idx.setter
    def box_idx(self, value):
        self._box_idx = value

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
        id = ""
        if node_data['clickID']: id = node_data['clickID']
        node = Node(node_data['name'], node_data['description'], node_data['textContent'], id)
        for child_data in node_data.get('children', []):
            node.add_child(create_node(child_data))
        return node

    return create_node(data)

def click_on_element(id):

  return