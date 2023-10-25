#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 16:36:58 2023
Code for plotting the triplet frequencies for each group for the last day's training. 
@author: gdf724
"""

import os
import glob
import itertools
import pandas as pd
import numpy as np
import Grammar_stimuli as gstim
import matplotlib.pyplot as plt


#%% Get all available triplets.
def getTriplets(cue_positions, clean):
    #Order matters
    init_combinations=[]
    for com in itertools.combinations_with_replacement(cue_positions,3):
        init_combinations.append(com[0]+com[1]+com[2])
    
    if clean:
        #Clean from repeats.
        combinations = []
        for combination in init_combinations:
            if combination[0]!=combination[1] and combination[1]!=combination[2]:
                for perm in itertools.permutations(combination,3):
                    combinations.append(perm[0]+perm[1]+perm[2])
    else:
        combinations = []
        for combination in init_combinations:
            for perm in itertools.permutations(combination,3):
                combinations.append(perm[0]+perm[1]+perm[2])
    nodup_combinations = []
    for i in combinations:
        if i not in nodup_combinations:
            nodup_combinations.append(i)
    
    return nodup_combinations

#%% Get plot settings
def getplotsettings(indx):
    if indx==0:
        plot_data_occ = triplet_occ_day1.loc[triplet_occ_day1['group']==8020].iloc[:,2:]
        plot_data_RT = triplet_meanRT_day1.loc[triplet_meanRT_day1['group']==8020].iloc[:,2:]
        savename_occ = 'TripletOcc_HiLo_Day1.png'
        savename_RT = 'TripletRT_HiLo_Day1.png'
        title='HiLo group Day 1'
    elif indx==1:
        plot_data_occ = triplet_occ_day2.loc[triplet_occ_day1['group']==8020].iloc[:,2:]
        plot_data_RT = triplet_meanRT_day2.loc[triplet_meanRT_day1['group']==8020].iloc[:,2:]
        savename_occ = 'TripletOcc_HiLo_Day2.png'
        savename_RT = 'TripletRT_HiLo_Day2.png'
        title='HiLo group Day 2'
    elif indx==2:
        plot_data_occ = triplet_occ_day3.loc[triplet_occ_day1['group']==8020].iloc[:,2:]
        plot_data_RT = triplet_meanRT_day3.loc[triplet_meanRT_day1['group']==8020].iloc[:,2:]
        savename_occ = 'TripletOcc_HiLo_Day3.png'
        savename_RT = 'TripletRT_HiLo_Day3.png'
        title='HiLo group Day 3' 
    elif indx==3:
        plot_data_occ = triplet_occ_day1.loc[triplet_occ_day1['group']==5050].iloc[:,2:]
        plot_data_RT = triplet_meanRT_day1.loc[triplet_meanRT_day1['group']==5050].iloc[:,2:]
        savename_occ = 'TripletOcc_Eq_Day1.png'
        savename_RT = 'TripletRT_Eq_Day1.png'
        title='Eq group Day 1'
    elif indx==4:
        plot_data_occ = triplet_occ_day2.loc[triplet_occ_day1['group']==5050].iloc[:,2:]
        plot_data_RT = triplet_meanRT_day2.loc[triplet_meanRT_day1['group']==5050].iloc[:,2:]
        savename_occ = 'TripletOcc_Eq_Day2.png'
        savename_RT = 'TripletRT_Eq_Day2.png'
        title='Eq group Day 2'
    elif indx==5:
        plot_data_occ = triplet_occ_day3.loc[triplet_occ_day1['group']==5050].iloc[:,2:]
        plot_data_RT = triplet_meanRT_day3.loc[triplet_meanRT_day1['group']==5050].iloc[:,2:]
        savename_occ = 'TripletOcc_Eq_Day3.png'
        savename_RT = 'TripletRT_Eq_Day3.png'
        title='Eq group Day 3' 
        
    return plot_data_occ, plot_data_RT, savename_occ, savename_RT, title
#%% Load and save data
datadir='/Users/gdf724/Data/MovementGrammar/AGIL/'
datafile = '/Users/gdf724/Data/MovementGrammar/AGIL/LearningSRTT_data.csv'
reportdir = '/Users/gdf724/Data/MovementGrammar/AGIL/Triplet_check/'
allowed_keys = ['a', 'b', 'c', 'f', 'g', 'h']
learningdata = pd.read_csv(datafile)
#Build a structure with the triplets as column names and one row per subject. 
#Also consider th grammaticality? 
triplets = getTriplets(allowed_keys,False)
df_columns = ['subject', 'group']+triplets
triplet_RTs_day1 = pd.DataFrame(columns=df_columns)
triplet_RTs_day2 = pd.DataFrame(columns=df_columns)
triplet_RTs_day3 = pd.DataFrame(columns=df_columns)
tmp_data = [[] for _ in range(len(df_columns))]
subject_list = list(set(learningdata['subject']))


curr_subj = learningdata['subject'][0]
tmp_data[0] = learningdata['subject'][0]
tmp_data[1] = learningdata['group'][0]
curr_day = 0
curr_seq = 0
for itr in range(len(learningdata)):
    if learningdata['sequence'][itr]!=curr_seq:
        if learningdata['day'][itr]!=curr_day:
            if curr_day==1:
                triplet_RTs_day1.loc[len(triplet_RTs_day1)] = tmp_data
                tmp_data = [[] for _ in range(len(df_columns))]
            elif curr_day==2:
                triplet_RTs_day2.loc[len(triplet_RTs_day2)] = tmp_data
                tmp_data = [[] for _ in range(len(df_columns))]
            elif curr_day==3:
                triplet_RTs_day3.loc[len(triplet_RTs_day3)] = tmp_data
                tmp_data = [[] for _ in range(len(df_columns))]
                curr_subj=learningdata['subject'][itr]
            tmp_data[0] = learningdata['subject'][itr]
            tmp_data[1] = learningdata['group'][itr]
            curr_day=learningdata['day'][itr]
        curr_seq=learningdata['sequence'][itr]
        #For each sequence, add the six triplets
        #Can only be average of the two last responses in the triplet because the first RT is from responding on that one. 
        tmp_data[df_columns.index(learningdata['response'][itr]+learningdata['response'][itr+1]+learningdata['response'][itr+2])].append(np.mean(learningdata['RT'][itr+1:itr+3]))
        tmp_data[df_columns.index(learningdata['response'][itr+1]+learningdata['response'][itr+2]+learningdata['response'][itr+3])].append(np.mean(learningdata['RT'][itr+2:itr+4]))
        tmp_data[df_columns.index(learningdata['response'][itr+2]+learningdata['response'][itr+3]+learningdata['response'][itr+4])].append(np.mean(learningdata['RT'][itr+3:itr+5]))
        tmp_data[df_columns.index(learningdata['response'][itr+3]+learningdata['response'][itr+4]+learningdata['response'][itr+5])].append(np.mean(learningdata['RT'][itr+4:itr+6]))
        tmp_data[df_columns.index(learningdata['response'][itr+4]+learningdata['response'][itr+5]+learningdata['response'][itr+6])].append(np.mean(learningdata['RT'][itr+5:itr+7]))
        tmp_data[df_columns.index(learningdata['response'][itr+5]+learningdata['response'][itr+6]+learningdata['response'][itr+7])].append(np.mean(learningdata['RT'][itr+6:itr+8]))
triplet_RTs_day3.loc[len(triplet_RTs_day3)] = tmp_data

#Calculate triplet grammaticality
hilo_grammar = gstim.getGrammar('8020', True)
eq_grammar = gstim.getGrammar('5050', True)
hilo_triplet_scores = [0]*len(triplets)
eq_triplet_scores = [0]*len(triplets)
#Same for grammaticality score, only the changes to the stimuli can have a
#score associated to the triplet. 
for tri_itr in range(len(triplets)):
    hilo_triplet_scores[tri_itr] = gstim.calcGramScore_seq(triplets[tri_itr], hilo_grammar)
    eq_triplet_scores[tri_itr] = gstim.calcGramScore_seq(triplets[tri_itr], eq_grammar)

triplet_occ_day1 = pd.DataFrame(columns=df_columns)
triplet_occ_day1['subject'] = triplet_RTs_day1['subject']
triplet_occ_day1['group'] = triplet_RTs_day1['group']
triplet_occ_day2 = pd.DataFrame(columns=df_columns)
triplet_occ_day2['subject'] = triplet_RTs_day1['subject']
triplet_occ_day2['group'] = triplet_RTs_day1['group']
triplet_occ_day3 = pd.DataFrame(columns=df_columns)
triplet_occ_day3['subject'] = triplet_RTs_day1['subject']
triplet_occ_day3['group'] = triplet_RTs_day1['group']
triplet_meanRT_day1 = pd.DataFrame(columns=df_columns)
triplet_meanRT_day1['subject'] = triplet_RTs_day1['subject']
triplet_meanRT_day1['group'] = triplet_RTs_day1['group']
triplet_meanRT_day2 = pd.DataFrame(columns=df_columns)
triplet_meanRT_day2['subject'] = triplet_RTs_day1['subject']
triplet_meanRT_day2['group'] = triplet_RTs_day1['group']
triplet_meanRT_day3 = pd.DataFrame(columns=df_columns)
triplet_meanRT_day3['subject'] = triplet_RTs_day1['subject']
triplet_meanRT_day3['group'] = triplet_RTs_day1['group']
#Calculate triplet occasions
for itr in range(2,triplet_RTs_day1.shape[1]):
    tmp = triplet_RTs_day1.iloc[:,itr]
    for iitr in range(len(tmp)):
        triplet_occ_day1[tmp.name][iitr]=len(tmp[iitr])
        triplet_meanRT_day1[tmp.name][iitr]=np.mean(tmp[iitr])
    tmp = triplet_RTs_day2.iloc[:,itr]
    for iitr in range(len(tmp)):
        triplet_occ_day2[tmp.name][iitr]=len(tmp[iitr])
        triplet_meanRT_day2[tmp.name][iitr]=np.mean(tmp[iitr])
    tmp = triplet_RTs_day3.iloc[:,itr]
    for iitr in range(len(tmp)):
        triplet_occ_day3[tmp.name][iitr]=len(tmp[iitr])
        triplet_meanRT_day3[tmp.name][iitr]=np.mean(tmp[iitr])
    #All sequences are 8 elements long. Triplets: 1-3 2-4 3-5 4-6 5-7 6-8
    #Triplet grammaticality can be calculated later
    #Don't care about the order right now, just save the RTs. Occasions are the length of each list.


#Binary grammaticality and handshifts (HiLo allowed values are: 2.4, 1.8, 1.6, 1.2, 1.0, 0.6, 0.4 )
left_keys = ['a', 'b', 'c']
right_keys = ['f', 'g', 'h']
triplet_colors = []

for trip in triplets:
    if trip[0] in left_keys and trip[1] in right_keys: 
        light = 'dark'
    elif trip[0] in left_keys and trip[2] in right_keys:
        light = 'dark'
    elif trip[0] in right_keys and trip[1] in left_keys: 
        light = 'dark'
    elif trip[0] in right_keys and trip[2] in left_keys: 
        light = 'dark'
    else:
        light = 'light'
    
    if eq_grammar[trip[1]][trip[0]] != 0.5 or eq_grammar[trip[2]][trip[1]] != 0.5:
        gramcolor ='blue'
    else:
        gramcolor = 'green'
    triplet_colors.append(light+gramcolor)
#Plot. Box plot with SD bars, colored by grammaticality
#One per day and per group

for pltitr in range(6):
    plot_data_occ,plot_data_RT,savename_occ,savename_RT,title = getplotsettings(pltitr) 
    
    plt.figure(figsize=(50,10))
    bxplt = plt.boxplot(plot_data_occ,
                vert=True,
                patch_artist=True,
                labels=triplets)
    for box_itr in range(len(bxplt['boxes'])):
        bxplt['boxes'][box_itr].set(color=triplet_colors[box_itr])
    
    plt.xticks(rotation=90)
    plt.ylim(0,80)
    plt.title(title)
    plt.ylabel('Occurances')
    plt.savefig(os.path.join(reportdir,savename_occ), bbox_inches="tight")
    plt.close()
    
    plt.figure(figsize=(50,10))
    bxplt = plt.boxplot(plot_data_RT,
                vert=True,
                patch_artist=True,
                labels=triplets)
    for box_itr in range(len(bxplt['boxes'])):
        bxplt['boxes'][box_itr].set(color=triplet_colors[box_itr])
    
    plt.xticks(rotation=90)
    plt.ylim(0,1.4)
    plt.title(title)
    plt.ylabel('Response Time/s')
    plt.savefig(os.path.join(reportdir,savename_RT), bbox_inches="tight")
    plt.close()


