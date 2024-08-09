import cv2
import pytesseract
import os

# Specify the path to the local Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Path to the image file
image_path = 'dollartree.jpg'

# Read the image using OpenCV
image = cv2.imread(image_path)

# Convert the image to grayscale (optional, but often improves OCR results)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Perform OCR on the image
custom_config = r'--oem 3 --psm 6'  # OEM 3: Default, PSM 6: Assume a single uniform block of text
detection = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)

# Store text and location in an array
text_data = []
n_boxes = len(detection['level'])
for i in range(n_boxes):
    text = detection['text'][i]
    if text.strip():  # Only consider non-empty text
        (x, y, w, h) = (detection['left'][i], detection['top'][i], detection['width'][i], detection['height'][i])
        text_data.append({'text': text, 'x': x, 'y': y, 'w': w, 'h': h})

# Print the results
for item in text_data:
    print(f"Text: {item['text']}, Location: (x: {item['x']}, y: {item['y']}, w: {item['w']}, h: {item['h']})")

# Optionally, visualize the bounding boxes on the image
for item in text_data:
    cv2.rectangle(image, (item['x'], item['y']), (item['x'] + item['w'], item['y'] + item['h']), (0, 255, 0), 2)
    cv2.putText(image, item['text'], (item['x'], item['y'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Resize the image to fit within a window, maintaining aspect ratio
max_height = 800
max_width = 1200

height, width = image.shape[:2]
scaling_factor = min(max_width / width, max_height / height)

new_size = (int(width * scaling_factor), int(height * scaling_factor))
resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

# Display the resized image with bounding boxes
cv2.imshow('Image with Text Bounding Boxes', resized_image)
cv2.waitKey(0)
cv2.destroyAllWindows()