console.log('Clarity Kit for NVDA loaded successfully.')

const elementsData = [];

function generateRandomString() {
    const characters = 'ABCDFHIJKLMPRSTUVWXY';
    return characters.charAt(Math.floor(Math.random() * characters.length));
}

// Function to create the red box and floating tag
function highlightElement(element, id) {
    const rect = element.getBoundingClientRect();

    // Create a red box around the element
    const box = document.createElement('div');
    box.style.position = 'absolute';
    box.style.border = '2px solid red';
    box.style.pointerEvents = 'none';
    box.style.zIndex = '9999998';

    // Initial placement of the box
    updateBoxPosition(box, element);
    document.body.appendChild(box);

    // Create a floating tag with the ID number
    const tag = document.createElement('div');
    tag.innerText = id.split('').join(' '); // add spaces for readability
    tag.style.position = 'fixed';
    tag.style.backgroundColor = 'rgba(255, 255, 0, 1)';  // Yellow background with 70% opacity
    tag.style.color = 'black';
    tag.style.padding = '2px 4px';
    tag.style.borderRadius = '0px';
    tag.style.border = '1px solid black';
    tag.style.fontSize = '10px';
    tag.style.pointerEvents = 'none';
    tag.style.zIndex = '9999999';

    // Initial placement of the tag
    updateTagPosition(tag, element);
    document.body.appendChild(tag);

    // Store the element, box, and tag for later updates
    elementsData.push({ id, element, box, tag });
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
    tag.style.top = `${rect.top + rect.height}px`;
    tag.style.left = `${rect.left + rect.width / 2}px`;
    tag.style.transform = 'translateX(-50%)';
}

// Function to update all box and tag positions when the page layout changes
function updateAllPositions() {
    elementsData.forEach(({ element, box, tag }) => {
        updateBoxPosition(box, element);
        updateTagPosition(tag, element);
        if (!element.checkVisibility({visibilityProperty: true})) {
            box.style.visibility = 'hidden';
            tag.style.visibility = 'hidden';
        } else {
            box.style.visibility = 'visible';
            tag.style.visibility = 'visible';
        }
    });
}

// Get all interactable elements
const interactableElements = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [role="link"], [tabindex], [onclick]');

// Loop through each element and highlight it
// TODO ensure uniqueness of IDs

const characters = 'ABCDFHIJKLMPRSTUVWXY';
function generateCombinations(str) {
    let result = [];

    // // Generate 2-character combinations
    // for (let i = 0; i < str.length; i++) {
    //     for (let j = 0; j < str.length; j++) {
    //         if (i !== j) {
    //             result.push(str[i] + str[j]);
    //         }
    //     }
    // }

    // Generate 3-character combinations
    for (let i = 0; i < str.length; i++) {
        for (let j = 0; j < str.length; j++) {
            for (let k = 0; k < str.length; k++) {
                if (i !== j && i !== k && j !== k) {
                    result.push(str[i] + str[j] + str[k]);
                }
            }
        }
    }

    return result;
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        let j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]]; // Swap elements
    }
    return array;
}

// get all possible IDs and shuffle
const possibleIDs = generateCombinations(characters)
const shuffledIDs = shuffleArray(possibleIDs)

interactableElements.forEach((element, index) => {
    highlightElement(element, shuffledIDs[index % shuffledIDs.length]); // may produce duplicates
});

// Update the positions of boxes and tags on window resize and scroll
// TODO delete old elements and add new ones every interval
setInterval(updateAllPositions, 3000)
// window.addEventListener('scroll', updateAllPositions);
// window.addEventListener('resize', updateAllPositions);

const WEBSOCKET_URL = 'ws://localhost:8765';  // Replace with your WebSocket URL
const RECONNECT_INTERVAL = 10000;  // 10 seconds

let ws;

function connectWebSocket() {
  if (ws) {
    ws.close();
  }

  ws = new WebSocket(WEBSOCKET_URL);
  let pollId = null;

  ws.onopen = () => {
    console.log('WebSocket connection established.');
    ws.send(JSON.stringify({type: 'log', payload: `WebSocket connection established.`}))
    // Optionally, handle WebSocket connection open

    function pollSocket() {
        console.log('Polling...')
        ws.send(JSON.stringify({type: 'poll'}))
    }

    pollId = setInterval(pollSocket, 1000)

  };

  ws.onmessage = (event) => {
    console.log('Received message:', event.data);

    let hitElement = null;
    
    elementsData.forEach(
        ({id, element}) => {
            if (event.data == id) { 
                console.log('hit!')
                hitElement = element
                element.focus()
                element.click()
            }
        }
    )
    if (hitElement) {
        ws.send(JSON.stringify({type: 'log', payload: `Hit! Element: ${hitElement.outerHTML}`}))
    } else {
        ws.send(JSON.stringify({type: 'log', payload: `Miss for ${event.data}`}))
    }

  };

  ws.onclose = (event) => {
    console.log('WebSocket connection closed. Reconnecting in 10 seconds...');
    setTimeout(connectWebSocket, RECONNECT_INTERVAL);
    clearInterval(pollId)
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    ws.close();
  };

}

// Start WebSocket connection on extension startup
connectWebSocket();