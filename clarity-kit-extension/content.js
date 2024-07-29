console.log('Clarity Kit for NVDA loaded successfully.')

// Function to log the element in focus
function logFocusedElement(event) {
  const focusedElement = event.target;
  console.log("Element in focus:", focusedElement);
  console.log("Element tag name:", focusedElement.tagName);
  console.log("Element attributes:", focusedElement.attributes);
  console.log("Element inner text:", focusedElement.innerText);
}

// Add event listener for focus and focusin events
document.addEventListener('mouseover', logFocusedElement, true);
document.addEventListener('focusin', logFocusedElement, true);