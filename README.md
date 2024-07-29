# clarity-kit

## Build Log

### 7/29/24
- gave up on chrome extension, doesn't integrate well with NVDA
- completed MVP (<3 days of work)
  - frontend: NVDA addon, audio-traversable tree representation of screen
  - backend: flask server that talks to claude, gives JSON to frontend
- todo
  - deploy backend, package addon to give to beta testers (I have now reached first quantum of utility)
  - tune claude prompts to get the clickable elements
  - add a clicking capacity, knowing the structure is only half the problem, need interactivity

## Usage
- install NVDA, enable developer mode (under advanced settings)
- Start Screen > explore user configuration > find 'scratchpad' directory
- mklink /D target source, symlink addon/globalPlugins/clarity to scratchpad/globalPlugins/clarity
- Reload plugins (NVDA+n > tools)
- Fire up flask (app.py)
- All set. Use NVDA+z to start, and NVDA+ arrow keys to traverse tree

## Debugging
- %temp%/nvda.log