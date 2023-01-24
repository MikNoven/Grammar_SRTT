#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:39:39 2023
Script for generating stimlus sequences for Grammar SRTT.
@author: gdf724
"""
#%% Import packages.
import random
import numpy as np
import pandas as pd
import itertools
import os

#%% Global variables
cue_positions = ['s', 'd', 'f', 'j', 'k', 'l']

#%% Random Sequences
def getRandomSequences(lengthOfSequences,sequencesPerBlock):
    block_stim = []
    block_stim.append(cue_positions[random.randrange(0,len(cue_positions)-1)])
    for itr in range(lengthOfSequences*sequencesPerBlock-1):
        tmp=cue_positions[:]
        tmp.remove(block_stim[-1]) #Making sure there are no simple repeats.
        block_stim.append(tmp[random.randrange(0,len(cue_positions)-1)])
    
    return block_stim


#%% Grammars
def getGrammar(grammar_type):
    if grammar_type == '8020':
        trans_s = [0,0,0.8,0,0,0.2]
        trans_d = [0.2,0,0,0.8,0,0]
        trans_f = [0,0.8,0,0,0.2,0]
        trans_j = [0,0,0.2,0,0,0.8]
        trans_k = [0.8,0,0,0.2,0,0]
        trans_l = [0,0.2,0,0,0.8,0]
    elif grammar_type == '5050':
        trans_s = [0,0,0.5,0,0,0.5]
        trans_d = [0.5,0,0,0.5,0,0]
        trans_f = [0,0.5,0,0,0.5,0]
        trans_j = [0,0,0.5,0,0,0.5]
        trans_k = [0.5,0,0,0.5,0,0]
        trans_l = [0,0.5,0,0,0.5,0]
    
    adjacency_matrix = []
    adjacency_matrix.append(trans_s)
    adjacency_matrix.append(trans_d)
    adjacency_matrix.append(trans_f)
    adjacency_matrix.append(trans_j)
    adjacency_matrix.append(trans_k)
    adjacency_matrix.append(trans_l)
    adjacency_matrix = np.array(adjacency_matrix)

    grammar = pd.DataFrame(adjacency_matrix, columns=cue_positions, index=cue_positions)
    
    return grammar

#%% Get all available triplets.
def getTriplets():
    #Order matters
    combinations=[]
    for com in itertools.combinations_with_replacement(cue_positions,3):
        combinations.append(com)
    
    #Clean from repeats.
    clean_combinations = []
    for combination in combinations:
        if combination[0]!=combination[1] and combination[1]!=combination[2]:
            for perm in itertools.permutations(combination,3):
                clean_combinations.append(perm)
           
    #Possibly just save and load. 
    return clean_combinations
    
#%% Calculate grammaticality scores
def calcGramScore(block_stim,grammar):
    gramScore= []
    score = 0
    for stim_itr in range(1,len(block_stim)):
        stim = block_stim[stim_itr]
        if stim=='pause':
            gramScore.append(score)
            score = 0
        elif block_stim[stim_itr-1]!='pause':
            score = score + grammar[stim][block_stim[stim_itr-1]]
            
    return gramScore

    
#%% Define and print figure of grammar
def characterize_grammar_block(block_stim,grammar,grammar_type,save_path,block_nbr,subject):
    #Grammaticality of sequences
    grammaticality_scores = calcGramScore(block_stim,grammar) #To save the cumalitive sum of probabilities of the sequence. 
    #Triplet frequency
    triplets = getTriplets()
    triplet_freq = np.zeros(len(triplets))
    #Transitional properties
    adjacency_matrix = []
    for itr in range(len(grammar)):
        adjacency_matrix.append([0]*len(grammar))

    adjacency_matrix = np.array(adjacency_matrix)
    trans_prob = pd.DataFrame(adjacency_matrix, columns=cue_positions, index=cue_positions)
    trans_dn = 0
    trip_dn = 0
    
    for stim_itr in range(1,len(block_stim)):
        stim = block_stim[stim_itr]
        if stim!='pause' and block_stim[stim_itr-1]!='pause':
            trans_prob[stim][block_stim[stim_itr-1]] = trans_prob[stim][block_stim[stim_itr-1]] + 1
            trans_dn = trans_dn + 1
            if stim_itr > 2 and block_stim[stim_itr-2]!='pause':
                triplet_freq[triplets.index((block_stim[stim_itr-2],block_stim[stim_itr-1],stim))] = triplet_freq[triplets.index((block_stim[stim_itr-2],block_stim[stim_itr-1],stim))] + 1
                trip_dn = trip_dn + 1
    
    save_pkl = pd.DataFrame()
    save_pkl['grammaticality'] =  [grammaticality_scores]
    save_pkl['adjacency_matrix'] =  [trans_prob/trans_dn]
    save_pkl['triplets'] =  [triplets]
    save_pkl['triplet_probability'] =  [triplet_freq/trip_dn] 
    save_pkl.to_pickle(os.path.join(save_path,subject+'_block_'+str(block_nbr)+'.pkl'))


#%% Grammar Sequencs
"""
Code for generating SRTT sequences with 6 visual cue positions corresponding to 
index, middle, or ring finger on either hand according to below:
    s=left ring finger
    d=left middle finger
    f=left index finger
    j=right index finger
    k=right middle finger
    l=right ring finger
grammar_type is either '8020' or '5050'.
"""
def getGrammarSequences(lengthOfSequences,sequencesPerBlock,grammar_type,characterize_block,save_path,block_nbr,subject):
    block_stim = []
    grammar = getGrammar(grammar_type)
    
    for seq_itr in range(sequencesPerBlock):
        prev_element = 'f'
        block_stim.append(prev_element)
        for stim_itr in range(lengthOfSequences-1):
            tmp_choice = random.choices(cue_positions, weights=grammar.iloc[cue_positions.index(prev_element)])[0]
            block_stim.append(tmp_choice)
            prev_element = tmp_choice
        block_stim.append('pause')
    
    if characterize_block:
        characterize_grammar_block(block_stim,grammar,grammar_type,save_path,block_nbr,subject)
    
    return block_stim
        
    
    