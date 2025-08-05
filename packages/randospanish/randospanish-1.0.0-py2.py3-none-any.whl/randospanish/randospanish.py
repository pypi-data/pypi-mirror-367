import os
import numpy as np
from . import utils

DATA = np.load(utils.datadir()+'spanish_database_5000words.npy')

def pickoptions(randomword,noptions=5):
    # Get random options
    done = False
    numpicked = 0
    optdata = []
    pickcount = 0
    while (done==False):
        optdata1 = np.random.choice(DATA)
        optnum = optdata1['number']
        if (optnum != randomword[-1]) and (optnum not in [o['number'] for o in optdata]): 
            optdata.append(optdata1)
            numpicked += 1
        if numpicked >= noptions:
            done = True
        pickcount += 1
    return optdata
        
def randomword(noptions=4,maxattempts=10):
    """
    Random word
    """

    flag = False
    count = 0
    history = []
    while (flag==False):

        # Pick the next word
        #  done repeat words
        randomword = np.random.choice(DATA)
        
        # Get random options
        optdata = pickoptions(randomword,noptions=noptions)
        
        # Stick the correct number in a random location
        correctposition = np.random.randint(noptions+1)
        alldata = optdata.copy()
        alldata.insert(correctposition,randomword)
            
        # Print them out
        print(randomword['word'])
        for i in range(len(alldata)):
            print('{:2d} {:s}'.format(i+1,alldata[i]['engdef']))
            
        # Solve attempts
        solvedone = False
        solved = False
        solvecount = 0
        while (solvedone==False):
            # Read answer
            guess = input('What is the correct definition? ')
            if guess.lower() == 'q':
                return
            if guess.isnumeric()==False:
                print(' ')
                print('Not a number')
                print(' ')
                solvecount += 1
                continue
            guess = int(guess)
            if guess != correctposition+1:
                print(' ')
                print('Incorrect')
                print(' ')
                solvecount += 1
                continue
            else:
                print(' ')
                print('Correct!')
                print(' ')
                solved = True
                solvecount += 1
            if solved or solvecount >= maxattempts:
                solvedone = True
        
        
        # Save what happened
        hist = [randomword,optdata,solved,solvecount]
        history.append(hist)
        
        count += 1
