#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 08:27:28 2023

@author: gdf724

Script for data collection and structuring. 

"""

#%% Import necessary libraries
import os 
import pandas as pd
from glob import glob
import Grammar_stimuli as gramstim
import numpy as np

#%% Help functions
def sortDynamic(listed):
    sortedList = [None]*len(listed)
    for itr in range(len(listed)):
        tmp = listed[itr]
        if tmp[-1]=='v':
            if tmp[-6].isnumeric():
                indx = int(tmp[-6:-4]) #Works for now but could be more versatile. 
            else:
                indx = int(tmp[-5:-4])
        else:
            indx = int(os.path.basename(tmp)[2:])
        sortedList[indx-1] = tmp
    
    return sortedList

def gethandshifts(trials):
    left = ['a', 'b', 'c'] 
    right = ['f', 'g', 'h']
    handshift = []
    skip = False
    for itr in range(len(trials)):
        if (skip) or (itr==0):
            handshift.append(-1)
            skip=False
        else:
            if trials[itr]=='pause':
                skip = True
            elif (left.count(trials[itr]) > 0) and (right.count(trials[itr-1]) > 0):
                handshift.append(1)
            elif (right.count(trials[itr]) > 0) and (left.count(trials[itr-1]) > 0):
                handshift.append(1)
            else:
                handshift.append(0)
                
    return handshift

def getGrammarScores(responses,seq,grammar,gr):
    grammarscores = []
    grammarscores.append(np.nan)
    for itr in range(1,len(responses)):
        if seq[itr-1]!=seq[itr]:
            grammarscores.append(np.nan)
        else:
            grammarscores.append(grammar[responses[itr]][responses[itr-1]])
    
    return grammarscores
            
            
#%% Define variables
datapath = '/Users/gdf724/Data/MovementGrammar/AGIL/'
output_path = '/Users/gdf724/Data/MovementGrammar/AGIL/'

subjlist = glob(os.path.join(datapath,'*'))
subjlist = sortDynamic([x for x in subjlist if len(x)>4 and x[-4]!='.'])

#This could potentially also be read from the settings text file. 
nbrOfDays = 3
nbrOfBlocks = 15
nbrOfSequences = 5 
nbrOfItems = 8


#%% SRTT
# Output: csv-file with subject, day, block, sequence_nbr, element_nbr, cue, RT, response, accuracy, handshift and potentially background measures.
# Named "learning"

seq_nbr_template = []
element_nbr_template = []

for seqitr in range(nbrOfSequences):
    for ittr in range(nbrOfItems):
        seq_nbr_template.append(seqitr+1)
        element_nbr_template.append(ittr+1)

subjcol = []
groupcol = []
daycol = []
blockcol = []
sequence_nbr_col = []
element_nbr_col = []
cue_col = []
RTcol = []
responsecol = []
accuracycol = []
handshiftcol = []

for subject in subjlist:
    subj = os.path.basename(subject)
    subj = subj.replace(" ","")
    
    learning_list = sorted(glob(os.path.join(subject,subj+'*_learning')))    
    for day_itr in range(len(learning_list)):
        block_list = sortDynamic(glob(os.path.join(learning_list[day_itr],'*_block_*.csv')))
        tmp = pd.read_table(os.path.join(learning_list[day_itr],'settings.txt'),sep=':')
        group = tmp.iloc[7,1]
        for block_itr in range(len(block_list)):
            block_data = pd.read_csv(os.path.join(block_list[block_itr]))
            handshiftcol.extend(gethandshifts(block_data['trial'].tolist()))
            block_data=block_data.drop(block_data[block_data['trial']=='pause'].index)
            subjcol.extend([subj]*len(seq_nbr_template))
            groupcol.extend([group]*len(seq_nbr_template))
            daycol.extend([day_itr+1]*len(seq_nbr_template))
            blockcol.extend([block_itr+1]*len(seq_nbr_template))
            sequence_nbr_col.extend(seq_nbr_template)
            element_nbr_col.extend(element_nbr_template)
            cue_col.extend(block_data['trial'].tolist())
            RTcol.extend(block_data['reaction_time'].tolist())
            responsecol.extend(block_data['response'].tolist())
            accuracycol.extend(block_data['accuracy'].tolist())
            
savedf = pd.DataFrame({'subject': subjcol,
                       'group': groupcol,
                       'day': daycol,
                       'block': blockcol,
                       'sequence': sequence_nbr_col,
                       'element': element_nbr_col,
                       'cue': cue_col,
                       'RT': RTcol,
                       'response': responsecol,
                       'accuracy': accuracycol,
                       'handshift': handshiftcol})
savedf.to_csv(os.path.join(output_path,'LearningSRTT_data.csv'), index=False)
        
#%% Sequence production
element_nbr_template = []

for seqitr in range(4):
    for ittr in range(nbrOfItems):
        element_nbr_template.append(ittr+1)

subjcol = []
group = []
conditioncol = []
sequence_nbr_col = []
element_nbr_col = []
gentimecol = []
responsecol = []
fixed = []
grammatical = []

for subject in subjlist:
    subj = os.path.basename(subject)
    subj = subj.replace(" ","")
    
    production_list = sorted(glob(os.path.join(subject,subj+'*_generation','*generation*')))    
    tmp = pd.read_table(os.path.join(os.path.dirname(production_list[0]),'settings.txt'),sep=':')
    group = tmp.iloc[2,1]
    grammar = gramstim.getGrammar(group, True)
    
    for prod_itr in range(len(production_list)):
        if production_list[prod_itr][-5] == 'l':
            gr = 'grammatical'
        elif production_list[prod_itr][-5] == 'm':
            gr = 'random'
            
        tmp_data = pd.read_csv(production_list[prod_itr])
        subjcol.extend([subj]*len(tmp_data))
        groupcol.extend([group]*len(tmp_data))
        conditioncol.extend([gr]*len(tmp_data))
        sequence_nbr_col.extend(tmp_data['sequence'].tolist())
        element_nbr_col.extend(element_nbr_template)
        gentimecol.extend(tmp_data['generation_time'].tolist())
        responsecol.extend(tmp_data['response'].tolist())
        fixed.extend(tmp_data['pregenerated'].tolist())
        grammatical.extend(getGrammarScores(tmp_data['response'].tolist(),tmp_data['sequence'].tolist(),grammar,gr))
            
savedf = pd.DataFrame({'subject': subjcol,
                       'group': groupcol,
                       'condition': conditioncol,
                       'sequence': sequence_nbr_col,
                       'element': element_nbr_col,
                       'cue': cue_col,
                       'generation_time': gentimecol,
                       'response': responsecol,
                       'pregenerated': fixed,
                       'grammaticality': grammatical})
savedf.to_csv(os.path.join(output_path,'SequenceProduction_data.csv'), index=False)

#%% Post SRTT
