import cv2
import pytesseract
import os

# Specify the path to the local Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Path to the image file
image_path = 'brainstorm/dollartree.jpg'

# Read the image using OpenCV
image = cv2.imread(image_path)

# Convert the image to grayscale (optional, but often improves OCR results)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Perform OCR on the image
custom_config = r'--oem 3 --psm 3'  # OEM 3: Default, PSM 6: Assume a single uniform block of text
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

# # Display the resized image with bounding boxes
# cv2.imshow('Image with Text Bounding Boxes', resized_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# pairs of words for whole doc
clusters = []
for i in range(2, len(detection['level'])):
    clusters.append(detection['text'][i-2] + ' ' + detection['text'][i-1] + ' ' + detection['text'][i])

print(clusters)


# # clustering vars
# detection['visited'] = [False for x in range(len(detection['level']))]
# detection['rneighbor'] = [None for x in range(len(detection['level']))]
# detection['lneighbor'] = [None for x in range(len(detection['level']))]
# distance_thresh = 50
# clusters = []

# # find neighbors
# for i in range(len(detection['level'])):
#     current_left = detection['left'][i] + detection['width'][i]
#     current_top = detection['top'][i]
#     for j in range(len(detection['level'])):
#         if abs(current_left - detection['left'][j]) < distance_thresh  and abs(current_top - detection['top'][j]) < 10: # found a neighbor
#             detection['rneighbor'][i] = j
#             detection['lneighbor'][j] = i
#             break # only one neighbor

# # cluster neighbors
# for i in range(len(detection['level'])):
#     if not detection['visited'][i]:
#         detection['visited'][i] = True
#         cluster = []
#         cluster.append(i)
#         lneighbor = detection['lneighbor'][i]
#         while lneighbor:
#             if detection['visited'][lneighbor]: break
#             cluster.insert(0, lneighbor)
#             detection['visited'][lneighbor] = True
#             lneighbor = detection['lneighbor'][lneighbor]
#         rneighbor = detection['rneighbor'][i]
#         while rneighbor:
#             if detection['visited'][rneighbor]: break
#             cluster.append(rneighbor)
#             detection['visited'][rneighbor] = True
#             rneighbor = detection['rneighbor'][rneighbor]
#         clusters.append(cluster)

# print(clusters)

# clusters_text = [','.join([detection['text'][x] for x in c]) for c in clusters]
# print(clusters_text)

print('done')
