#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------
#
# Author: Francois Schiettecatte
# Creation Date: November 2014 (ported from Perl)
#


#--------------------------------------------------------------------------
#
# Description:
#
# Language identifier, creates language specific ngram data files from text 
# and and identifies the language of a piece of text.
#


#--------------------------------------------------------------------------
#
# Command lines:
#
#

#
# Creating ngram data:
#
#
# ./languageIdentifier.py --create --text-file=textcat.texts/en.txt | more
#
# ./languageIdentifier.py --create --text-file=textcat.texts/fr.txt | more
#
# ./languageIdentifier.py --create --text-file=textcat.texts/ja.txt | more
#
# ./languageIdentifier.py --create --text-file=textcat.texts/zh_SC.txt | more
#
# ./languageIdentifier.py --create --text-file=textcat.texts/zh_TC.txt | more
#
# ./languageIdentifier.py --create --text-directory=textcat.texts --ngram-directory=textcat.ngrams
#
# ./languageIdentifier.py ---create -text-directory=udhr.texts --ngram-directory=udhr.ngrams
#
#

#
# Identifying text language:
#
#
# en
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="the quick brown fox"
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="the quick brown fox jumped over the lazy dog"
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --hint=en --text="the quick brown fox"
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --hint=en --text="the quick brown fox jumped over the lazy dog"
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --hint=en --hint-multiplier=1.2 --text="the quick brown foxg"
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --hint=en --hint-multiplier=1.2 --text="the quick brown fox jumped over the lazy dog"
#
#
# fr
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="le renard brun rapide a sauté par-dessus le chien paresseux"
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="Après l'Assemblée mardi, le Sénat a voté mercredi le projet de loi qui doit, selon le gouvernement, soutenir le pouvoir d'achat, la croissance et l'emploi dès 2009."
#
#
# de
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="der schnelle braune Fuchs sprang über den faulen Hund"
#
#
# es
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="el zorro marrón rápido saltó sobre el perro perezoso"
#
#
# el
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="η γρήγορη καφετιά αλεπού πήδησε πέρα από το οκνηρό σκυλί"
#
#
# it
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="a volpe marrone rapida ha saltato sopra il cane pigro"
#
#
# pt
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="a raposa marrom rápida saltou sobre o cão preguiçoso"
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="A Marinha está a rebocar para o Porto de Peniche uma embarcação com sete pescadores que esta madrugada se estava a afundar, a cerca de 30 milhas a Oeste do cabo Carvoeiro, noticia a agência Lusa. Segundo o capitão do porto Peniche, Guerreiro Cardos"
#
#
# ja
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="速い茶色のフォックスは不精な犬を飛び越した"
#
#
# ko
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="빠른 갈색 여우는 게으른 개에 뛰어올랐다"
#
#
# nl
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="de snelle bruine vos sprong over de luie hond"
#
#
# ru
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="быстро коричневая лисица поскакала над ленивой собакой"
#
#
# zh_SC
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="快速棕色狐狸跳过了懒惰狗"
#
#
# zh_TC
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text="快速棕色狐狸跳過了懶惰狗"
#
#
# --
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text=""
#


#
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text-file=textcat.texts/en.txt
#
# ./languageIdentifier.py --ngram-directory=textcat.ngrams --text-file=textcat.texts/fr.txt
#
#


#--------------------------------------------------------------------------
#
# Imported modules
#

import getopt
import locale
import logging
import operator
import os
import os.path
import re
import sys


#--------------------------------------------------------------------------
#
# Constants
#

# Text file name extension
TEXT_FILE_NAME_EXTENSION = '.txt'


#--------------------------------------------------------------------------
#
# Setup
#

# Set the locale
locale.setlocale(locale.LC_ALL, 'en_US')

# Logging format - '2014-02-21 09:37:25,480 CRITICAL - ...'
LOGGING_FORMAT = '%(asctime)s %(levelname)s - %(message)s'

# Logging basic config
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)


#--------------------------------------------------------------------------
#
# Globals
#

# Logger
logger = logging.getLogger()


