#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 19:13:48 2023
Separate generation task. 
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
    exp_info = {'Generation task\nsubject': ''}  
    loopDiag=True
    while loopDiag:
        dlg = gui.DlgFromDict(exp_info,title=title_text)
        
        if not dlg.OK:
            controlled_e()
        else:
            subj=exp_info['Generation task\nsubject']
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
    savefolder = os.path.join(save_path,subj+'_'+date.today().isoformat()+'_generation')
    if os.path.exists(savefolder):
        savefolder = "error"
    else:
        os.makedirs(savefolder)
    return savefolder


#%% Define the hardware
cedrus_RB840 = False #Whether to use Cedrus or keyboard. (affects which buttons to use.)
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
grammar_type = '5050' #'8020', '5050', or 'random'
grammar_version = 'a' 
nbrOfStartKeys = 2 #Can be 2 or 1 and alternates between [L3] and [L3,R1].
#Generation task
lengthOfSequences = 8 #Number of presses per sequence.
pregeneratedGenerationTask = 3 #How many of the elements should be pre-generated in the generation task. 0 for completely free generation.
grammaticalPregenerated_randomGenTask = True #False if starting sequence should be random
nbrOfGeneratedSequences = 4


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
    f.write('lengthOfSequences:'+str(lengthOfSequences)+'\n')
    f.write('grammar_type:'+str(grammar_type)+'\n')
    f.write('grammar_version:'+str(grammar_version)+'\n')
    f.write('nbrOfStartKeys:'+str(nbrOfStartKeys)+'\n')
    f.write('pregeneratedGenerationTask:'+str(pregeneratedGenerationTask)+'\n')
    f.write('nbrOfGeneratedSequences:'+str(nbrOfGeneratedSequences)+'\n')
    f.write('grammaticalPregenerated_randomGenTask:'+str(grammaticalPregenerated_randomGenTask)+'\n')
   
#%%Generation task intialization.
win = Window(size=winsize, monitor=mon, fullscr=False, screen=0, units="norm", pos=[0,0], color=[-.69,-.69,-.69], colorSpace = 'rgb')
gentest_start_text = "In the previous part of the experiment,\nthe cues were presented in sequences\nthat came from a system.\nPress "+continue_key_name+" to continue."
gentest_start_stim = TextStim(win, gentest_start_text, color=(1, 1, 1), colorSpace='rgb')
gentest_start_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('First gentest text done.')
elif response[-1]=='escape':
    controlled_e()

clock = core.Clock()
#%%Generation task grammatical.
if pregeneratedGenerationTask == 0 or grammar_type == 'random':
    gentest_grammar_text = "We now ask you to freely generate "+str(nbrOfGeneratedSequences)+" sequences\nfrom that system.\nPress "+continue_key_name+" to continue."
else:
    gentest_grammar_text = "We now ask you to freely generate "+str(nbrOfGeneratedSequences)+" sequences\nfrom that system.\nYou will get "+str(pregeneratedGenerationTask)+" keys to press to start you off\nPress "+continue_key_name+" to continue."
   
gentest_grammar_stim = TextStim(win, gentest_grammar_text, color=(1, 1, 1), colorSpace='rgb')
gentest_grammar_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('Generation task grammar.')
elif response[-1]=='escape':
    controlled_e()

#Start with empty and then show the pressed key image 
gen_time = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)
gen_response = []
gen_seq = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)
gen_pregenerated = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)

if pregeneratedGenerationTask == 0 or grammar_type == 'random':
    for gen_itr in range(nbrOfGeneratedSequences):
        gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
        gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
        gen_seq_text_stim.draw()
        win.flip()
        core.wait(1)
        genStim = SimpleImageStim(win, image='00.jpg')
        genStim.draw()
        win.flip()
        for seq_itr in range(lengthOfSequences):
            t_init = clock.getTime()
            response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
            if response[-1] in allowed_keys:
                gen_time[seq_itr+lengthOfSequences*gen_itr] = clock.getTime()-t_init
                gen_response.append(response[-1])
                gen_seq[seq_itr+lengthOfSequences*gen_itr] = gen_itr+1
                
                genStim = SimpleImageStim(win, image=img_paths[response[-1]])
                genStim.draw()
                win.flip()
            elif response[-1]=='escape':
                controlled_e()
else:
    for gen_itr in range(nbrOfGeneratedSequences):
        gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
        gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
        gen_seq_text_stim.draw()
        win.flip()
        core.wait(0.5)
        pregen_seq = gstim.getPreGeneratedSequences(pregeneratedGenerationTask,'5050',cedrus_RB840,nbrOfStartKeys,grammar_version)
        for pregen_itr in range(pregeneratedGenerationTask):
            genStim = SimpleImageStim(win, image=img_paths[pregen_seq[pregen_itr]])
            genStim.draw()
            win.flip()
            t_init = clock.getTime()
            response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
            if response[-1] in allowed_keys:
                gen_time[pregen_itr+lengthOfSequences*gen_itr] = clock.getTime()-t_init
                gen_response.append(response[-1])
                gen_seq[pregen_itr+lengthOfSequences*gen_itr] = gen_itr+1
                gen_pregenerated[pregen_itr+lengthOfSequences*gen_itr] = 1
            elif response[-1]=='escape':
                controlled_e()
        genStim = SimpleImageStim(win, image='00.jpg')
        genStim.draw()
        win.flip()
        for seq_itr in range(lengthOfSequences-pregeneratedGenerationTask):
            t_init = clock.getTime()
            response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
            if response[-1] in allowed_keys:
                gen_time[pregen_itr+seq_itr+1+lengthOfSequences*gen_itr] = clock.getTime()-t_init
                gen_response.append(response[-1])
                gen_seq[pregen_itr+seq_itr+1+lengthOfSequences*gen_itr] = gen_itr+1
                genStim = SimpleImageStim(win, image=img_paths[response[-1]])
                genStim.draw()
                win.flip()
            elif response[-1]=='escape':
                controlled_e()
                
