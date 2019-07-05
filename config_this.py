import copy
import os
class pathOfFile:
    def __init__(self,path):
        self.path = path
        self.scene = path.split('\\')[-1].split('_')[2]
        self.datein = path.split('\\')[-1].split('_')[3]
        self.band = path.split('\\')[-1].split('_')[-1].split('.')[0]

def getFoldTiff (folder):
    folders = copy.copy(folder)
    TIFs = []
    allFiles = os.listdir(folders)
    for i in allFiles:
        if '.TIF' in i:
            i = folder+'\\' + i
            TIFs.append(i)
    return TIFs