#--------------------------------------------------------------------------
#
#   Class:      Ngram
#
#   Purpose:    Ngram class
#
class Ngram(object):

    # Ngram maximum length
    NGRAM_MAXIMUM_LENGTH = 4


    #--------------------------------------------------------------------------
    #
    #   Method:     __init__
    #   
    #   Purpose:    Constructor
    #
    #   Parameters: language        language
    #               ngramFilePath   ngram file path
    #
    #   Exceptions: ValueError      if the language is invalid
    #               ValueError      if the ngram file path is invalid
    #
    def __init__(self, language, ngramFilePath):

        # Check parameters
        if not language:
            raise ValueError('Invalid language')
   
        if not ngramFilePath:
            raise ValueError('Invalid ngram file path')


        # Set the instance variables
        self.language = language
        self.ngramFilePath = ngramFilePath
        self.ngramDict = None
        self.ngramMaximumLength = 0


        # Read the ngram file
        self._readNgramFile()

        

    #--------------------------------------------------------------------------
    #
    #   Method:     _readNgramFile
    #
    #   Purpose:    Read the ngram file
    #
    #   Parameters: 
    #
    #   Exceptions: ValueError      if there is an invalid entry in the ngram file
    #
    #   Returns:    
    #
    def _readNgramFile(self):

        # Ngram dict
        self.ngramDict = dict()
        
        # Open the ngram file
        ngramFile = open(self.ngramFilePath, encoding='utf-8')

        # Read the ngram file
        for line in ngramFile:

            # Clean the line
            line = line.strip()
            
            # Parse the line
            match = re.match(r'^(.*?)\s+(.*)$', line)
            if match:
            
                # Get the ngram and the normalized frequency
                ngram = match.group(1)
                normalizedFrequency = float(match.group(2))
                
                # Add the ngram and the normalized frequency to the ngram dict
                self.ngramDict[ngram] = normalizedFrequency
                
                # Update the ngram maximum length
                self.ngramMaximumLength = max(self.ngramMaximumLength, len(ngram))
            
            # Match failed
            else:
                raise ValueError('Invalid ngram entry: \'{}\', in ngram file: \'{}\''.format(line, self.ngramFilePath))
        
        # Close the ngram file
        ngramFile.close()



    #--------------------------------------------------------------------------
    #
    #   Method:     score
    #
    #   Purpose:    Score against the passed text ngram dict/text
    #
    #   Parameters: textNgramDict   text ngram dict (optional)
    #               text            text (optional)
    #
    #   Exceptions: ValueError      if the text ngram dict/text is invalid
    #
    #   Returns:    the score
    #
    def score(self, textNgramDict=None, text=None):

        # Check parameters
        if not textNgramDict and not text:
            raise ValueError('Invalid text ngram dict/text')
        elif textNgramDict and text:
            raise ValueError('Invalid text ngram dict/text')

        
        # Extract the text ngram dict if needed
        if text:
            textNgramDict = Ngram.extractNgramDict(text, ngramMaximumLength=self.ngramMaximumLength)
        
        
        # The score
        score = 0
        
        # Loop over all the text ngrams in the text ngram dict,
        # and increment the score if applicable
        for textNgram, textFrequency in textNgramDict.items():
            
            # Get the normalized frequency from the ngram dict
            normalizedFrequency = self.ngramDict.get(textNgram)

            # Increment the score if the normalized frequency is defined
            if normalizedFrequency:
                score += normalizedFrequency * textFrequency


        # Return the score
        return score



    #--------------------------------------------------------------------------
    #
    #   Function:   extractNgramDict()
    #
    #   Purpose:    Extract the ngram dict from the text
    #
    #   Called by:   
    #
    #   Parameters: text                the text
    #               ngramMaximumLength  ngram maximum length
    #
    #   Exceptions: ValueError      if the text is invalid
    #
    #   Returns:   the ngram dict
    #
    @staticmethod
    def extractNgramDict(text, ngramMaximumLength=NGRAM_MAXIMUM_LENGTH):

        # Check parameters
        if not text:
           raise ValueError('Invalid text')


        # Split the text into a list of terms
        termList = re.split(r'[^\w]+', text)


        # The ngram dict
        ngramDict = dict()

        # Loop over each term in the term list
        for term in termList:
        
            # Skip empty terms
            if not term:
                continue
        
            # Downcase
            term = term.lower()

            # Term length
            termLength = len(term)

            # Adjusted ngram length, in case the term is too short
            ngramAdjustedLength = min(termLength, ngramMaximumLength)

            # Loop over the ngram range
            for start in range(1 - ngramAdjustedLength, termLength):
    
                # End of the ngram range
                end = min(start + ngramAdjustedLength, termLength)
    
                # Start can never be less than 0
                if start < 0:
                    start = 0

                # Extract the ngram we want
                ngram = term[start:end]

                # Close off start and end
                if start == 0:
                     ngram = '$' + ngram 
                if end == termLength:
                     ngram += '$' 
    
                # And add it to the ngram dict
                if ngram not in ngramDict:
                    ngramDict[ngram] = 0
                ngramDict[ngram] += 1


        # Log
        logger.info('Terms processed: %d, ngrams extracted: %d.', len(termList), len(ngramDict))


        # Return the ngram dict
        return ngramDict



    #--------------------------------------------------------------------------
    #
    #   Function:   normalizeNgramDict()
    #
    #   Purpose:    Normalize the ngram dict 
    #
    #   Called by:   
    #
    #   Parameters: ngramDict           the ngram dict
    #               ngramMaximumLength  ngram maximum length
    #
    #   Exceptions: ValueError      if the ngram dict is invalid
    #
    #   Returns:   the same ngram dict
    #
    @staticmethod
    def normalizeNgramDict(ngramDict, ngramMaximumLength=NGRAM_MAXIMUM_LENGTH):

        # Check parameters
        if not ngramDict:
           raise ValueError('Invalid ngram dict')


        # Loop over all the ngrams by length, adding up the frequencies and then normalizing them
        for ngramLength in range(ngramMaximumLength, 0, -1):
            
            # Total frequency for this length
            totalFrequency = 0
            
            # Add up the frequencies
            for ngram, frequency in ngramDict.items():
                term = ngram.replace('$', '')
                if len(term) == ngramLength:
                    totalFrequency += frequency
            
            # Normalize the frequencies and set them back in the ngrams hash
            for ngram, frequency in ngramDict.items():
                term = ngram.replace('$', '')
                if len(term) == ngramLength:
                    ngramDict[ngram] = (frequency / totalFrequency) * ngramLength


        # Return the ngram dict
        return ngramDict



    #--------------------------------------------------------------------------
    #
    #   Function:   createNgramFile()
    #
    #   Purpose:    
    #
    #   Called by:   
    #
    #   Parameters: textFilePath        the text file path
    #               textFile            the text file
    #               ngramFilePath       the ngram file path
    #               ngramFile           the ngram file
    #               ngramMaximumLength  the ngram maximum length
    #
    #   Exceptions: ValueError      if the text file path/text file is invalid
    #               ValueError      if the ngram file path/ngram file is invalid
    #
    #   Returns:   
    #
    @staticmethod
    def createNgramFile(textFilePath=None, textFile=None, ngramFilePath=None, ngramFile=None,
            ngramMaximumLength=NGRAM_MAXIMUM_LENGTH):

        # Check parameters
        if not textFilePath and not textFile:
            raise ValueError('Invalid text file path/text file')
        elif textFilePath and textFile:
            raise ValueError('Invalid text file path/text file')
        
        if not ngramFilePath and not ngramFile:
            raise ValueError('Invalid ngram file path/ngram file')
        elif ngramFilePath and ngramFile:
            raise ValueError('Invalid ngram file path/ngram file')
        
        
        # Open the text file if needed
        if textFilePath:
            textFile = open(textFilePath, encoding='utf-8')
    
        # Read the text file
        text = textFile.read()
    
        # Extract the ngram dict
        ngramDict = Ngram.extractNgramDict(text, ngramMaximumLength=ngramMaximumLength)

        # Normalize the ngram dict
        ngramDict = Ngram.normalizeNgramDict(ngramDict, ngramMaximumLength=ngramMaximumLength)

        # Create the ngram file if needed
        if ngramFilePath:
            ngramFile = open(ngramFilePath, 'w', encoding='utf-8')

        # Sort the ngram dict in order of descending frequency
        for ngram, frequency in sorted(ngramDict.items(), key=operator.itemgetter(1), reverse=True):
            ngramFile.write('{:<10}{}\n'.format(ngram, frequency))
    
        # Close the text file if needed
        if textFilePath:
            textFile.close()

        # Close the ngram file if needed
        if ngramFilePath:
            ngramFile.close()



