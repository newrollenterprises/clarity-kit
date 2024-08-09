# clarity-kit

## Build Log

### 08/09/24
- I figured out why imports were breaking. NVDA uses python 3.11 32-bit version. You need to use `/path/to/3.11/32-bit/python.exe -m pip install [module]`. It was saying import not found because the .pyd files (c-extended) have a name tag that matches them to a particular arch. So when NVDA's python tried to import only .pyd files for my python 3.9 were being found

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
- Fire up flask (app.py)
- All set. Use NVDA+z to start, and NVDA+ arrow keys to traverse tree

## Debugging
- %temp%/nvda.log