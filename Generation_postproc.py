#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 15:34:47 2023
Generation task postprocessing. 
* Cummulative probability of sequence based on simple transitions
* Probability of each sequence element given the sequence position
(First would indicate transitional probability learning, second that the whole system is learnt.)
* Would the input be correct for previous or next position?
* Triplet frequencies
* Hand shifts
@author: gdf724
"""
#%% Import relevant packages
import os
import csv
import glob
import Grammar_stimuli as gstim
import itertools
import pandas as pd
from numpy import nan

#%% Helper functions
def handShifted(prev,curr,allowed_keys):
    if allowed_keys[0]=='a':
        left_keys = ['a', 'b', 'c']
    else:
        left_keys = ['s', 'd', 'f']
    
    if prev in left_keys:
        return curr not in left_keys
    else:
        return curr in left_keys

def getTriplets(cue_positions, clean):
    #Order matters
    init_combinations=[]
    for com in itertools.combinations_with_replacement(cue_positions,3):
        init_combinations.append(com[0]+com[1]+com[2])
    
    if clean:
        #Clean from repeats.
        clean_combinations = []
        for combination in init_combinations:
            if combination[0]!=combination[1] and combination[1]!=combination[2]:
                for perm in itertools.permutations(combination,3):
                    clean_combinations.append(perm[0]+perm[1]+perm[2])
        return dict.fromkeys(clean_combinations,0)
    else:
        combinations = []
        for combination in init_combinations:
            for perm in itertools.permutations(combination,3):
                combinations.append(perm[0]+perm[1]+perm[2])
        return dict.fromkeys(combinations,0)

def updateTripletFrequencies(seq,freq_table):
    for seq_itr in range(6):
        tmp_triplet = seq[seq_itr]+seq[seq_itr+1]+seq[seq_itr+2]
        freq_table[tmp_triplet]+=1
    return freq_table

#%% Settings and paths
datapath='/Users/gdf724/Data/MovementGrammar/GrammarSRTT/'
#subj = 'HansC1'
list_of_subjs = ['ID13','ID14','ID15']

for subj in list_of_subjs:
    save_path = os.path.join(datapath,'PostProcessing',subj)

    #%% Read the data and settings

    sequence = []
    generation_time = []
    response = []
    pregenerated = []
    condition = []
    gramcorr = []
    gramscore = []
    hand_shift = []
    #trial,reaction_time,response,accuracy
    sesslist = glob.glob(os.path.join(datapath,subj,'*_generation/'))
    session = sesslist[0]
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
    
    grammaticality_list = ['grammatical', 'random']
            
    for gram in grammaticality_list:
        file = os.path.join(session,subj+'T3_generation_'+gram+'.csv')
        data = pd.read_csv(file)
        for itr in range(len(data['sequence'])):
            sequence.append(data['sequence'][itr])
            generation_time.append(data['generation_time'][itr])
            response.append(data['response'][itr])
            pregenerated.append(data['pregenerated'][itr])
            condition.append(gram)
            if itr==0 or data['sequence'][itr]!=data['sequence'][itr-1]:
                gramcorr.append(nan)
                gramscore.append(nan)
                hand_shift.append(nan)
            else:
                gramcorr.append(int(grammar[data['response'][itr]][data['response'][itr-1]]>0))
                gramscore.append(grammar[data['response'][itr]][data['response'][itr-1]])
                hand_shift.append(int(handShifted(data['response'][itr-1], data['response'][itr], allowed_keys)))
                
        

    #%% Save the data
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    alltrial_df = pd.DataFrame(list(map(list, zip(*[sequence,response,pregenerated,condition,gramcorr,gramscore,hand_shift]))), columns = ['sequence','response','pregenerated','condition','gramcorr','gramscore','hand_shift'])
    alltrial_df.to_csv(os.path.join(save_path,'Generation_alltrial_info.csv'), index = False)

                    