#--------------------------------------------------------------------------
#
#   Class:      LanguageIdentifier
#
#   Purpose:    Language identifier
#
class LanguageIdentifier(object):

    # Ngram file name extension
    NGRAM_FILE_NAME_EXTENSION = '.txt'
    
    # Hint multiplier (10%)
    HINT_MULTIPLIER = 0.10


    #--------------------------------------------------------------------------
    #
    #   Method:     __init__
    #   
    #   Purpose:    Constructor
    #
    #   Parameters: ngramDirectoryPath      ngram directory path
    #               ngramFileNameExtension  ngram file name extension (optional)
    #               hintMultiplier          hint multiplier (optional)
    #
    #   Exceptions: ValueError      if the ngram directory path is invalid
    #               ValueError      if no ngram files were found
    #
    def __init__(self, ngramDirectoryPath, ngramFileNameExtension=NGRAM_FILE_NAME_EXTENSION, 
            hintMultiplier=HINT_MULTIPLIER):

        # Check parameters
        if not ngramDirectoryPath:
            raise ValueError('Invalid ngram directory path')


        # Set the instance variables
        self.ngramDirectoryPath = ngramDirectoryPath
        self.ngramFileNameExtension = ngramFileNameExtension
        self.ngramMaximumLength = 0
        self.languageNgramList = list()
        self.hintMultiplier = hintMultiplier

        
        # Ngram file path list, tuple of language and file path
        ngramFilePathList = list()

        # Create the match regex for filtering file names,
        # matching the following formats:
        #
        #   en.txt
        #   eng.txt
        #   en_US.txt
        #   
        ngramFileNameMatchRegex = re.compile(r'^(\w\w|\w\w\w|\w\w_\w\w)\{}$'.format(self.ngramFileNameExtension))

        # Walk over the the text directory
        for dirname, dirnames, filenames in os.walk(self.ngramDirectoryPath):
    
            # Walk over the files names
            for filename in filenames:
        
                # Match on the file name
                matcher = ngramFileNameMatchRegex.match(filename)
                    
                # Skip over file names that don't match the regex
                if not matcher:
                    continue
                
                # Set the language from the ngram file name
                language = matcher.group(1)
                        
                # Create the text file path
                ngramFilePath = os.path.join(dirname, filename)
        
                # Add the language and ngram file path to the ngram file path list
                ngramFilePathList.append((language, ngramFilePath,))


        # Check that we got ngram files
        if len(ngramFilePathList) == 0:
            raise ValueError('Failed to find any ngram files in the ngram directory: \'{}\''.format(self.ngramDirectoryPath))

    
        # Loop over the ngram file path list
        for language, ngramFilePath in ngramFilePathList:
        
            # Create a new language ngram object for this ngram file path/language combination
            languageNgram = Ngram(language, ngramFilePath)
            
            # Update the ngram maximum length
            self.ngramMaximumLength = max(self.ngramMaximumLength, languageNgram.ngramMaximumLength)
            
            # And append the language ngram to the language ngram list
            self.languageNgramList.append(languageNgram)



    #--------------------------------------------------------------------------
    #
    #   Method:     score
    #   
    #   Purpose:    Get the scores for a piece of text
    #
    #   Parameters: text            text
    #               hint            language hint
    #               hintMultiplier  hint multiplier
    #
    #   Exceptions: ValueError      if the text is invalid
    #
    #   Returns:   
    #
    def score(self, text, hint=None, hintMultiplier=HINT_MULTIPLIER):

        # Check parameters
        if not text:
            raise ValueError('Invalid text')

        
        # Extract the ngram dict from the text
        textNgramDict = Ngram.extractNgramDict(text, ngramMaximumLength=self.ngramMaximumLength)
        
        
        # The score list, tuple of language and score
        scoreList = list()

        # Loop over the language ngram list, setting the language 
        # and score in the score dict
        for languageNgram in self.languageNgramList:
            
            # Get the score
            score = languageNgram.score(textNgramDict=textNgramDict)
        
            # Set the score dict if the score is meaningful
            if score:

                # Multiply the score if a hint was provided and the language scored
                if hint == languageNgram.language:
                    if not hintMultiplier:
                        hintMultiplier = self.hintMultiplier
                    if hintMultiplier:
                        score *= (1 + hintMultiplier)
        
                # Set the score dict if the score is meaningful
                scoreList.append((languageNgram.language, score,))
        
        
        # Sort the score list
        scoreList = sorted(scoreList, key=lambda tuple: tuple[1], reverse=True)


        # And return the score list
        return scoreList



