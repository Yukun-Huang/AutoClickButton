# AutoClickButton
readscreen -> visual recongnition -> mouse click

## Requirement
 - PyAutoGUI: Read screenshot, install by pip.
 - OpenCV: Button detection, install by pip.
 - PyUserinput: Mouse & Keyboard Input, install by pip.
 - pyHook: Required by PyUserinput.
 - pyWinhook (optional): Alternative to pyHook.

Q1.How to install pyHook?
 - https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyhook (swig is required)

Q2.TypeError: KeyboardSwitch() missing 8 required positional arguments.
 - Replace pyHook with pyWinhook, that is, import pyWinhook as pyHook
