import cv2
import json

# Load the image
image_path = 'dollartree.jpg'
image = cv2.imread(image_path)

# JSON data
data = [
    {"component": "Page", "topLeft": [0, 0], "bottomRight": [1920, 1080]},
    {"component": "Header", "topLeft": [0, 0], "bottomRight": [1920, 200]},
    {"component": "TopBar", "topLeft": [0, 0], "bottomRight": [1920, 40]},
    {"component": "LocationSelector", "topLeft": [10, 5], "bottomRight": [150, 35]},
    {"component": "CatalogQuickOrder", "topLeft": [160, 5], "bottomRight": [320, 35]},
    {"component": "PhoneOrder", "topLeft": [330, 5], "bottomRight": [540, 35]},
    {"component": "SameDayDelivery", "topLeft": [550, 5], "bottomRight": [700, 35]},
    {"component": "TrackOrders", "topLeft": [710, 5], "bottomRight": [830, 35]},
    {"component": "ShopFamilyDollar", "topLeft": [1720, 5], "bottomRight": [1910, 35]},
    {"component": "MainHeader", "topLeft": [0, 45], "bottomRight": [1920, 120]},
    {"component": "Logo", "topLeft": [10, 50], "bottomRight": [200, 110]},
    {"component": "SearchBar", "topLeft": [220, 60], "bottomRight": [1600, 100]},
    {"component": "MoreChoices", "topLeft": [1620, 60], "bottomRight": [1700, 100]},
    {"component": "Account", "topLeft": [1720, 60], "bottomRight": [1800, 100]},
    {"component": "Cart", "topLeft": [1820, 60], "bottomRight": [1900, 100]},
    {"component": "NavigationMenu", "topLeft": [0, 125], "bottomRight": [1920, 200]},
    {"component": "AllDepartments", "topLeft": [10, 130], "bottomRight": [160, 195]},
    {"component": "CategoryLinks", "topLeft": [170, 130], "bottomRight": [1900, 195]},
    {"component": "Main", "topLeft": [0, 200], "bottomRight": [1920, 1040]},
    {"component": "AppDownloadBanner", "topLeft": [0, 200], "bottomRight": [1920, 280]},
    {"component": "BackToSchoolPromo", "topLeft": [0, 285], "bottomRight": [1920, 1040]},
    {"component": "PromoImage", "topLeft": [0, 285], "bottomRight": [1920, 1040]},
    {"component": "PromoText", "topLeft": [50, 350], "bottomRight": [600, 500]},
    {"component": "Footer", "topLeft": [0, 1040], "bottomRight": [1920, 1080]},
    {"component": "TrustedSite", "topLeft": [10, 1050], "bottomRight": [100, 1070]}
]

# Draw rectangles and labels on the image
for item in data:
    component = item['component']
    topLeft = tuple(item['topLeft'])
    bottomRight = tuple(item['bottomRight'])
    
    # Draw rectangle
    cv2.rectangle(image, topLeft, bottomRight, (0, 255, 0), 2)
    
    # Put label
    label_position = (topLeft[0], topLeft[1] - 10)
    cv2.putText(image, component, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Resize the image for display
scale_percent = 50  # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)

# Resize image
resized_image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

# Save the labeled image
output_path = 'labeled_dollartree.jpg'
cv2.imwrite(output_path, image)

# Display the resized image
cv2.imshow('Labeled Image', resized_image)
cv2.waitKey(0)
cv2.destroyAllWindows()