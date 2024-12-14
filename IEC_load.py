#
# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
#
#
# This file is part of [R#SPACE], [IEC61850 Digital Control System testing.
#

import logging
# import pandas as XLRD
import xlrd as XLRD

"""
 Définition du modèle de donnée d'un test JLPT
"""


class JLPT_Section:
    def __init__(self, _part, _year, _level):
        self.Part = _part
        self.year = _year
        self.level = _level
        self.QuestionSet = []  # list[JLPT_Section.Question]       # liste de Question

class Question:  #
    def __init__(self, _reponse_, _answer): #: list[str]):  # 問1・ 車の中に男の子が何人いますか。
#        self.text = _text  # 問1・ 車の中に男の子が何人いますか。
        self.answer = _answer  # Choix de l'utilisateur
        self.subQuestion = [10]  #: list[JLPT_Section.Question.Proposition]
        self.question = ''  # （1）．雨 １．かぜ ２．あめ ３．ゆき ４．くも
        self.reponse =  _reponse_
        self.hint = ''
        self.answer = ''  # IHM answer


class Test_JLPT:
    def __init__(self, book, sheet):
        self.sheet = sheet
        self.book  = book
        self.Chapitre = ['問題Ⅰ', '問題ⅠⅠ', '問題Ⅲ']
        self.Section = [1, 2, 3]
        self.Consigne = ""  # " 問題Ⅰ＿＿＿のことばはどうよみますか"
        self.Part1 = []  # QuestionX()
        self.Part2 = []  # QuestionX()
        self.lineIndex = 1

        self.TestSection        = 0  # Colonne 0 Titre 問題Ⅰ＿＿＿のことばはどうよみますか
        self.TestQuestion       = 1  # Colonne 1     問1・ 車の中に男の子が何人いますか。
        self.TestProposition    = 2  # Colonne 2     （1）．車 １．しゃ ２．くるま ３．ちゃ ４．くろま
        self.reponseCorrecte     = 3

    def TestPart(self, sheet):
        num_titre = 1
        self.lineIndex = 1

        T1 = self.sheet.cell_value(self.lineIndex, self.TestSection)  # Titre 問題Ⅰ＿＿＿のことばはどうよみますか
        if not T1.startswith('問題'):
            exit(-1)
        else:
            JLPT_Part1 = JLPT_Section(T1, 1991, 'Level4')
            self.Part1, self.lineIndex = self.ParseTest(JLPT_Part1, self.lineIndex)

            T2 = self.sheet.cell_value(self.lineIndex, self.TestSection)
            JLPT_Part2 = JLPT_Section(T2, 1991, 'Level4')
            self.Part2, self.lineIndex = self.ParseTest(JLPT_Part2, self.lineIndex)

            #            JLPT_Part3 = JLPT_Section(T1, 1991, 'Level4')
            #            self.Part3, self.lineIndex = self.ParseTest(JLPT_Part1, self.lineIndex)

            return self.Part1 # ('Manque 問題 sur première ligne')


    def ParseTest(self, JLPT_Part1: JLPT_Section, lineIndex: int):
        lineIndex = lineIndex + 1
        GlobalList=[]
        JLP_question = Question('xxx', [])
        _SubQuestion = ''
        try:
            while True:
                _question = self.sheet.cell_value(lineIndex, self.TestQuestion)
                if _question.startswith('問'):
                    print('****** Question : ', _question + ' ' + str(self.lineIndex))
                    JLP_question = Question(_question, [])
                    lineIndex = lineIndex + 1
                    _SubQuestion = self.sheet.cell_value(lineIndex, self.TestProposition)
                    _SubReponse  = self.sheet.cell_value(lineIndex, self.reponseCorrecte)
                else:
    #                _SubQuestion.append(_SubQuestion) # '問1・ 車の中に男の子が何人いますか。'
                    while _SubQuestion.startswith('（'):
                        JLP_question.subQuestion.append(_SubQuestion)
                        print('SubQuestion : ', _SubQuestion + ' ' + str(lineIndex))
                        lineIndex = lineIndex + 1
                        _SubQuestion = self.sheet.cell_value(lineIndex, self.TestProposition)
                        _SubReponse  = self.sheet.cell_value(lineIndex, self.reponseCorrecte)

                    _question = self.sheet.cell_value(lineIndex,   self.TestQuestion)
                    _SubReponse = self.sheet.cell_value(lineIndex, self.reponseCorrecte)
                    GlobalList.append(JLP_question)
                    if _question.startswith('問'):
                        continue
                    _Chapitre = self.sheet.cell_value(lineIndex, 0)
                    if _Chapitre.startswith('問題'):
                        return GlobalList, lineIndex
                        break
                continue
        except IndexError:
             print('Fin du ficher')
        return GlobalList


## \b LoadSCL:  classe générique pour charger un fichier SCL au niveau fichier et au niveau.
# Le code permet de s'abstraire des problèmes liés à des OS spécifiques
#
# @param fname      : le nom du fichier SCL
# @return sclMgr    : Point d'accès aux services de la librairie 'scl_loader'
# @return data      : Image de la section DataTypeTemplates du SCL.
# @return tComm     : Image de la section Communication du SCL

class LoadExcel(object):
    def __init__(self, _name: str, sheet, _load_excel: bool = False, _fullpath=False):
        self.file_name = _name
        self.full_path = _fullpath
        self.load_excel = _load_excel
        self.sheet = sheet

    def __enter__(self):
        self.Test_Set = XLRD.open_workbook(self.file_name)
        self.sheet = self.Test_Set.sheet_by_index(0)  # Accès au premier onglet du tableau Excel
        return (self.Test_Set, self.sheet)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("__exit__")
        self.Test_Set.release_resources()
        del (self.Test_Set)


if __name__ == '__main__':
    with LoadExcel("JLPT_3_ESSAI_2003.xls", True, False) as (JLPT_TestSet, sheet):
        print("Chargement SCL ok")  # str(self.T_LoadSCL))

    Test = Test_JLPT(JLPT_TestSet,sheet)
    Test.TestPart()