#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#
#   Function:   createFromFile()
#
#   Purpose:    Create from file
#
#   Called by:   
#
#   Parameters: textFilePath        the text file path (optional)
#               textFile            the text file (optional)
#               ngramFilePath       the ngram file path (optional)
#               ngramFile           the ngram file (optional)
#               ngramMaximumLength  the ngram maximum length (optional)
#
#   Exceptions: ValueError      if the text file path/text file is invalid
#               ValueError      if the ngram file path/ngram file is invalid
#
#   Returns:   
#
def createFromFile(textFilePath=None, textFile=None, ngramFilePath=None, ngramFile=None,
        ngramMaximumLength=Ngram.NGRAM_MAXIMUM_LENGTH):

    # Check parameters
    if not textFilePath and not textFile:
        raise ValueError('Invalid text file path/text file')
    elif textFilePath and textFile:
        raise ValueError('Invalid text file path/text file')
   
    if not ngramFilePath and not ngramFile:
        raise ValueError('Invalid ngram file path/ngram file')
    elif ngramFilePath and ngramFile:
        raise ValueError('Invalid ngram file path/ngram file')

    
    # Log 
    if textFilePath and ngramFilePath:
        logger.info('Processing from: \'%s\', to: \'%s\'.', textFilePath, ngramFilePath)
    elif textFilePath and not ngramFilePath:
        logger.info('Processing from: \'%s\', to: \'stdout\'.', textFilePath)
    elif not textFilePath and ngramFilePath:
        logger.info('Processing from: \'stdin\', to: \'%s\'.', ngramFilePath)
    elif not textFilePath and not ngramFilePath:
        logger.info('Processing from: \'stdin\', to: \'stdout\'.')


    # Create the ngram file
    Ngram.createNgramFile(textFilePath=textFilePath, textFile=textFile, 
            ngramFilePath=ngramFilePath, ngramFile=ngramFile, ngramMaximumLength=ngramMaximumLength)



