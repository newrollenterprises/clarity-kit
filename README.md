# clarity-kit

## Ideas
- talk to page? ask questions in english
- "magic search" english query finds element (using info from extension)
- sophisticated lazy loading, back-and-forth conditional expansion of components
- simple lazy loading, first pass, then immediate involuntary background second pass to fill in attributes

## Todo
- extension
  - speed up refresh interval
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

## Debugging
- %temp%/nvda.log