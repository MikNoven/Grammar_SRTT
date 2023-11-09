#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 14:56:22 2023
Script for generating behavioral parameters for SRTT task and characterizing 
the stimuli sequences. 
* Triplet frequency
* Hand shift frequency
* Starting finger (if relevant)
* Actual transitional distribution
* Distribution of ending cues
* Distribution of failed responses
@author: gdf724
"""
#%% Import packages
import os
import pandas as pd
import csv
import glob
import itertools
import Grammar_stimuli as gstim
from numpy import nan

#%% Get all available triplets.
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

#%% Update frequency table
def updateTripletFrequencies(seq,freq_table):
    for seq_itr in range(6):
        tmp_triplet = seq[seq_itr]+seq[seq_itr+1]+seq[seq_itr+2]
        freq_table[tmp_triplet]+=1
    return freq_table

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
    
    sessions = glob.glob(os.path.join(datapath, subj, subj+'*'+'_learning')) #For now assume all are in one session or that the number changes.
    for session in sessions:
        #%% Read the data and settings
        block = []
        trial = []
        RT = []
        response = []
        accuracy = []
        sequence = []
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
        
        for file in filelist:
            sequence_itr = 1
            #with open(os.path.join(session,subj+'_block_'+str(block_itr+1)+'.csv'),'r') as datafile:
            with open(file,'r') as datafile:
                if file[-6]=='_':
                    block_nbr=int(file[-5])
                else:
                    block_nbr=int(file[-6:-4])
                reader = csv.reader(datafile)
                for row in reader:
                    if row[1] == 'pause':
                        sequence_itr = sequence_itr + 1
                    elif row[1] != 'trial':
                        block.append(block_nbr)
                        sequence.append(sequence_itr)
                        trial.append(row[1])
                        RT.append(float(row[2]))
                        response.append(row[3]) 
                        accuracy.append(float(row[4]))
            
        #%% Loop through and calculate parameters
        hand_shift = []
        starting_finger = []
        last_cue = []
        sequence_position = []
        cummulative_probability_prompted = [] #A measure of "grammaticality" of sequence.
        cummulative_probability_response = [] #A measure of "grammaticality" of sequence.
        correctness_wrong_response = [] #The probability of the incorrect response, given the grammar.
        cue_trans_prob = [] #Save the transitional probability for each transition.
        response_prob = [] #If it could was the other correct response given the grammar.
        
        tmp_sequence = 0
        seq_indx = 0
        sequence_counter = 0
        
        triplet_frequencies_prompted = getTriplets(allowed_keys,True)
        triplet_frequencies_response = getTriplets(allowed_keys,False)
        
        #The actual transitional distribution
        trial_matrix = pd.DataFrame([[0]*len(allowed_keys) for x in range(len(allowed_keys))], columns=allowed_keys, index=allowed_keys)
        #The responses grouped after what the previous cue was. 
        response_matrix_prompt = pd.DataFrame([[0]*len(allowed_keys) for x in range(len(allowed_keys))], columns=allowed_keys, index=allowed_keys)
        #The responses grouped after what the previous response was.
        response_matrix_response = pd.DataFrame([[0]*len(allowed_keys) for x in range(len(allowed_keys))], columns=allowed_keys, index=allowed_keys)
        #Column is what it should have been, row what it was. df[column][row]
        wrong_response_matrix = pd.DataFrame([[0]*len(allowed_keys) for x in range(len(allowed_keys))], columns=allowed_keys, index=allowed_keys)
        
        for itr in range(len(RT)):
            if sequence[itr] != tmp_sequence:
                hand_shift.append(nan)
                starting_finger.append(trial[itr])
                tmp_sequence = sequence[itr]
                seq_indx = itr
                sequence_counter = 1
                cue_trans_prob.append(1/len(start_keys))
                if response[itr] in start_keys:
                    response_prob.append(1/len(start_keys))
                else:
                    response_prob.append(0)
            else:
                hand_shift.append(int(handShifted(trial[itr-1],trial[itr],allowed_keys)))
                sequence_counter += 1
                if sequence_counter == sequence_lengths:
                    last_cue.append(trial[itr])
                    triplet_frequencies_prompted = updateTripletFrequencies(trial[seq_indx:itr+1],triplet_frequencies_prompted)
                    triplet_frequencies_response = updateTripletFrequencies(response[seq_indx:itr+1],triplet_frequencies_response)
                    cummulative_probability_prompted.append(gstim.calcGramScore_seq(trial[seq_indx:itr+1], grammar))
                    cummulative_probability_response.append(gstim.calcGramScore_seq(response[seq_indx:itr+1], grammar))
            if accuracy[itr] == 0:
                wrong_response_matrix[trial[itr]][response[itr]]+=1
            if itr > seq_indx:
                response_prob.append(grammar[response[itr]][trial[itr-1]])
                response_matrix_prompt[response[itr]][trial[itr-1]]+=1
                cue_trans_prob.append(grammar[trial[itr]][trial[itr-1]])
                response_matrix_response[response[itr]][response[itr-1]]+=1
                trial_matrix[trial[itr]][trial[itr-1]]+=1
                if accuracy[itr] == 0:
                    correctness_wrong_response.append(grammar[response[itr]][trial[itr-1]])
            sequence_position.append(sequence_counter)
            
            
        #Make it frequencies by calculating the number of possible triplets and dividing each element by that. 
        nbrOfPossibleTriplets = 6*sequence[-1]*block[-1]
        triplet_frequencies_prompted = {k: v / nbrOfPossibleTriplets for k, v in triplet_frequencies_prompted.items()}
        triplet_frequencies_response = {k: v / nbrOfPossibleTriplets for k, v in triplet_frequencies_response.items()}
        
        #Make it into probabilities by dividing with total number of transitions.
        trial_probabilities=trial_matrix/trial_matrix.to_numpy().sum()
        response_probabilities_prompt=response_matrix_prompt/response_matrix_prompt.to_numpy().sum()
        response_probabilities_response=response_matrix_response/response_matrix_response.to_numpy().sum()
    
        #%% Save the data
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        sesstime = os.path.basename(os.path.normpath(session))
        sesstime = sesstime.replace(subj+'_','')
        sess_save_path = os.path.join(save_path,sesstime)
        if not os.path.exists(sess_save_path):
            os.makedirs(sess_save_path)
        
        #Save matrices
        trial_matrix.to_csv(os.path.join(sess_save_path,'SRTT_stimulus_frequency.csv'))
        wrong_response_matrix.to_csv(os.path.join(sess_save_path,'SRTT_wrong_frequency.csv'))
        response_matrix_prompt.to_csv(os.path.join(sess_save_path,'SRTT_cue_response_frequency.csv'))
        response_matrix_response.to_csv(os.path.join(sess_save_path,'SRTT_response_response_frequency.csv'))
        
        #Save triplet frequencies
        triplet_freq_prompt_names = [x[0] for x in triplet_frequencies_prompted.items()]
        triplet_freq_prompt_freq = [x[1] for x in triplet_frequencies_prompted.items()]
        triplet_freq_prompt_df = pd.DataFrame(list(map(list, zip(*[triplet_freq_prompt_names,triplet_freq_prompt_freq]))), columns=['triplet', 'triplet_frequency'])
        triplet_freq_prompt_df.to_csv(os.path.join(sess_save_path,'SRTT_cue_triplet_frequencies.csv'), index = False)
        
        triplet_freq_resp_names = [x[0] for x in triplet_frequencies_response.items()]
        triplet_freq_resp_freq = [x[1] for x in triplet_frequencies_response.items()]
        triplet_freq_resp_df = pd.DataFrame(list(map(list, zip(*[triplet_freq_resp_names,triplet_freq_resp_freq]))), columns=['triplet', 'triplet_frequency'])
        triplet_freq_resp_df.to_csv(os.path.join(sess_save_path,'SRTT_response_triplet_frequencies.csv'), index = False)
        
        #Save sequence-level data
        block_set = set(block)
        seq_set = set(sequence)
        block_seq = []
        seq_seq = []
        
        for blocknbr in block_set:
            for seqnbr in seq_set:
                block_seq.append(blocknbr)
                seq_seq.append(seqnbr)
        seq_info_df = pd.DataFrame(list(map(list, zip(*[block_seq,seq_seq,cummulative_probability_prompted,cummulative_probability_response,starting_finger,last_cue]))),columns = ['block', 'sequence', 'cummulative_probability_cue', 'cummulative_probability_response', 'start_cue', 'last_cue'])
        seq_info_df.to_csv(os.path.join(sess_save_path,'SRTT_sequence_info.csv'), index = False)
        
        alltrial_df = pd.DataFrame(list(map(list, zip(*[block,sequence,sequence_position,trial,response,accuracy,response_prob,RT,cue_trans_prob,hand_shift]))), columns = ['block', 'sequence', 'sequence_position', 'correct', 'response', 'accuracy', 'response_prob', 'RT', 'cue_probability', 'hand_shift'])
        alltrial_df.to_csv(os.path.join(sess_save_path,'SRTT_alltrial_info.csv'), index = False)
    
                        

                        
                        