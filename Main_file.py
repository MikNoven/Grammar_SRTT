#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 13:35:37 2023
Main file of the Grammar_SRTT experiment.
@author: gdf724
"""

#%% Import necessary packages.
from psychopy import gui, monitors
from psychopy.visual import Window, TextStim
from psychopy import core
from psychopy.hardware.keyboard import Keyboard
import os

#%% Remove problematic variables and quit 
def controlled_e():
    if 'kb' in locals():
        del(kb)
    if 'keys' in locals():
        del(keys)
    if 'welcome_on' in locals():
        del(welcome_on)
    if 'win' in locals():
        del(win)
    if 'loopDiag' in locals():
        del(loopDiag)
    core.quit()

#%% Gather subject information and make sure that the subject name is set. 
exp_info = {'subject': ''}  
loopDiag=True
while loopDiag:
    dlg = gui.DlgFromDict(exp_info)
    
    if not dlg.OK:
        controlled_e()
    else:
        subj=exp_info['subject']
        if subj!='':
            loopDiag=False  
#Can't allow for it to close with pressing enter. 

#%% Define the paradigm. 
nbrOfBlocks = 10
lengthOfSequences = 8 #Number of presses per sequence.
sequencesPerBlock = 25

#%% Define the hardware
mon = monitors.Monitor('SonyG55')
mon.setSizePix((2560,1600))

#%% Initialize Window and make welcome screen.
welcome_string = "Welcome to the experiment!\nPut your fingers on the target keys on the keyboard.\nPlease press the indicated keys as quickly as possible.\nAre you ready to start?"
win = Window(size=[800,600],color=(0, 0, 0), colorSpace='rgb', monitor=mon, fullscr=False, screen=0)
welcome_text = TextStim(win, welcome_string, color=(1, 1, 1), colorSpace='rgb')
welcome_text.draw()
win.flip()
#Wait until subject has pressed enter or escape
kb = Keyboard()
welcome_on=True
while welcome_on:
    keys = kb.getKeys(['return', 'escape'], waitRelease = True)
    if 'return' in keys: 
        welcome_on=False
        pause_text = TextStim(win, "Wait", color=(1, 1, 1), colorSpace='rgb')
        pause_text.draw()
        win.flip()
    if 'escape' in keys:
        controlled_e()

#for block_itr in range(nbrOfBlocks):
#%% Initialize the experiment.
#Get sequences for the block. (Separate class.)

#
clock = core.Clock()

#Wait with "fullscr=True" until I have a way to close the program.

t_init = clock.getTime()
core.wait(2)
#keys = kb.getKeys()
#spacebar_pressed = "space" in keys
win.close()
t_after = clock.getTime()-t_init
#%% Quit the program
controlled_e()