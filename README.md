# clarity-kit

## Ideas
- talk to page? ask questions in english
- "magic search" english query finds element (using info from extension)
- sophisticated lazy loading, back-and-forth conditional expansion of components
- simple lazy loading, first pass, then immediate involuntary background second pass to fill in attributes
- use text matching (when available) via chrome extension for even more reliable clicks
  - claude's textContent compared against elementsData[].textContent

## Todo
- extension
  - fix click dynamic pages no refresh of elements
  - remove extraneous elements (amazon for ex)
- backend
  - easier LLM swap out
  - make everything JSON (/processScreen)
- addon 

## Build Log

### 08/14/24
- kept getting 529 (server overload) errors from Claude, so I created backend/app2.py which uses OpenAI under the hood instead. Less effective but more reliable.

### 08/12/24
- ditched OCR text-matching, instead I use tesseract to find text and label each text blob with an ID number. Claude matches ID (drawn over original screen shot) to components. Click() location is specified using tesseract coordinates and IDs.

### 08/09/24
- Clarity Kit now lets you click elements using OCR text-matching. Claude is bad at positions. So I match textContent from Claude with local OCR text recognition to find element to click.
- I figured out why imports were breaking. NVDA uses python 3.11 32-bit version. You need to use `/path/to/3.11/32-bit/python.exe -m pip install [module]`. It was saying import not found because the .pyd files (c-extended) have a name tag that matches them to a particular arch. So when NVDA's python tried to import only .pyd files for my python 3.9 were being found
- IDEA: iterate on sub-components of the tree, like a "more info" command to access parts that weren't well-described by Claude
- todo
  - pre-scan tree and add "clickable" audio description tag

### 07/29/24
- gave up on chrome extension, doesn't integrate well with NVDA
- completed MVP (<3 days of work)
  - frontend: NVDA addon, audio-traversable tree representation of screen
  - backend: flask server that talks to claude, gives JSON to frontend
- todo
  - deploy backend, package addon to give to beta testers (I have now reached first quantum of utility)
  - tune claude prompts to get the clickable elements
  - add a clicking capacity, knowing the structure is only half the problem, need interactivity
  - compile/obfuscate code
  - loading indicator

## Usage
- install NVDA, enable developer mode (under advanced settings)
- Start Screen > explore user configuration > find 'scratchpad' directory
- mklink /D target source, symlink addon/globalPlugins/clarity to scratchpad/globalPlugins/clarity
- Reload plugins (NVDA+n > tools)
- Create folder `backend/logs`
- Fire up flask (app.py)
- All set. Use NVDA+z to start, and NVDA+ arrow keys to traverse tree

## Creating a Release

### addon
- run scratchpad plugin one more time to ensure all the python is compiled
- copy addon to version folder, ex: release/1.0.0/addon
- edit manifest.ini as needed (version, etc.)
- for each dependency, in its dist info, delete everything but LICENSE
- add copies of LICENSES as necessary 
- go into /clarity/__pycache__ and copy everything into /clarity
- rename the .pyc so it has the same name as its corresponding .py
  - ex: __init__.cpython-311.pyc -> __init__.pyc
- delete everything in /clarity except the .pyc files
- change email.txt to have the user's email (at the moment any uuid can go inside email.txt and work)
- zip everything inside /addon (manifest.ini is at the root) and rename the zip `clarityKit.nvda-addon`
- copy the .nvda-addon to /release/1.0.0/clarityKit.nvda-addon

### extension
- copy clarity-kit-extension folder and rename to extension
  - ex: /release/1.0.0/extension
- obfuscate the js files, ex: `javascript-obfuscator content.js --rename-globals true`
- delete the old js files and rename the new ones to replace

### other
- add in my LICENSE at /release/1.0.0/LICENSE
- zip the .nvda-addon and extension folder into `clarityKit-1.0.0.zip` 

### testing
- copy clarityKit-1.0.0.zip to downloads and unzip
- disable scratchpad in NVDA (settings > advanced)
- install the addon from unzipped files
- from chrome://extensions, hit load unpacked and select 'extension' folder
- NVDA + z

## Debugging
- %temp%/nvda.log