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
    exp_info = {'subject': ''}  
    loopDiag=True
    while loopDiag:
        dlg = gui.DlgFromDict(exp_info,title=title_text)
        
        if not dlg.OK:
            controlled_e()
        else:
            subj=exp_info['subject']
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
    savefolder = os.path.join(save_path,subj+'_'+date.today().isoformat())
    if os.path.exists(savefolder):
        savefolder = "error"
    else:
        os.makedirs(savefolder)
    return savefolder

#%% Define the hardware
cedrus_RB840 = False #Whether to use Cedrus or keyboard. (affects which buttons to use.)
mon = monitors.Monitor('SonyG55')
mon.setSizePix((2560,1600))
winsize=(1080,720)

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
nbrOfBlocks = 3
lengthOfSequences = 8 #Number of presses per sequence.
sequencesPerBlock = 5
pause_block_length = 15 #Pause between blocks length in seconds. 
pause_trial_length = 0.5 #Pause length for pause trials in seconds.
grammar_type = '8020' #'8020', '5050', or 'random'

#Generation task
nbrOfGeneratedSequences = 3

#%% Define save path
save_path = '/Users/gdf724/Data/ReScale/MovementGrammar/GrammarSRTT/' 

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
    welcome_on=False
    pause_text = TextStim(win, "Wait", color=(1, 1, 1), colorSpace='rgb')
    pause_text.draw()
    win.flip()
if 'escape' in response:
    controlled_e()

#%%Warm up
#Start with some interactive instructions. E.g. Generate s-d-f-j-k-l. Inform 
#that participants need to be as quick and accurate as possible. 
warmup_timings = []
warmup_responses = []
clock = core.Clock()

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
    elif 'escape' in keys:
        controlled_e()
    

for block_itr in range(nbrOfBlocks):
#%% Initialize the experiment.
    #Get sequences for the block. (Separate class.)
    if grammar_type == 'random':
        block_trials = gstim.getRandomSequences(lengthOfSequences,sequencesPerBlock,cedrus_RB840)
    else:
        block_trials = gstim.getGrammarSequences(lengthOfSequences,sequencesPerBlock,\
                                                 grammar_type,True,savefolder,block_itr+1,subj,cedrus_RB840)
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
            response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
            if response[-1] in allowed_keys:
                block_RT[trial_itr] = clock.getTime()-t_init
                block_response.append(response[-1])
                block_accuracy[trial_itr] = int(trial==response[-1])
            elif 'escape' in keys:
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
        pause_text="Great job! Take a "+str(pause_block_length)+" second break.\n"
        for pause_itr in range(pause_block_length):
            pause_stim = TextStim(win, pause_text+str(pause_itr+1)+"/"+str(pause_block_length), color=(1, 1, 1), colorSpace='rgb')
            pause_stim.draw()
            win.flip()
            core.wait(1)
    #Should we make them start the next block on their own? 
#%% End of SRTT message.
end_text = "Great job! You are now done with this part of the experiment!\nPress "+continue_key_name+" to continue."
end_stim = TextStim(win, end_text, color=(1, 1, 1), colorSpace='rgb')
end_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('SRTT done.')
elif 'escape' in keys:
    controlled_e()
    
#%%Generation task intialization.
gentest_start_text = "In the previous part of the experiment,\nthe cues were presented in sequences\nthat came from a system.\nPress "+continue_key_name+" to continue."
gentest_start_stim = TextStim(win, gentest_start_text, color=(1, 1, 1), colorSpace='rgb')
gentest_start_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('First gentest text done.')
elif 'escape' in keys:
    controlled_e()

#%%Generation task grammatical.
gentest_grammar_text = "We now ask you to freely generate "+str(nbrOfGeneratedSequences)+" sequences\nfrom that system.\nPress "+continue_key_name+" to continue."
gentest_grammar_stim = TextStim(win, gentest_grammar_text, color=(1, 1, 1), colorSpace='rgb')
gentest_grammar_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('Generation task grammar.')
elif 'escape' in keys:
    controlled_e()

#Start with empty and then show the pressed key image 
gen_time = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)
gen_response = []
for gen_itr in range(nbrOfGeneratedSequences):
    gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
    gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
    gen_seq_text_stim.draw()
    win.flip()
    core.wait(1)
    gen_seq = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)
    genStim = SimpleImageStim(win, image='00.jpg')
    genStim.draw()
    win.flip()
    for seq_itr in range(lengthOfSequences):
        t_init = clock.getTime()
        response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
        if response[-1] in allowed_keys:
            gen_time[seq_itr+lengthOfSequences*gen_itr] = clock.getTime()-t_init
            gen_response.append(response[-1])
            gen_seq[seq_itr+lengthOfSequences*gen_itr] = seq_itr+1
            
            genStim = SimpleImageStim(win, image=img_paths[response[-1]])
            genStim.draw()
            win.flip()
        elif 'escape' in keys:
            controlled_e()
#Save the information. 
gen_gram_save = pd.DataFrame({'sequence':gen_seq,
                           'generation_time':gen_time,
                           'response':gen_response}
    )
gen_gram_save.to_csv(os.path.join(savefolder,subj+'_generation_grammatical.csv')) #Maybe save as pickle instead.


#%%Generation task random.
gentest_random_text = "We now ask you to freely generate "+str(nbrOfGeneratedSequences)+" sequences\nthat you are sure is not\nfrom that sequence.\nYou are not allowed to press the same key twice in a row.\nPress "+continue_key_name+" to continue."
gentest_random_stim = TextStim(win, gentest_random_text, color=(1, 1, 1), colorSpace='rgb')
gentest_random_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('Generation task random.')
elif 'escape' in keys:
    controlled_e()

#Start with empty and then show the pressed key image 
gen_time = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)
gen_response = []
for gen_itr in range(nbrOfGeneratedSequences):
    gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
    gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
    gen_seq_text_stim.draw()
    win.flip()
    core.wait(1)
    gen_seq = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)
    genStim = SimpleImageStim(win, image='00.jpg')
    genStim.draw()
    win.flip()
    for seq_itr in range(lengthOfSequences):
        t_init = clock.getTime()
        response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
        if response[-1] in allowed_keys:
            gen_time[seq_itr+lengthOfSequences*gen_itr] = clock.getTime()-t_init
            gen_response.append(response[-1])
            gen_seq[seq_itr+lengthOfSequences*gen_itr] = seq_itr+1
            
            genStim = SimpleImageStim(win, image=img_paths[response[-1]])
            genStim.draw()
            win.flip()
        elif 'escape' in keys:
            controlled_e()
#Save the information. 
gen_rand_save = pd.DataFrame({'sequence':gen_seq,
                           'generation_time':gen_time,
                           'response':gen_response}
    )
gen_rand_save.to_csv(os.path.join(savefolder,subj+'_generation_random.csv')) #Maybe save as pickle instead.


#%% Thank the participant and quit the program
end_of_experiment_text = "Thank you for participating in our experiment!"
end_of_experiment_stim = TextStim(win, end_of_experiment_text, color=(1, 1, 1), colorSpace='rgb')
end_of_experiment_stim.draw()
win.flip()
core.wait(3)
controlled_e()