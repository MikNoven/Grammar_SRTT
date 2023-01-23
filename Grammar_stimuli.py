#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:39:39 2023
Script for generating stimlus sequences for Grammar SRTT.
@author: gdf724
"""

import random

def getRandomSequences(lengthOfSequences,sequencesPerBlock):
    keys = ['s', 'd', 'f', 'j', 'k', 'l']
    block_stim = []
    block_stim.append(keys[random.randrange(0,len(keys)-1)])
    for itr in range(lengthOfSequences*sequencesPerBlock-1):
        tmp=keys[:]
        tmp.remove(block_stim[-1]) #Making sure there are no simple repeats.
        block_stim.append(tmp[random.randrange(0,len(keys)-1)])
    
    return block_stim