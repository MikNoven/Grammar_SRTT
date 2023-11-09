#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 15:57:48 2023
Script for postprocessing the Posttest SRTT. 
@author: gdf724
"""

#%% Import packages
import os
import pandas as pd
import glob
import Grammar_stimuli as gstim
from numpy import nan
import numpy as np

#%% determine hand shift
def handShifted(prev,curr,allowed_keys):
    if allowed_keys[0]=='a':
        left_keys = ['a', 'b', 'c']
    else:
        left_keys = ['s', 'd', 'f']
    
    if prev in left_keys:
        return curr not in left_keys
    else:
        return curr in left_keys

#%% Get sorted filelist
def getBlockFilelist(session,subj):
    tmp_filelist = glob.glob(os.path.join(session,'*_block_*.csv'))
    filelist = ['']*len(tmp_filelist)
    for file in tmp_filelist:
        block_nbr=int(file[file.index('block_')+6:file.index('.csv')])
        filelist[block_nbr-1] = file
    
    return filelist

#%% Define paths and settings
datapath='/Users/gdf724/Data/MovementGrammar/GrammarSRTT/'
#subj = 'HansC1'
list_of_subjs = ['ID13','ID14','ID15']

for subj in list_of_subjs:
    save_path = os.path.join(datapath,'PostProcessing',subj)
    
    sessions = glob.glob(os.path.join(datapath, subj, subj+'*'+'_post')) #For now assume all are in one session or that the number changes.
    session = sessions[0]
    #%% Read the data and settings
    block = []
    trial = []
    RT = []
    response = []
    accuracy = []
    sequence = []
    sequence_type = []
    response_prob = []
    cue_trans_prob = []
    hand_shift = []
    #trial,reaction_time,response,accuracy
    
    
    with open(os.path.join(session,'settings.txt'),'r') as settingsfile:
        lines = settingsfile.readlines()
    
    for line in lines:
        tmp_str = line[0:line.index(':')]
        tmp_answ = line[line.index(':')+1:-1]
        if tmp_str=='cedrus_RB840':
            if tmp_answ=='True':
                cedrus_RB840=True
                allowed_keys = ['a', 'b', 'c', 'f', 'g', 'h']
            else:
                cedrus_RB840=False
                allowed_keys = ['s', 'd', 'f', 'j', 'k', 'l']
        if tmp_str=='lengthOfSequences':
            sequence_lengths = int(tmp_answ)
        if tmp_str=='grammar_type':
            grammar_type = tmp_answ
        if tmp_str=='grammar_version':
            grammar_version = tmp_answ
        if tmp_str=='nbrOfStartKeys':
            nbrOfStartKeys=int(tmp_answ)
            
    grammar = gstim.getGrammar(grammar_type,cedrus_RB840,grammar_version)
    start_keys = allowed_keys[2:2+nbrOfStartKeys]
        
    filelist = getBlockFilelist(session,subj)
    
    for file_itr in range(len(filelist)):
        file = filelist[file_itr]
        data = pd.read_csv(file)
        
        block.extend([file_itr+1]*len(data['trial']))
        trial.extend(data['trial'].to_list())
        RT.extend(data['reaction_time'].to_list())
        response.extend(data['response'].to_list())
        accuracy.extend(data['accuracy'].to_list())
        seq_itr = 1
        for itr in range(len(data['trial'])):
            if data['trial'][itr] == 'pause':
                seq_itr = itr + 1
                sequence.append(nan)
                response_prob.append(nan)
                cue_trans_prob.append(nan)
                hand_shift.append(nan)
            elif itr > 0 and data['trial'][itr-1] == 'pause':
                sequence.append(seq_itr)
                response_prob.append(nan)
                cue_trans_prob.append(nan)
                hand_shift.append(nan)     
            else:
                sequence.append(seq_itr)
                if itr == 0:
                    response_prob.append(nan)
                    cue_trans_prob.append(nan)
                    hand_shift.append(nan)
                else:
                    response_prob.append(grammar[data['response'][itr]][data['response'][itr-1]])
                    cue_trans_prob.append(grammar[data['trial'][itr]][data['trial'][itr-1]])
                    hand_shift.append(handShifted(data['trial'][itr-1], data['trial'][itr], allowed_keys))
                
        if 'sequence_type' in data:
            sequence_type.extend(data['sequence_type'].to_list())
        else:
            if(np.nanmean(cue_trans_prob[-len(data['trial']):])>=0.5):
                sequence_type.extend(['grammatical']*len(data['trial']))
            else:
                sequence_type.extend(['random']*len(data['trial']))

        

    #%% Save the data
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    alltrial_df = pd.DataFrame(list(map(list, zip(*[block,sequence,sequence_type,trial,response,accuracy,response_prob,RT,cue_trans_prob,hand_shift]))), columns = ['block', 'sequence', 'sequence_type', 'correct', 'response', 'accuracy', 'response_prob', 'RT', 'cue_probability', 'hand_shift'])
    alltrial_df.to_csv(os.path.join(save_path,'Post_SRTT_alltrial_info.csv'), index = False)

           