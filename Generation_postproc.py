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
subj = 'HenrikC1'
allowed_keys = ['a', 'b', 'c', 'f', 'g', 'h']
starting_keys = ['c']
grammar_type = '8020' #or '5050'
sequence_lengths = 8 #Number of elements in generated sequences. 

save_path = os.path.join(datapath,'PostProcessing',subj)

grammar = gstim.getGrammar(grammar_type)

#%% Grammatical sequences
#Load data
session = glob.glob(os.path.join(datapath, subj+'*'+'_generation')) #For now assume all are in one session or that the number changes.
session = session[0]

sequence_g = []
genTime_g = []
response_g = []
pregenerated_g = []
with open(os.path.join(session,subj+'_generation_grammatical.csv'),'r') as datafile:
    reader = csv.reader(datafile)
    for row in reader:
        if row[1] != 'sequence':
            sequence_g.append(int(row[1]))
            genTime_g.append(float(row[2]))
            response_g.append(row[3])
            if len(row)>4:
                pregenerated_g.append(row[4])

#Calculate parameters
cummulative_probability_g = []
trans_probs_g = []            
hand_shift_g = [] 
correct_shift_previous_g = [] #1 if true that the response would have been a possible response to the previous.
correct_shift_current_g = []
correct_pos_previous_g = [] #1 if true that the response would have been a possible response to the previous.
correct_pos_current_g = []
correct_pos_subsequent_g = []

allowed_pos = [['c'],['b', 'g'],['a', 'f'],['c', 'h'],['b', 'g'],['a', 'f'],['c', 'h'],['b', 'g']]

triplet_frequencies_generated_g = getTriplets(allowed_keys,False)

for seq in set(sequence_g):
    hand_shift_g.append(nan)
    seq_indices = [i for i, x in enumerate(sequence_g) if x == seq]
    cummulative_probability_g.append(gstim.calcGramScore_seq(response_g[seq_indices[0]:seq_indices[-1]+1], grammar))
    triplet_frequencies_generated_g = updateTripletFrequencies(response_g[seq_indices[0]:seq_indices[-1]+1],triplet_frequencies_generated_g)
    if response_g[seq_indices[0]] in starting_keys:
        trans_probs_g.append(1.0)    
        correct_pos_current_g.append(1)
        correct_shift_current_g.append(1)
    else: 
        trans_probs_g.append(0.0)
        correct_pos_current_g.append(0)
        correct_shift_current_g.append(0)
    correct_pos_previous_g.append(nan)
    correct_shift_previous_g.append(nan)
    correct_pos_subsequent_g.append(int(response_g[seq_indices[0]] in allowed_pos[1]))
    pos_itr = 1
    for seq_itr in seq_indices[1:]:
        trans_probs_g.append(grammar[response_g[seq_itr-1]][response_g[seq_itr-1]])
        correct_shift_current_g.append(int(trans_probs_g[-1]>0))
        hand_shift_g.append(int(handShifted(response_g[seq_itr-1],response_g[seq_itr],allowed_keys)))
        
        if pos_itr == 1:
            correct_shift_previous_g.append(int(response_g[seq_itr] in starting_keys))
        else:
            correct_shift_previous_g.append(int(grammar[response_g[seq_itr]][response_g[seq_itr-2]]))
        correct_pos_previous_g.append(int(response_g[seq_itr] in allowed_pos[pos_itr-1]))
        correct_pos_current_g.append(int(response_g[seq_itr] in allowed_pos[pos_itr]))
        if pos_itr < sequence_lengths-1:
            correct_pos_subsequent_g.append(int(response_g[seq_itr] in allowed_pos[pos_itr+1]))
        else:
            correct_pos_subsequent_g.append(nan)
        pos_itr += 1
        
nbrOfPossibleTriplets = 6*seq
triplet_frequencies_generated_g = {k: v / nbrOfPossibleTriplets for k, v in triplet_frequencies_generated_g.items()}

#%% Ungrammatical sequences
#Load data

sequence_u = []
genTime_u = []
response_u = []
pregenerated_u = []
with open(os.path.join(session,subj+'_generation_random.csv'),'r') as datafile:
    reader = csv.reader(datafile)
    for row in reader:
        if row[1] != 'sequence':
            sequence_u.append(int(row[1]))
            genTime_u.append(float(row[2]))
            response_u.append(row[3])
            if len(row)>4:
                pregenerated_u.append(row[4])

#Calculate parameters
cummulative_probability_u = []
trans_probs_u = []            
hand_shift_u = [] 
correct_shift_previous_u = [] #1 if true that the response would have been a possible response to the previous.
correct_shift_current_u = []
correct_pos_previous_u = [] #1 if true that the response would have been a possible response to the previous.
correct_pos_current_u = []
correct_pos_subsequent_u = []

triplet_frequencies_generated_u = getTriplets(allowed_keys,False)

