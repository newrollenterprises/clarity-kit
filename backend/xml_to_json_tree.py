import xml.etree.ElementTree as ET
import json

def xml_to_json(element):
    json_obj = {"name": element.tag}

    # Add attributes
    json_obj.update(element.attrib)

    # manually rename attributes as neccessary
    
    if "tagText" not in json_obj.keys():
        json_obj["tagText"] = ""
    if "tagText" in json_obj.keys():
        json_obj["clickID"] = json_obj["tagText"]
        json_obj.pop("tagText")
    if "description" not in json_obj.keys():
        json_obj["description"] = ""
    if "textContent" not in json_obj.keys():
        json_obj["textContent"] = ""
    if "children" not in json_obj.keys():
        json_obj["children"] = []


    # Add children recursively
    children = []
    for child in element:
        children.append(xml_to_json(child))
    
    if children:
        json_obj["children"] = children

    return json_obj

def react_xml_to_json(xml_string):
    # Parse the XML string
    root = ET.fromstring(xml_string)
    
    # Convert the root element to JSON
    return xml_to_json(root)

# Example usage
xml_string = """
<Component1 attr1="value1" attr2="value2">
    <Component2 attr3="value3" />
    <Component3 attr4="value4">
        <Component4 attr5="value5" />
    </Component3>
</Component1>
"""

if __name__ == "__main__":
    json_tree = react_xml_to_json(xml_string)
    print(json.dumps(json_tree, indent=4))