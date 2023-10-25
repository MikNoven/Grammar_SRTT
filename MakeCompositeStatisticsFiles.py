#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 11:15:00 2023
Script for collecting data from all participants.
@author: gdf724
"""

import os 
import glob
import pandas as pd

#%% Define variables
datapath = '/Users/gdf724/Data/MovementGrammar/AGIL/PostProcessing/'
output_path = '/Users/gdf724/Data/MovementGrammar/AGIL/'
bg_data = pd.read_csv('/Users/gdf724/Data/MovementGrammar/AGIL/Background.csv')
subjlist = glob.glob(os.path.join(datapath,'*'))
#subjlist = sortDynamic([x for x in subjlist if len(x)>4 and x[-4]!='.' and   x[-4]!='x'])

#This could potentially also be read from the settings text file. 
nbrOfDays = 3
nbrOfBlocks = 15
nbrOfSequences = 5 
nbrOfItems = 8
template_nbr = nbrOfBlocks*nbrOfSequences*nbrOfItems

indx_template = []
indx_itr = 1
for blockitr in range(nbrOfBlocks):
    for seqitr in range(nbrOfSequences):
        for ittr in range(nbrOfItems):
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
prob_response_col = []
prob_cue_col = []
prob_hilo_cue_col = []
RTcol = []
responsecol = []
accuracycol = []
handshiftcol = []

for subj in subjlist:
    
    subject = os.path.basename(subj)
    group = bg_data['group'][bg_data['subject']==subject].to_string(index=False)
    sessions = sorted(glob.glob(os.path.join(subj,'*'+'_learning/'))) #For now assume all are in one session or that the number changes.
    for day_itr in range(len(sessions)):
        session = sessions[day_itr]
        tmp = pd.read_csv(os.path.join(session,'SRTT_alltrial_info.csv'))
        handshiftcol.extend(tmp['hand_shift'])
        prob_response_col.extend(tmp['response_prob'])
        prob_cue_col.extend(tmp['cue_probability'])
        subjcol.extend([subject]*template_nbr)
        groupcol.extend([group]*template_nbr)
        daycol.extend([day_itr+1]*template_nbr)
        blockcol.extend(tmp['block'])
        sequence_nbr_col.extend(tmp['sequence'])
        element_nbr_col.extend(tmp['sequence_position'])
        indx_col.extend(indx_template)
        cue_col.extend(tmp['correct'])
        RTcol.extend(tmp['RT'])
        responsecol.extend(tmp['response'])
        accuracycol.extend(tmp['accuracy'])
            
savedf = pd.DataFrame({'subject': subjcol,
                       'group': groupcol,
                       'day': daycol,
                       'block': blockcol,
                       'sequence': sequence_nbr_col,
                       'element': element_nbr_col,
                       'indx': indx_col,
                       'cue': cue_col,
                       'response_prob': prob_response_col,
                       'cue_prob': prob_cue_col,
                       'RT': RTcol,
                       'response': responsecol,
                       'accuracy': accuracycol,
                       'handshift': handshiftcol})
savedf.to_csv(os.path.join(output_path,'LearningSRTT_data.csv'), index=False)