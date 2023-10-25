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

def getTransProb(group,cuelist):
    grammar = gramstim.getGrammar(group, True)
    transprob = []
    transprob.append(np.nan)
    for itr in range(1,len(cuelist)):
        if cuelist[itr-1]=='pause':
            transprob.append(np.nan)
        elif cuelist[itr]!='pause':
            transprob.append(grammar[cuelist[itr]][cuelist[itr-1]])
            
    return transprob
        
            
            
#%% Define variables
datapath = '/Users/gdf724/Data/MovementGrammar/AGIL/'
output_path = '/Users/gdf724/Data/MovementGrammar/AGIL/'

subjlist = glob(os.path.join(datapath,'*'))
#subjlist = sortDynamic([x for x in subjlist if len(x)>4 and x[-4]!='.' and   x[-4]!='x'])

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
indx_template = []
indx_itr = 1

for seqitr in range(nbrOfSequences):
    for ittr in range(nbrOfItems):
        seq_nbr_template.append(seqitr+1)
        element_nbr_template.append(ittr+1)
        indx_template.append(indx_itr)
        indx_itr = indx_itr+1

subjcol = []
groupcol = []
daycol = []
blockcol = []
sequence_nbr_col = []
element_nbr_col = []
indx_col = []
cue_col = []
prob_col = []
prob_hilo_cue_col = []
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
            prob_col.extend(getTransProb(group,block_data['trial'].tolist()))
            prob_hilo_cue_col.extend(getTransProb('8020',block_data['trial'].tolist()))
            block_data=block_data.drop(block_data[block_data['trial']=='pause'].index)
            subjcol.extend([subj]*len(seq_nbr_template))
            groupcol.extend([group]*len(seq_nbr_template))
            daycol.extend([day_itr+1]*len(seq_nbr_template))
            blockcol.extend([block_itr+1]*len(seq_nbr_template))
            sequence_nbr_col.extend(seq_nbr_template)
            element_nbr_col.extend(element_nbr_template)
            indx_col.extend(indx_template)
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
                       'indx': indx_col,
                       'cue': cue_col,
                       'transprob': prob_col,
                       'hilo_transprob': prob_hilo_cue_col,
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
groupcol = []
conditioncol = []
sequence_nbr_col = []
element_nbr_col = []
gentimecol = []
responsecol = []
fixed = []
grammatical = []
hilo_grammatical = []
eq_grammatical = []
bin_grammatical = []

hilo_grammar = gramstim.getGrammar('8020', True)
eq_grammar = gramstim.getGrammar('5050', True)

for subject in subjlist:
    subj = os.path.basename(subject)
    subj = subj.replace(" ","")
    
    production_list = sorted(glob(os.path.join(subject,subj+'*_generation','*generation*')))
    if len(production_list) > 0:
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
            hilo_grammatical.extend(getGrammarScores(tmp_data['response'].tolist(),tmp_data['sequence'].tolist(),hilo_grammar,gr))
            eq_grammatical.extend(getGrammarScores(tmp_data['response'].tolist(),tmp_data['sequence'].tolist(),eq_grammar,gr))
            bin_grammatical.extend([1 if x>0 and not np.isnan(x) else 0 for x in getGrammarScores(tmp_data['response'].tolist(),tmp_data['sequence'].tolist(),grammar,gr)])
savedf = pd.DataFrame({'subject': subjcol,
                       'group': groupcol,
                       'condition': conditioncol,
                       'sequence': sequence_nbr_col,
                       'element': element_nbr_col,
                       'generation_time': gentimecol,
                       'response': responsecol,
                       'pregenerated': fixed,
                       'grammaticality': grammatical,
                       'hilo_grammaticality': hilo_grammatical,
                       'eq_grammaticality': eq_grammatical,
                       'bin_grammaticality': bin_grammatical})
savedf.to_csv(os.path.join(output_path,'SequenceProduction_data.csv'), index=False)

#%% Post SRTT
element_nbr_template = []
seq_nbr_template = []
for seqitr in range(5):
    for ittr in range(nbrOfItems):
        seq_nbr_template.append(seqitr+1)
        element_nbr_template.append(ittr+1)

subjcol = []
probcond = []
sequence_nbr_col = []
element_nbr_col = []
cue_col = []
prob_col = []
RTcol = []
responsecol = []
accuracycol = []
handshiftcol = []

for subject in subjlist:
    subj = os.path.basename(subject)
    subj = subj.replace(" ","")
    
    block_list = sorted(glob(os.path.join(subject,subj+'*_post','*block*')))  
    if len(block_list) > 0:
        tmp = pd.read_table(os.path.join(os.path.dirname(block_list[0]),'settings.txt'),sep=':')
        testorder_tmp = tmp.iloc[1,1]
        indx20 = testorder_tmp.find('20')
        indx80 = testorder_tmp.find('80')
        indxrnd = testorder_tmp.find('random')
        testorder=[]
        if indx20<indx80:
            testorder.append('20')
            if indx80<indxrnd:
                testorder.append('80')
                testorder.append('random')
            elif indxrnd<indx80:
                testorder.append('random')
                testorder.append('80')
            elif indxrnd<indx20:
                testorder.append('80')
                testorder.insert(0,'random')
        else:
            testorder.append('80')
            if indx20<indxrnd:
                testorder.append('20')
                testorder.append('random')
            elif indxrnd<indx20:
                testorder.append('random')
                testorder.append('20')
            elif indxrnd<indx80:
                testorder.append('20')
                testorder.insert(0,'random')
        
                
        
        for block_itr in range(len(block_list)):
            block_data = pd.read_csv(block_list[block_itr])
            if len(block_data)>45: #Quick fix. Check why this is
                block_data = block_data[1:]
                block_data = block_data.reset_index()
                
            handshiftcol.extend(gethandshifts(block_data['trial'].tolist()))
            prob_col.extend(getTransProb(group,block_data['trial'].tolist()))
            block_data=block_data.drop(block_data[block_data['trial']=='pause'].index,  )
            subjcol.extend([subj]*len(block_data))
            probcond.extend([testorder[block_itr]]*len(block_data))
            sequence_nbr_col.extend(seq_nbr_template)
            element_nbr_col.extend(element_nbr_template)
            cue_col.extend(block_data['trial'].tolist())
            RTcol.extend(block_data['reaction_time'].tolist())
            responsecol.extend(block_data['response'].tolist())
            accuracycol.extend(block_data['accuracy'].tolist())
            
savedf = pd.DataFrame({'subject': subjcol,
                       'transition_prob': probcond,
                       'sequence': sequence_nbr_col,
                       'element': element_nbr_col,
                       'cue': cue_col,
                       'transprob': prob_col,
                       'RT': RTcol,
                       'response': responsecol,
                       'accuracy': accuracycol,
                       'handshift': handshiftcol})
savedf.to_csv(os.path.join(output_path,'PostSRTT_data.csv'), index=False)
        