for seq in set(sequence_u):
    hand_shift_u.append(nan)
    seq_indices = [i for i, x in enumerate(sequence_u) if x == seq]
    cummulative_probability_u.append(gstim.calcGramScore_seq(response_u[seq_indices[0]:seq_indices[-1]+1], grammar))
    triplet_frequencies_generated_u = updateTripletFrequencies(response_u[seq_indices[0]:seq_indices[-1]+1],triplet_frequencies_generated_u)
    if response_u[seq_indices[0]] in starting_keys:
        trans_probs_u.append(1.0)    
        correct_pos_current_u.append(1)
        correct_shift_current_u.append(1)
    else: 
        trans_probs_u.append(0.0)
        correct_pos_current_u.append(0)
        correct_shift_current_u.append(0)
    correct_pos_previous_u.append(nan)
    correct_shift_previous_u.append(nan)
    correct_pos_subsequent_u.append(int(response_u[seq_indices[0]] in allowed_pos[1]))
    pos_itr = 1
    for seq_itr in seq_indices[1:]:
        trans_probs_u.append(grammar[response_u[seq_itr-1]][response_u[seq_itr-1]])
        correct_shift_current_u.append(int(trans_probs_u[-1]>0))
        hand_shift_u.append(int(handShifted(response_u[seq_itr-1],response_u[seq_itr],allowed_keys)))
        
        if pos_itr == 1:
            correct_shift_previous_u.append(int(response_u[seq_itr] in starting_keys))
        else:
            correct_shift_previous_u.append(int(grammar[response_u[seq_itr]][response_u[seq_itr-2]]))
        correct_pos_previous_u.append(int(response_u[seq_itr] in allowed_pos[pos_itr-1]))
        correct_pos_current_u.append(int(response_u[seq_itr] in allowed_pos[pos_itr]))
        if pos_itr < sequence_lengths-1:
            correct_pos_subsequent_u.append(int(response_u[seq_itr] in allowed_pos[pos_itr+1]))
        else:
            correct_pos_subsequent_u.append(nan)
        pos_itr += 1
        
triplet_frequencies_generated_u = {k: v / nbrOfPossibleTriplets for k, v in triplet_frequencies_generated_u.items()}

#%% Save the data
if not os.path.exists(save_path):
    os.makedirs(save_path)
sesstime = os.path.basename(os.path.normpath(session))
sesstime = sesstime.replace(subj+'_','')
sess_save_path = os.path.join(save_path,sesstime)
if not os.path.exists(sess_save_path):
    os.makedirs(sess_save_path)

#Save sequence-level information
sequences = list(set(sequence_g))
cum_prob_df = pd.DataFrame(list(map(list, zip(*[sequences,cummulative_probability_g,cummulative_probability_u]))), columns=['sequence', 'cummulative_probability_grammatical', 'cummulative_probability_ungrammatical'])
cum_prob_df.to_csv(os.path.join(sess_save_path,'generated_sequences_cummulative_probabilities.csv'), index = False)

#Save triplet frequencies
triplet_names = [x[0] for x in triplet_frequencies_generated_g.items()]
triplet_freq_g = [x[1] for x in triplet_frequencies_generated_g.items()]
triplet_freq_u = [x[1] for x in triplet_frequencies_generated_u.items()]
triplet_freq_df = pd.DataFrame(list(map(list, zip(*[triplet_names,triplet_freq_g,triplet_freq_u]))), columns=['triplet', 'triplet_frequency_grammatical', 'triplet_frequency_ungrammatical'])
triplet_freq_df.to_csv(os.path.join(sess_save_path,'generated_sequences_triplet_frequencies.csv'), index = False)

#Info for all sequences
if len(pregenerated_g)==0:
    seq_info_df = pd.DataFrame(list(map(list, zip(*[sequence_g,response_g,response_u,genTime_g,genTime_u,correct_pos_current_g,correct_pos_current_u,correct_pos_previous_g,correct_pos_previous_u,correct_pos_subsequent_g,correct_pos_subsequent_u,correct_shift_current_g,correct_shift_current_u,correct_shift_previous_g,correct_shift_previous_u,hand_shift_g,hand_shift_u]))),columns = ['sequence','generated_sequence_grammatical','generated_sequence_ungrammatical','generation_time_grammatical','generation_time_ungrammatical','position_current_grammatical','position_current_ungrammatical','position_previous_grammatical','position_previous_ungrammatical','position_subsequent_grammatical','position_subsequent_ungrammatical','shift_current_grammatical','shift_current_ungrammatical','shift_previous_grammatical','shift_previous_ungrammatical','hand_shift_grammatical','hand_shift_ungrammatical'])
else:
    seq_info_df = pd.DataFrame(list(map(list, zip(*[sequence_g,pregenerated_g,response_g,response_u,genTime_g,genTime_u,correct_pos_current_g,correct_pos_current_u,correct_pos_previous_g,correct_pos_previous_u,correct_pos_subsequent_g,correct_pos_subsequent_u,correct_shift_current_g,correct_shift_current_u,correct_shift_previous_g,correct_shift_previous_u,hand_shift_g,hand_shift_u]))),columns = ['sequence','pregenerated','generated_sequence_grammatical','generated_sequence_ungrammatical','generation_time_grammatical','generation_time_ungrammatical','position_current_grammatical','position_current_ungrammatical','position_previous_grammatical','position_previous_ungrammatical','position_subsequent_grammatical','position_subsequent_ungrammatical','shift_current_grammatical','shift_current_ungrammatical','shift_previous_grammatical','shift_previous_ungrammatical','hand_shift_grammatical','hand_shift_ungrammatical'])

seq_info_df.to_csv(os.path.join(sess_save_path,'generated_sequences_sequence_info.csv'))