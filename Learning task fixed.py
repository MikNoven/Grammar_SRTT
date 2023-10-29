#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 13:35:37 2023
Main file of the Grammar_SRTT experiment.
@author: gdf724
"""

#%% Import necessary packages.
import os
from psychopy import gui
from psychopy.visual import Window, TextStim, ImageStim, SimpleImageStim
from psychopy import event, core, monitors, prefs
prefs.general['audioLib'] = ['pygame']
import numpy as np
import Grammar_stimuli as gstim
from datetime import date
import pandas as pd

#%% Get subject dialog box
def subject_dialog(title_text):
    subj=''
    exp_info = {'Learning task\nsubject': ''}  
    loopDiag=True
    while loopDiag:
        dlg = gui.DlgFromDict(exp_info,title=title_text)
        
        if not dlg.OK:
            controlled_e()
        else:
            subj=exp_info['Learning task\nsubject']
            if subj!='':
                loopDiag=False  
    return subj

#%% Remove problematic variables and quit 
def controlled_e():
    if 'kb' in globals():
        global kb
        del(kb)
    if 'keys' in globals():
        global keys
        del(keys)
    if 'win' in globals():
        global win
        win.close()
        del(win)
    if 'loopDiag' in globals():
        global loopDiag
        del(loopDiag)
    if 'clock' in globals():
        global clock
        del(clock)
    core.quit()

#%% Make a save folder with date stamp
def make_savefolder(save_path, subj):
    savefolder = os.path.join(save_path,subj+'_'+date.today().isoformat()+'_learning')
    if os.path.exists(savefolder):
        savefolder = "error"
    else:
        os.makedirs(savefolder)
    return savefolder

#%% Define the hardware
cedrus_RB840 = True #Whether to use Cedrus or keyboard. (affects which buttons to use.)
mon = monitors.Monitor('SonyG55')
mon.setSizePix((1920,1080))
winsize=(1920,1080)

if cedrus_RB840:
    allowed_keys = ['a', 'b', 'c', 'f', 'g', 'h']
    continue_keys = ['d', 'e']
    continue_key_name = "one of the bottom keys"
    img_paths = {
        "a": "01.jpg",
        "b": "02.jpg",
        "c": "03.jpg",
        "f": "04.jpg",
        "g": "05.jpg",
        "h": "06.jpg"
        }
else:
    allowed_keys = ['s', 'd', 'f', 'j', 'k', 'l']
    continue_keys = ['space']
    continue_key_name = "space bar"
    img_paths = {
        "s": "01.jpg",
        "d": "02.jpg",
        "f": "03.jpg",
        "j": "04.jpg",
        "k": "05.jpg",
        "l": "06.jpg"
        }

#%% Define the paradigm. 
#SRTT
nbrOfBlocks = 15
lengthOfSequences = 8 #Number of presses per sequence.
sequencesPerBlock = 5
pause_block_length = 1 #Pause between blocks length in seconds. 
pause_trial_length = 0.5 #Pause length for pause trials in seconds.
nbrOfLongBreaks = 2 #Number of longer breaks that are gone through by button press. 
nbrOfStartKeys = 2 #Can be 2 or 1 and alternates between [L3] and [L3,R1].
begin_with_set_sequences = True


#%% Define grammar!
grammar_type = '5050' #'8020', '8020', '5050', or 'random'
grammar_version = 'b' #'a' or 'b'
     
#%% Define save path
save_path = 'C:\\Users\\isaki\\Documents\\Skole\\Bachelor\\Grammar_SRTT-main' 

#%% Gather subject information and make sure that the subject name is set and make a save folder.
loop_subjDial=True
title_text = "Write subject ID"
while loop_subjDial:
    subj = subject_dialog(title_text)
    savefolder = make_savefolder(save_path, subj)
    if savefolder == "" or savefolder == "error":
        title_text = "Subject ID already tested today!"
    else:
        loop_subjDial = False
    
#%% Save settings
with open(os.path.join(savefolder,'settings.txt'),'w') as f:
    f.write('subject:'+str(subj)+'\n')
    f.write('cedrus_RB840:'+str(cedrus_RB840)+'\n')
    f.write('nbrOfBlocks:'+str(nbrOfBlocks)+'\n')
    f.write('lengthOfSequences:'+str(lengthOfSequences)+'\n')
    f.write('sequencesPerBlock:'+str(sequencesPerBlock)+'\n')
    f.write('pause_block_length:'+str(pause_block_length)+'\n')
    f.write('pause_trial_length:'+str(pause_trial_length)+'\n')
    f.write('nbrOfLongBreaks:'+str(nbrOfLongBreaks)+'\n')
    f.write('grammar_type:'+str(grammar_type)+'\n')
    f.write('grammar_version:'+str(grammar_version)+'\n')
    f.write('nbrOfStartKeys:'+str(nbrOfStartKeys)+'\n')
    f.write('begin_with_set_sequences:'+str(begin_with_set_sequences)+'\n')

#%% Initialize Window and make welcome screen.
welcome_string = "Welcome to the experiment!\nPut your fingers on the target keys on the keyboard.\nPlease press the indicated keys as quickly as possible.\nAre you ready to start?\nPress "+continue_key_name+" to continue"
win = Window(size=winsize, monitor=mon, fullscr=False, screen=0, units="norm", pos=[0,0], color=[-.69,-.69,-.69], colorSpace = 'rgb')
welcome_text = TextStim(win, welcome_string, pos=(0.0, 0.8), color=(1, 1, 1), units = "norm", height = 0.05, wrapWidth=0.8)
instr_image_stim = ImageStim(win, image='Instructions_figure.jpeg')
instr_image_stim.draw()
welcome_text.draw()
win.flip()
#Wait until subject has pressed enter or escape
#kb = Keyboard()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents=True)
if response[-1] in continue_keys: 
    pause_text = TextStim(win, "Wait", color=(1, 1, 1), colorSpace='rgb')
    pause_text.draw()
    win.flip()
if 'escape' in response:
    controlled_e()

clock = core.Clock()


#%%Warm up
#Start with some interactive instructions. E.g. Generate s-d-f-j-k-l. Inform 
#that participants need to be as quick and accurate as possible. 
warmup_timings = []
warmup_responses = []

for key in allowed_keys:
    #Present correct instruction.
    trial_stim = SimpleImageStim(win, image=img_paths[key])
    trial_stim.draw()
    win.flip()
    t_wu_start = clock.getTime()
    
    #Collect keypress. Right now only allows presses on the correct 
    response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
    if response[-1] in allowed_keys:
        warmup_timings.append(clock.getTime()-t_wu_start)
        warmup_responses.append(response[-1])
        continue
    elif response[-1]=='escape':
        controlled_e()
    
#%%Ready to start screen.
ready_string = "Great job!\nAre you ready to start the experiment?\nPress "+continue_key_name+" to continue"
ready_text = TextStim(win, ready_string, color=(1, 1, 1), colorSpace='rgb')
ready_text.draw()
win.flip()
#Wait until subject has pressed enter or escape
#kb = Keyboard()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents=True)
if response[-1] in continue_keys: 
    pause_text = TextStim(win, "Wait", color=(1, 1, 1), colorSpace='rgb')
    pause_text.draw()
    win.flip()
if 'escape' in response:
    controlled_e()

#%%Calculate number of blocks before longer break
pause_indices = np.linspace(0,nbrOfBlocks,nbrOfLongBreaks+2)
pause_indices = [round(x) for x in pause_indices[1:-1]]

quarantine_presses_key = []
quarantine_presses_RT = []
quarantine_presses_correct = []
quarantine_presses_block = []
quarantine_presses_trial = []

for block_itr in range(nbrOfBlocks):
#%% Initialize the experiment.
    #Get sequences for the block. (Separate class.)
    if grammar_type == 'random':
        block_trials = gstim.getRandomSequences(lengthOfSequences,sequencesPerBlock,cedrus_RB840)
    elif grammar_type == '8020' and begin_with_set_sequences:
        block_trials = gstim.getFixed8020Block(lengthOfSequences,sequencesPerBlock,cedrus_RB840,nbrOfStartKeys,grammar_version)
        begin_with_set_sequences = False
    else:
        block_trials = gstim.getGrammarSequences(lengthOfSequences,sequencesPerBlock,\
                                                 grammar_type,True,savefolder,block_itr+1,subj,cedrus_RB840,nbrOfStartKeys,grammar_version)
    # Initialize data save structures.
    block_RT = np.zeros(len(block_trials))
    block_response = []
    block_feedbackGiven = [] #Saves 1 if the subject was too slow or inaccurate.
    block_accuracy = np.zeros(len(block_trials)) #To keep track of accuracy in the experiment.
    

#%%Run experiment block.
    acc_check_skips = 0
    for trial_itr in range(len(block_trials)):
        trial = block_trials[trial_itr]
        #Present correct stimulus + measure t_trial_init
        if trial == 'pause':
            trial_stim = SimpleImageStim(win, image='00.jpg')
            trial_stim.draw()
            win.flip()
            block_RT[trial_itr] = np.nan
            block_response.append(np.nan)
            block_accuracy[trial_itr] = np.nan
            core.wait(pause_trial_length)
            if trial_itr >= 29:
                msg_text = ""
                acc_check = block_accuracy[trial_itr-20:trial_itr]
                acc_check = acc_check[~np.isnan(acc_check)]
                if np.nanmean(block_RT[trial_itr-10:trial_itr]) >= 0.8:
                    msg_text = msg_text+"Too slow, please speed up.\n"
                if sum(acc_check)/len(acc_check) < 0.7 and acc_check_skips==0:
                    msg_text = msg_text+"Too many inaccuracies. Please pay attention.\n"
                    acc_check_skips=20
                if not msg_text=="":
                    feedback_text = TextStim(win, msg_text, color=(1, 1, 1), colorSpace='rgb')
                    block_feedbackGiven.append(1)
                    feedback_text.draw()
                    win.flip()
                    core.wait(1.5)
        else:
            t_init = clock.getTime()
            trial_stim = SimpleImageStim(win, image=img_paths[trial])
            trial_stim.draw()
            win.flip()
            #Collect response from the keyboard.
            stop = False
            while not stop:
                response = event.getKeys(keyList=allowed_keys+['escape'])
                if len(response)>0 and clock.getTime()-t_init <= 0.12:
                    quarantine_presses_key.append(response[-1])
                    quarantine_presses_RT.append(clock.getTime()-t_init)
                    quarantine_presses_correct.append(trial)
                    quarantine_presses_block.append(block_itr+1)
                    quarantine_presses_trial.append(trial_itr+1)
                elif len(response)>0 and response[-1] in allowed_keys:
                    block_RT[trial_itr] = clock.getTime()-t_init
                    block_response.append(response[-1])
                    block_accuracy[trial_itr] = int(trial==response[-1])
                    stop=True
                elif len(response)>0 and response[-1]=='escape':
                    controlled_e()
    
            #After 30 trials, check that accuracy is above 95% and that average reaction time is below 450 ms. 
            if acc_check_skips > 0:
                acc_check_skips = acc_check_skips - 1
                    
                
    #Save block data and save to csv-file.
    block_save = pd.DataFrame({'trial':block_trials,
                               'reaction_time':block_RT,
                               'response':block_response,
                               'accuracy':block_accuracy}
        )
    block_save.to_csv(os.path.join(savefolder,subj+'_block_'+str(block_itr+1)+'.csv')) #Maybe save as pickle instead.
    #Take a break
    if block_itr < nbrOfBlocks-1:
        if block_itr in pause_indices:
            ready_string = "Great job!\nHave a short break.\nPress "+continue_key_name+" to continue"
            ready_text = TextStim(win, ready_string, color=(1, 1, 1), colorSpace='rgb')
            ready_text.draw()
            win.flip()

            response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents=True)
            if response[-1] in continue_keys: 
                pause_text = TextStim(win, "Wait", color=(1, 1, 1), colorSpace='rgb')
                pause_text.draw()
                win.flip()
            if 'escape' in response:
                controlled_e()
        else:
            pause_text="Great job! Take a "+str(pause_block_length)+" second break.\n"
            for pause_itr in range(pause_block_length):
                pause_stim = SimpleImageStim(win, image='00.jpg')
                pause_stim.draw()
                win.flip()
                core.wait(0.5)

#%% Save the quarantine presses
quarantine_presses = pd.DataFrame({'response':quarantine_presses_key,
                                   'reaction_time':quarantine_presses_RT,
                                   'trial':quarantine_presses_correct,
                                   'block':quarantine_presses_block,
                                   'trialNbr':quarantine_presses_trial}
                                  )
quarantine_presses.to_csv(os.path.join(savefolder,subj+'_quarantine_presses.csv'))

#%% End of SRTT message.
end_text = "Great job! You are now done with this part of the experiment!\nPress "+continue_key_name+" to continue."
end_stim = TextStim(win, end_text, color=(1, 1, 1), colorSpace='rgb')
end_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('SRTT done.')
elif response[-1]=='escape':
    controlled_e()


#%% Thank the participant and quit the program
end_of_experiment_text = "Thank you for participating in our experiment!"
end_of_experiment_stim = TextStim(win, end_of_experiment_text, color=(1, 1, 1), colorSpace='rgb')
end_of_experiment_stim.draw()
win.flip()
core.wait(3)
controlled_e()