#--------------------------------------------------------------------------
#
#   Function:   createFromDirectory()
#
#   Purpose:    Create from directory
#
#   Called by:   
#
#   Parameters: textDirectoryPath       the text directory path
#               ngramDirectoryPath      the ngram directory path
#               textFileNameExtension   the text file name extension (optional)
#               ngramFileNameExtension  the ngram file name extension (optional)
#               ngramMaximumLength      the ngram maximum length (optional)
#
#   Exceptions: ValueError      if the text directory path is invalid
#               ValueError      if the ngram directory path is invalid
#
#   Returns:   
#
def createFromDirectory(textDirectoryPath, ngramDirectoryPath, 
        textFileNameExtension=TEXT_FILE_NAME_EXTENSION, 
        ngramFileNameExtension=LanguageIdentifier.NGRAM_FILE_NAME_EXTENSION, 
        ngramMaximumLength=Ngram.NGRAM_MAXIMUM_LENGTH):

    # Check parameters
    if not textDirectoryPath:
        raise ValueError('Invalid text directory path')
   
    if not ngramDirectoryPath:
        raise ValueError('Invalid ngram directory path')
   
   
    # Create the match regex for filtering text file names,
    # matching the following formats:
    #
    #	en.txt
    #	eng.txt
    #	en_US.txt
    #	
    textFileNameMatchRegex = re.compile(r'^(\w\w|\w\w\w|\w\w_\w\w)\{}$'.format(textFileNameExtension))


    # Walk over the the text directory
    for dirname, dirnames, filenames in os.walk(textDirectoryPath):
    
        # Walk over the files names
        for filename in filenames:
        
            # Skip over file names that don't match the regex
            if not textFileNameMatchRegex.match(filename):
                continue

            # Create the text file path
            textFilePath = os.path.join(dirname, filename)
        
            # Create the ngram file name
            ngramFileName = filename[:-(len(textFileNameExtension))] + ngramFileNameExtension

            # Create the ngram file path
            ngramFilePath = os.path.join(ngramDirectoryPath, ngramFileName)
            
            # Create with the file path
            createFromFile(textFilePath=textFilePath, ngramFilePath=ngramFilePath, 
                    ngramMaximumLength=ngramMaximumLength)



