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

class Answers:
    def __init__(self, _Ans1, _Ans2, _Ans3, _Ans4):
        self.Ans1 = _Ans1
        self.Ans2 = _Ans2
        self.Ans3 = _Ans3
        self.Ans4 = _Ans4

class QuestionTopic:
    def __init__(self, _title):
        self.title = _title

class JLPT:
    def __init__(self, _year, _level):
        self.Year  = _year
        self.Level = _level
    class partie1:
        def __init__(self,_text):
            self.text = _text
            self.QuestionTopic = []
    class partie2:
        def __init__(self, _text):
            self.text = _text
            self.QuestionTopic = []

    class partie3:
        def __init__(self, _text):
            self.text = _text
            self.QuestionTopic = []




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

        self.TEST = JLPT(1991, 'Level4')
        
    def __enter__(self):

#        Test_Set = XLRD.open_workbook(self.file_name)
        Test_Set = XLRD.open_workbook(self.file_name)
        sheet = Test_Set.sheet_by_index(0) 
        LineIndex = 1

        # for extracting multiple rows at a time
        for ligne in range(LineIndex, sheet.nrows): 
            num_titre = 0
            Title = sheet.cell_value(ligne,0)

# Détection d'un grand chapître
            if Title.startswith('問題'): 
                if num_titre == 0:
                    self.TEST.partie1.text = Title
                    print('self.TEST.partie1.text :' + self.TEST.partie1.text )
                    num_titre = num_titre + 1
                elif num_titre == 1:
                    self.TEST.partie2.text = Title
                    print('self.TEST.partie1.text :' + self.TEST.partie2.text )
                    num_titre = num_titre + 1
                elif num_titre == 1:
                    self.TEST.partie3.text = Title
                    print('self.TEST.partie1.text :' + self.TEST.partie2.text )

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
                        if LineIndex is None:
                            return
            
            else:
                print('xxx')

    def GetQuestionList(self, sheet, LineIndex):
                        
        QuestionList=[]
        GetQuestion = True
        while GetQuestion is True:
            
            try:
                Question = sheet.cell_value(LineIndex, 2)
            except IndexError:
                print('fin du fichier..')
                return None

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



    print('Fin chargement Excel')

