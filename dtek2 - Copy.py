from usgs import api
import usgs
from usgs import USGS_API
from usgs import xsi, payloads
import requests
import urllib.request as urllib2
import json
import argparse
import numpy as np 
import sys
import math
from osgeo import gdal
from osgeo import ogr
from gdalconst import*
import os
import re
import copy
import shutil
import tarfile
import clipMosaic
import yu
import cal
import ls8Down
import gzip
import connectPostgres
import config_this
from config_this import pathOfFile
#
def run(shp,date,province):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shp, 0)
    layer = dataSource.GetLayer()
    feature = layer[0]
    geom = feature.GetGeometryRef()

    A = geom.GetEnvelope()
    lowLeftLat = A[2] #(y dưới trái)
    lowLeftLong = A[0] #(x dưới trái)
    upRightLat = A[3] #(y trên phải)
    upRightLong = A[1] #(x trên phải)


    #create a landsat folder
    landsat_folder = ls8Down.Download_Landsat_8(str(lowLeftLat),str(lowLeftLong),str(upRightLat),str(upRightLong),str(date))
    direct_folder = province + 'IMAGES'
    if not os.path.exists(landsat_folder):
        os.mkdir(landsat_folder)
    else:
        pass
    
    #extract file into a landsat folder
    zipFile = landsat_folder  +'.tar.gz'
    tar = tarfile.open(zipFile, "r:gz")
    tar.extractall(landsat_folder)
    tar.close()
    
    #create a folder has province's name, if exist then pass.
    if not os.path.exists(direct_folder):
        os.mkdir(direct_folder)
    else:
        pass
    basename = config_this.getFoldTiff(landsat_folder)
    basename = pathOfFile(basename[0])
    direct_folder = direct_folder+ '/'+ direct_folder + '_'+basename.datein+'_'+basename.scene
    os.mkdir(direct_folder)

    #clip band from landsat_folder and put result into direct_folder (province folder)
    clipMosaic.clipFolder(landsat_folder,direct_folder,shp,band = 'B4')
    clipMosaic.clipFolder(landsat_folder,direct_folder,shp,band = 'B5')
    clipMosaic.clipFolder(landsat_folder,direct_folder,shp,band = 'B10')

    #remove zipfile and landsat_folder
    os.remove(zipFile)
    shutil.rmtree(landsat_folder)

    #cal NDVI and LST then write a record to postgreSQL
    pathNDVI = cal.NDVI(direct_folder)
    fieldsValues = {
        'location' : pathNDVI,
        'the_geom' : connectPostgres.getGeom(lowLeftLong,lowLeftLat,upRightLong,upRightLat,4326)
    }
    connectPostgres.insertSQL('processed_images',**fieldsValues)

    pathLST = cal.LST(direct_folder)
    fieldsValues ={
        'location' : pathLST,
        'the_geom' : connectPostgres.getGeom(lowLeftLong,lowLeftLat,upRightLong,upRightLat,4326)
    }
    connectPostgres.insertSQL('processed_images',**fieldsValues)


def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s",dest = "shp",help = "shape file with name of province", type = str)
    parser.add_argument("-d",dest = "date",help = "date captured", type = str)
    parser.add_argument("-p",dest = "province",help = "province", type = str)
    args = parser.parse_args()
    run('D:/python/STAC_intern_project/NDVI_LST/shp_gcs/bentre_tinh_polygon.shp','20190612','BenTre')
   # run(arg.shp,args.date,args.province)
if __name__=='__main__':
    main()


#py -3 D:/python/STAC_intern_project/NDVI_LST/test.py -s D:/python/STAC_intern_project/NDVI_LST/bentre/bentre_tinh_polygon.shp -d 20190619 -p BenTre