#--------------------------------------------------------------------------
#
#   Function:   identifyText()
#
#   Purpose:    Identify the text
#
#   Called by:   
#
#   Parameters: languageIdentifier  the language identifier
#               text                the text
#               hint                the language hint (optional)
#               hintMultiplier      the hint multiplier (optional)
#
#   Exceptions: ValueError          if the language identifier is invalid
#               ValueError          if the text is invalid
#
#   Returns:   
#
def identifyText(languageIdentifier, text, hint=None, 
        hintMultiplier=LanguageIdentifier.HINT_MULTIPLIER):

    # Check parameters
    if not languageIdentifier:
        raise ValueError('Invalid language identifier')
   
    if not text:
        raise ValueError('Invalid text')


    # Get the scores for the text
    scoreList = languageIdentifier.score(text, hint, hintMultiplier)
    
    # List the scores
    if scoreList:
        
        # Total score
        totalScore = 0

        # Get the total score
        for language, score in scoreList:
            totalScore += score
        
        # List the scores
        for language, score in scoreList:
            logger.info('{:<5}    {:f}    {:%}'.format(language, score, (score / totalScore)))
    
    # Fail
    else:
        logger.warn('Could not identify the passed text')



#--------------------------------------------------------------------------
#
#   Function:   identifyTextFromFile()
#
#   Purpose:    Identify the text from a file
#
#   Called by:   
#
#   Parameters: languageIdentifier  the language identifier
#               textFilePath        the text file path
#               hint                the language hint (optional)
#               hintMultiplier      the hint multiplier (optional)
#
#   Exceptions: ValueError          if the language identifier is invalid
#               ValueError          if the text file path is invalid
#
#   Returns:   
#
def identifyTextFromFile(languageIdentifier, textFilePath, hint=None, 
        hintMultiplier=LanguageIdentifier.HINT_MULTIPLIER):

    # Check parameters
    if not languageIdentifier:
        raise ValueError('Invalid language identifier')
   
    if not textFilePath:
        raise ValueError('Invalid text file path')

    
    # Log
    logger.info('Processing file: \'%s\'', textFilePath)

    # Open, read and close the text file
    textFile = open(textFilePath, encoding='utf-8')
    text = textFile.read()
    textFile.close()

    # Identify the text
    identifyText(languageIdentifier, text, hint, hintMultiplier)



#--------------------------------------------------------------------------
#
#   Function:   usage
#
#   Purpose:    usage
#
#   Parameters:    
#
#   Exceptions:
#
#   Returns:       
#
def usage():

    print('Usage:')
    print('\t[-h|--help] print out this message.')
    print('')
    print('Processing options:')
    print('\t[--create] create ngrams, default is to identify text language')
    print('\t[--hint=name] language hint, optional, no default')
    print('\t[--hint-multiplier=#] language hint multiplier, optional, defaults, defaults to: \'{}\''.format(LanguageIdentifier.HINT_MULTIPLIER))
    print('')
    print('Text options:')
    print('\t[--text=name|--text-file=name|--text-directory=name] text, text file name or text directory name, optional, defaults to \'stdin\'.')
    print('\t[--text-file-extension=name] text file name extension, optional, defaults to: \'{}\''.format(TEXT_FILE_NAME_EXTENSION))
    print('')
    print('Ngram options:')
    print('\t[--ngram-file=name|--ngram-directory=name] ngram file name or ngram directory name, optional, defaults to \'stdout\'.')
    print('\t[--ngram-file-extension=name] ngram file name extension, optional, defaults to: \'{}\''.format(LanguageIdentifier.NGRAM_FILE_NAME_EXTENSION))
    print('\t[--ngram-maximum-length=#] ngram length, defaults to: {}'.format(Ngram.NGRAM_MAXIMUM_LENGTH))
    print('')



