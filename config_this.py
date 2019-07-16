import copy
import os
from osgeo import gdal
from osgeo import ogr
import numpy as np 
import shutil
import configparser



class pathOfFile:
    def __init__(self,path):
        self.path = path
        self.scene = path.split('//')[-1].split('_')[2]
        self.datein = path.split('//')[-1].split('_')[3]
        self.band = path.split('//')[-1].split('_')[-1].split('.')[0]

def getFoldTiff (folder):
    folders = copy.copy(folder)
    TIFs = []
    allFiles = os.listdir(folders)
    for i in allFiles:
        if '.TIF' in i:
            i = folder+'//' + i
            TIFs.append(i)
    return TIFs

def createTiff(arr, imageDim, outband):
    imageDim = gdal.Open(imageDim)
    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outband,imageDim.RasterXSize,imageDim.RasterYSize,1,6)
    outDs.SetMetadata(imageDim.GetMetadata())
    outDs.SetGeoTransform(imageDim.GetGeoTransform())
    outDs.SetProjection(imageDim.GetProjection())
    outDs.GetRasterBand(1).WriteArray(arr)
    del outDs



def bring (folder1,folder2):
    list_tif_1 = getFoldTiff(folder1)
    list_tif_2 = list()
    for tif in list_tif_1:
        new_tif = folder2 + '/' + os.path.basename(tif)
        shutil.move(tif, new_tif)
def config_py (configFile = 'py_machine.txt', section = 'py_machine'):
    parser = configparser.ConfigParser()
    parser.read(configFile)
    return dict(parser.items(section))

    # os.remove(band_buffer)
# bring ('D:/python/STAC_intern_project/Download-and-process-landsat8/HoChiMinhIMAGES/HoChiMinhIMAGES_20160228_125052', 'D:/python/STAC_intern_project/Download-and-process-landsat8/HoChiMinhIMAGES/to')