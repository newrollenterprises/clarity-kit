import json

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