#--------------------------------------------------------------------------
#
#   Function:   main()
#
#   Purpose:    main
#
#   Called by:   
#
#   Parameters:   
#
#   Exceptions:   
#
#   Returns:   void
#
if __name__ == '__main__':


    # The options
    opts = None


    # Get the command line parameters
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help',
                'create', 'hint=', 'hint-multiplier=',
                'text=', 'text-file=', 'text-directory=', 'text-file-extension=',
                'ngram-file=', 'ngram-directory=', 'ngram-file-extension='])

    # Handle exception, print error and usage
    except getopt.GetoptError as exception:
        print(str(exception))
        print('')

        usage()
        sys.exit(-1)



    # Create flag
    create = False

    # Hint
    hint = None

    # Hint multiplier
    hintMultiplier = LanguageIdentifier.HINT_MULTIPLIER

    # Text
    text = None

    # Text file path
    textFilePath = None

    # Text directory path
    textDirectoryPath = None

    # Text file name extension
    textFileNameExtension = TEXT_FILE_NAME_EXTENSION

    # Ngram file path
    ngramFilePath = None

    # Ngram directory path
    ngramDirectoryPath = None

    # Ngram file name extension
    ngramFileNameExtension = LanguageIdentifier.NGRAM_FILE_NAME_EXTENSION

    # Ngram maximum length
    ngramMaximumLength = Ngram.NGRAM_MAXIMUM_LENGTH


    # Process the options
    for opt, arg in opts:

        if opt == '--create':
            create = True

        elif opt == '--hint':
            hint = arg

        elif opt == '--hint-multiplier':
            hintMultiplier = arg

        elif opt == '--text':
            text = arg

        elif opt == '--text-file':
            textFilePath = arg

        elif opt == '--text-directory':
            textDirectoryPath = arg

        elif opt == '--text-file-extension':
            textFileNameExtension = arg

        elif opt == '--ngram-file':
            ngramFilePath = arg

        elif opt == '--ngram-directory':
            ngramDirectoryPath = arg

        elif opt == '--ngram-file-extension':
            ngramFileNameExtension = arg

        elif opt == '--ngram-maximum-length':
            ngramMaximumLength = arg

        elif opt in ('-h', '--help'):
            usage()
            sys.exit(-1)

        else:
            assert False, 'Invalid option: \'{}\''.format(opt)



    # Create ngram
    if create: 

        # Directory to directory
        if textDirectoryPath and ngramDirectoryPath:

            # Create with directory path
            createFromDirectory(textDirectoryPath, ngramDirectoryPath, textFileNameExtension=textFileNameExtension, 
                    ngramFileNameExtension=ngramFileNameExtension, ngramMaximumLength=ngramMaximumLength)
    
        # File/stdin to file/stdout
        elif not textDirectoryPath and not ngramDirectoryPath:
    
            # Text file and ngram file
            textFile = None
            ngramFile = None
    
            # Set the text file to stdin if needed
            if not textFilePath:
                textFile = sys.stdin

            # Set the ngram file to stdout if needed
            if not ngramFilePath:
                ngramFile = sys.stdout

            # Create with file path
            createFromFile(textFilePath=textFilePath, textFile=textFile, ngramFilePath=ngramFilePath, 
                    ngramFile=ngramFile, ngramMaximumLength=ngramMaximumLength)

        # Fail
        else:
            logger.error('Invalid parameter combination')
            sys.exit(-1)

    # Identify text 
    else:

        # Create the language identifier
        languageIdentifier = LanguageIdentifier(ngramDirectoryPath, ngramFileNameExtension, hintMultiplier)


        # Text file path
        if textFilePath:

            # Identify with file path
            identifyTextFromFile(languageIdentifier, textFilePath, hint, hintMultiplier)
    
        # Text
        elif text:

            # Identify text
            identifyText(languageIdentifier, text, hint, hintMultiplier)

        # Fail
        else:
            logger.error('Invalid parameter combination')
            sys.exit(-1)



    # Log
    logger.info('Processing finished')


    sys.exit(0)


#--------------------------------------------------------------------------
