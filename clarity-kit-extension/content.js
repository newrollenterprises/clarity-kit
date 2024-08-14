console.log('Clarity Kit for NVDA loaded successfully.')

const elementsData = [];

// Function to create the red box and floating tag
function highlightElement(element, id) {
    const rect = element.getBoundingClientRect();

    // Create a red box around the element
    const box = document.createElement('div');
    box.style.position = 'absolute';
    box.style.border = '2px solid red';
    box.style.pointerEvents = 'none';
    box.style.zIndex = '9999';

    // Initial placement of the box
    updateBoxPosition(box, element);
    document.body.appendChild(box);

    // Create a floating tag with the ID number
    const tag = document.createElement('div');
    tag.innerText = id;
    tag.style.position = 'fixed';
    tag.style.backgroundColor = 'rgba(255, 255, 0, 0.7)';  // Yellow background with 70% opacity
    tag.style.color = 'red';
    tag.style.padding = '2px 5px';
    tag.style.borderRadius = '5px';
    tag.style.fontSize = '12px';
    tag.style.pointerEvents = 'none';
    tag.style.zIndex = '9999';

    // Initial placement of the tag
    updateTagPosition(tag, element);
    document.body.appendChild(tag);

    // Store the element, box, and tag for later updates
    elementsData.push({ element, box, tag });
}

// Function to update the box's position based on the element's current location
function updateBoxPosition(box, element) {
    const rect = element.getBoundingClientRect();
    box.style.top = `${rect.top + window.scrollY}px`;
    box.style.left = `${rect.left + window.scrollX}px`;
    box.style.width = `${rect.width}px`;
    box.style.height = `${rect.height}px`;
}

// Function to update the tag's position based on the element's current location
function updateTagPosition(tag, element) {
    const rect = element.getBoundingClientRect();
    tag.style.top = `${rect.top + rect.height / 2}px`;
    tag.style.left = `${rect.left + rect.width / 2}px`;
    tag.style.transform = 'translate(-50%, -50%)';
}

// Function to update all box and tag positions when the page layout changes
function updateAllPositions() {
    elementsData.forEach(({ element, box, tag }) => {
        updateBoxPosition(box, element);
        updateTagPosition(tag, element);
    });
}

// Get all interactable elements
const interactableElements = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [role="link"], [tabindex], [onclick]');

// Loop through each element and highlight it
interactableElements.forEach((element, index) => {
    highlightElement(element, index + 1);
});

// Update the positions of boxes and tags on window resize and scroll
setInterval(updateAllPositions, 3000)
// window.addEventListener('scroll', updateAllPositions);
// window.addEventListener('resize', updateAllPositions);