#Save the information. 
gen_gram_save = pd.DataFrame({'sequence':gen_seq,
                           'generation_time':gen_time,
                           'response':gen_response,
                           'pregenerated':gen_pregenerated}
    )
gen_gram_save.to_csv(os.path.join(savefolder,subj+'_generation_grammatical.csv')) #Maybe save as pickle instead.


#%%Generation task random.
if pregeneratedGenerationTask == 0 or grammar_type == 'random':
    gentest_grammar_text = "We now ask you to freely generate "+str(nbrOfGeneratedSequences)+" sequences\nthat you are sure is not\nfrom that system.\nYou are not allowed to press the same key twice in a row.\nPress "+continue_key_name+" to continue."
else:
    gentest_grammar_text = "We now ask you to freely generate "+str(nbrOfGeneratedSequences)+" sequences\nthat you are sure is not\nfrom that system.\nYou are not allowed to press the same key twice in a row.\nYou will get "+str(pregeneratedGenerationTask)+" keys to press to start you off\nPress "+continue_key_name+" to continue."
   
gentest_random_text = "We now ask you to freely generate "+str(nbrOfGeneratedSequences)+" sequences\nthat you are sure is not\nfrom that sequence.\nYou are not allowed to press the same key twice in a row.\nPress "+continue_key_name+" to continue."
gentest_random_stim = TextStim(win, gentest_random_text, color=(1, 1, 1), colorSpace='rgb')
gentest_random_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('Generation task random.')
elif response[-1]=='escape':
    controlled_e()

#Start with empty and then show the pressed key image 
gen_time = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)
gen_response = []
gen_seq = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)
gen_pregenerated = np.zeros(nbrOfGeneratedSequences*lengthOfSequences)
if pregeneratedGenerationTask == 0 or grammar_type == 'random':
    for gen_itr in range(nbrOfGeneratedSequences):
        gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
        gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
        gen_seq_text_stim.draw()
        win.flip()
        core.wait(1)
        genStim = SimpleImageStim(win, image='00.jpg')
        genStim.draw()
        win.flip()
        for seq_itr in range(lengthOfSequences):
            
            t_init = clock.getTime()
            response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
            if response[-1] in allowed_keys:
                gen_time[seq_itr+lengthOfSequences*gen_itr] = clock.getTime()-t_init
                gen_response.append(response[-1])
                gen_seq[seq_itr+lengthOfSequences*gen_itr] = gen_itr+1
                
                genStim = SimpleImageStim(win, image=img_paths[response[-1]])
                genStim.draw()
                win.flip()
            elif response[-1]=='escape':
                controlled_e()
else:
    for gen_itr in range(nbrOfGeneratedSequences):
        gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
        gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
        gen_seq_text_stim.draw()
        win.flip()
        core.wait(0.5)
        
        if grammaticalPregenerated_randomGenTask:
            pregen_seq = gstim.getPreGeneratedSequences(pregeneratedGenerationTask,grammar_type,cedrus_RB840,nbrOfStartKeys,grammar_version)
        else:
            pregen_seq = gstim.getPreGeneratedSequences(pregeneratedGenerationTask,'random',cedrus_RB840,nbrOfStartKeys,grammar_version)
            
        for pregen_itr in range(pregeneratedGenerationTask):
            genStim = SimpleImageStim(win, image=img_paths[pregen_seq[pregen_itr]])
            genStim.draw()
            win.flip()
            t_init = clock.getTime()
            response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
            if response[-1] in allowed_keys:
                gen_time[pregen_itr+lengthOfSequences*gen_itr] = clock.getTime()-t_init
                gen_response.append(response[-1])
                gen_seq[pregen_itr+lengthOfSequences*gen_itr] = gen_itr+1
                gen_pregenerated[pregen_itr+lengthOfSequences*gen_itr] = 1
            elif response[-1]=='escape':
                controlled_e()
        genStim = SimpleImageStim(win, image='00.jpg')
        genStim.draw()
        win.flip()
        for seq_itr in range(lengthOfSequences-pregeneratedGenerationTask):
            t_init = clock.getTime()
            response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
            if response[-1] in allowed_keys:
                gen_time[pregen_itr+seq_itr+1+lengthOfSequences*gen_itr] = clock.getTime()-t_init
                gen_response.append(response[-1])
                gen_seq[pregen_itr+seq_itr+1+lengthOfSequences*gen_itr] = gen_itr+1
                genStim = SimpleImageStim(win, image=img_paths[response[-1]])
                genStim.draw()
                win.flip()
            elif response[-1]=='escape':
                controlled_e()
                
#Save the information. 
gen_rand_save = pd.DataFrame({'sequence':gen_seq,
                           'generation_time':gen_time,
                           'response':gen_response,
                           'pregenerated':gen_pregenerated}
    )
gen_rand_save.to_csv(os.path.join(savefolder,subj+'_generation_random.csv')) #Maybe save as pickle instead.

#%% Thank the participant and quit the program
end_of_experiment_text = "Thank you for participating in our experiment!"
end_of_experiment_stim = TextStim(win, end_of_experiment_text, color=(1, 1, 1), colorSpace='rgb')
end_of_experiment_stim.draw()
win.flip()
core.wait(3)
controlled_e()