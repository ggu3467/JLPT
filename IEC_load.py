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

class question_topic:
    def __init__(self, _title):
        self.title = _title
"""
 Définition du modèle de donnée d'un test JLPT
"""
class JLPT:
    def __init__(self, _year, _level):
        self.year  = _year
        self.level = _level
    class partie_1:
        def __init__(self,_text):
            self.text = _text
            self.question_topic = []
    class partie_2:
        def __init__(self, _text):
            self.text = _text
            self.question_topic = []

    class partie_3:
        def __init__(self, _text):
            self.text = _text
            self.question_topic = []




## \b LoadSCL:  classe générique pour charger un fichier SCL au niveau fichier et au niveau.
# Le code permet de s'abstraire des problèmes liés à des OS spécifiques
#
# @param fname      : le nom du fichier SCL
# @return sclMgr    : Point d'accès aux services de la librairie 'scl_loader'
# @return data      : Image de la section DataTypeTemplates du SCL.
# @return tComm     : Image de la section Communication du SCL

class Question:
    def __init__(self, question_text, correct_answer, hint='' ):
        self.question = question_text
        self.correct_answer = correct_answer
        self.hint   = hint
class Proposition:
    def __init__(self, reponse1, reponse2, reponse3, reponse4, reponse5='', reponse6='', answer='', hint='' ):
        self.reponse1 = reponse1
        self.reponse2 = reponse2
        self.reponse3 = reponse3
        self.reponse4 = reponse4
        self.reponse5 = reponse5
        self.reponse6 = reponse6
        self.answer  = answer
        self.hint    = hint

class LoadExcel(object):
    def __init__(self, _name: str, _load_excel:bool = False, _fullpath=False):
        self.file_name  = _name
        self.full_path   = _fullpath
        self.load_excel = _load_excel

        self.TEST = JLPT(1991, 'Level4')
        
    def __enter__(self):

#        Test_Set = XLRD.open_workbook(self.file_name)
        Test_Set = XLRD.open_workbook(self.file_name)
        sheet = Test_Set.sheet_by_index(0) 
        line_index = 1
        num_titre = 0
        # for extracting multiple rows at a time
        for i in range(line_index, sheet.nrows): 
            Title = sheet.cell_value(i, 0)

# Détection d'un grand chapître
            if Title.startswith('問題'): 
                if num_titre == 0:
                    self.TEST.partie_1.text = Title
                    print('self.TEST.partie1.text :' + self.TEST.partie_1.text )
                    num_titre = num_titre + 1
                elif num_titre == 1:
                    self.TEST.partie_2.text = Title
                    print('self.TEST.partie1.text :' + self.TEST.partie_2.text )
                    num_titre = num_titre + 1
                elif num_titre == 1:
                    self.TEST.partie_3.text = Title
                    print('self.TEST.partie1.text :' + self.TEST.partie_3.text )

                print("Chapitre de question:" + '問題' + ':' + Title[2])
                # TODO récupérer le numéro de chapître
                print('Chapitre de question' + Title)
                line_index = line_index +1

                while True:
                    topic = sheet.cell_value(line_index, 1)
                    line_index = line_index +1
# Détection d'une phrase qui fera l'objet de questio
                    if topic.startswith('問'):                    
                        question = topic
                        number = topic[1]
                        print("Topic:" + topic + ':' + str(number))
                        line_index = self.GetQuestionList(sheet, line_index)
                        if line_index is None:
                            return
            
            else:
                print('xxx')

    def GetQuestionList(self, sheet, line_index:int):

        question=""
        get_question = True
        while get_question is True:
            try:
                question = sheet.cell_value(line_index, 2)
            except IndexError:
                print('fin du fichier..')
                return None

            num_question = []
            if question.startswith('(') or question.startswith('（'):
                num_question.append('Q: ' + question)

                liste_choix = question.split('．')
                num_question  = liste_choix[0]
                topic        = liste_choix[1].split(' ')
                print('Choix' + num_question + topic[1] + topic[0])
                proposition = []
                for i in range(1,5):
                    proposition.append(liste_choix[i])

                for i in range(0,4):
                    print('Choix:' +  proposition[i] + '\n')

            else:
                break

            line_index = line_index +1
    


        return line_index

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Chargement fichier JLPT:" + str(self.file_name[0]) + "réussi.")



if __name__ == '__main__':

    with LoadExcel("JLPT_3_ESSAI_2003.xls", True, False) as (JLPT_TestSet):  # , self.T_LoadSCL):
        print("Chargement SCL ok")  # str(self.T_LoadSCL))



    print('Fin chargement Excel')

