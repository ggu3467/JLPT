#
# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
#
#
# This file is part of [R#SPACE], [IEC61850 Digital Control System testing.
#

import logging
#import pandas as XLRD
import xlrd as XLRD


## \b encodeFileName:  encode un chemin de fichier selon l'OS (Windows/Linux)
#
# Cette adapte le chemin des fichiers à l'OS, utile surtour pour __Main__ et tests.
#
# @param fName      : Nom du fichier ou chemin, utilisant '/' ou '\'. Encodage final pour l'OS utilisé.
# @param FileName   : Délai d'attente maximal en ms
#



## \b LoadSCL:  classe générique pour charger un fichier SCL au niveau fichier et au niveau.
# Le code permet de s'abstraire des problèmes liés à des OS spécifiques
#
# @param fname      : le nom du fichier SCL
# @return sclMgr    : Point d'accès aux services de la librairie 'scl_loader'
# @return data      : Image de la section DataTypeTemplates du SCL.
# @return tComm     : Image de la section Communication du SCL
class Load_Excel(object):
    def __init__(self, _name: str, _load_excel:bool = False, _fullpath=False):
        self.file_name  = _name
        self.fullPath   = _fullpath
        self.load_excel = _load_excel

    def __enter__(self):

#        Test_Set = XLRD.open_workbook(self.file_name)
        Test_Set = XLRD.open_workbook(self.file_name)
        sheet = Test_Set.sheet_by_index(0) 
        LineIndex = 1
        
        # for extracting multiple rows at a time
        for i in range(LineIndex, sheet.nrows): 
            Title = sheet.cell_value(i, 0)

# Détection d'un grand chapître
            if Title.startswith('問題'):
                print("Chapitre de question:" + '問題' + ':' + Title[2])
                # TODO récupérer le numéro de chapître
                print('Chapitre de question' + Title)
                LineIndex = LineIndex +1

                while (True):
                    Topic = sheet.cell_value(LineIndex, 1)
                    LineIndex = LineIndex +1
# Détection d'une phrase qui fera l'objet de questio
                    if Topic.startswith('問'):                    
                        Question = Topic
                        Number = Topic[1]
                        print("Topic:" + Topic + ':' + str(Number))
                        LineIndex = self.GetQuestionList(sheet, LineIndex)
            
            else:
                print('xxx')

    def GetQuestionList(self, sheet, LineIndex):
                        
        QuestionList=[]
        GetQuestion = True
        while GetQuestion is True:
            
            Question = sheet.cell_value(LineIndex, 2)
            NumQuestion = []
            if Question.startswith('(') or Question.startswith('（'):
                NumQuestion.append('Q: ' + Question)

                ListeChoix = Question.split('．')
                NumQuestion  = ListeChoix[0]
                Topic        = ListeChoix[1].split(' ')
                print('Choix' + NumQuestion + Topic[1] + Topic[0])
                Proposition = []
                for i in range(1,5):
                    Proposition.append(ListeChoix[i])

                for i in range(0,4):
                    print('Choix:' +  Proposition[i] + '\n')

            else:
                break

            LineIndex = LineIndex +1
    
        for Question in QuestionList:
            print('Question:'  + Question)

        return LineIndex

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Chargement fichier JLPT:" + str(self.file_name[0]) + "réussi.")



if __name__ == '__main__':

    with Load_Excel("JLPT_3_ESSAI_2003.xls", True, False) as (JLPT_TestSet):  # , self.T_LoadSCL):
        print("Chargement SCL ok")  # str(self.T_LoadSCL))


    X = JLPT_TestSet.columns


    print("X" + str(X))
    for iX in X:
        print('Text: ' + str(iX))


    Y = JLPT_TestSet.lines
    for iY in Y:
        print('Text: ' + str(iY))

    Y = JLPT_TestSet
    for iY in Y:
        print('Text: ' + str(iY))

##    print('xxxx',JLPT_TestSet)
    
    


    print('xx')

