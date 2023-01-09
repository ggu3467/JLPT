#
# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
#
#
# This file is part of [R#SPACE], [IEC61850 Digital Control System testing.
#

import logging
import pandas as XLS
import openpyxl


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

        Test_Set = XLS.read_excel(self.file_name)

        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Chargement fichier SCL:" + str(self.file_name[0]) + "réussi.")



if __name__ == '__main__':

    with Load_Excel("JLPT_3.xls", True, False) as (JLPT_TestSet):  # , self.T_LoadSCL):
        print("Chargement SCL ok")  # str(self.T_LoadSCL))
    


    print('xx')

