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
nbrOfBlocks = 15
lengthOfSequences = 8 #Number of presses per sequence.
sequencesPerBlock = 5
pause_block_length = 3 #Pause between blocks length in seconds. 
pause_trial_length = 0.5 #Pause length for pause trials in seconds.
nbrOfLongBreaks = 1 #Number of longer breaks that are gone through by button press. 
grammar_type = '8020' #'8020', '5050', or 'random'
nbrOfStartKeys = 2 #Can be 2 or 1 and alternates between [L3] and [L3,R1].
do_SRTT = True #For debugging 
#Generation task
pregeneratedGenerationTask = 4 #How many of the elements should be pre-generated in the generation task. 0 for completely free generation.
grammaticalPregenerated_randomGenTask = True #False if starting sequence should be random
nbrOfGeneratedSequences = 3


#%% Define save path
save_path = '/Users/gdf724/Data/MovementGrammar/GrammarSRTT/' 

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
    f.write('nbrOfStartKeys:'+str(nbrOfStartKeys)+'\n')
    f.write('pregeneratedGenerationTask:'+str(pregeneratedGenerationTask)+'\n')
    f.write('nbrOfGeneratedSequences:'+str(nbrOfGeneratedSequences)+'\n')
    f.write('grammaticalPregenerated_randomGenTask:'+str(grammaticalPregenerated_randomGenTask)+'\n')
    

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

if do_SRTT:
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
        else:
            block_trials = gstim.getGrammarSequences(lengthOfSequences,sequencesPerBlock,\
                                                     grammar_type,True,savefolder,block_itr+1,subj,cedrus_RB840,nbrOfStartKeys)
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
                    if len(response)>0 and clock.getTime()-t_init <= 0.1:
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
                    pause_stim = TextStim(win, pause_text+str(pause_itr+1)+"/"+str(pause_block_length), color=(1, 1, 1), colorSpace='rgb')
                    pause_stim.draw()
                    win.flip()
                    core.wait(1)
    
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
        
#%%Generation task intialization.
gentest_start_text = "In the previous part of the experiment,\nthe cues were presented in sequences\nthat came from a system.\nPress "+continue_key_name+" to continue."
gentest_start_stim = TextStim(win, gentest_start_text, color=(1, 1, 1), colorSpace='rgb')
gentest_start_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('First gentest text done.')
elif response[-1]=='escape':
    controlled_e()

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
        pregen_seq = gstim.getPreGeneratedSequences(pregeneratedGenerationTask,grammar_type,cedrus_RB840,nbrOfStartKeys)
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
            pregen_seq = gstim.getPreGeneratedSequences(pregeneratedGenerationTask,grammar_type,cedrus_RB840,nbrOfStartKeys)
        else:
            pregen_seq = gstim.getPreGeneratedSequences(pregeneratedGenerationTask,'random',cedrus_RB840,nbrOfStartKeys)
            
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