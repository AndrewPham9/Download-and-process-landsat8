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
import remove_cloud
import histo


def run(shp,date,province):
    print (shp)
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

    print (lowLeftLat)
    print (lowLeftLong)
    print (upRightLat)
    print (upRightLong)

    #create a landsat folder
    landsat_folders = ls8Down.Download_Landsat_8(str(lowLeftLat),str(lowLeftLong),str(upRightLat),str(upRightLong),str(date))
    # landsat_folders = [
                    # 'LC08_L1TP_125052_20160228_20180523_01_T1'
                    # ,'LC08_L1TP_125052_20140326_20170424_01_T1'
                    # ,'LC08_L1TP_125052_20150209_20180523_01_T1'
                    # ,'LC08_L1TP_125052_20170214_20170228_01_T1'
                    # ,'LC08_L1TP_125052_20180217_20180307_01_T1'
                    # ,'LC08_L1TP_125052_20190220_20190222_01_T1'
                    # ,'LC08_L1TP_125053_20140326_20170424_01_T1'
                    # ,'LC08_L1TP_125053_20150209_20180523_01_T1'
                    # ,'LC08_L1TP_125053_20160228_20180523_01_T1'
                    # ,'LC08_L1TP_125053_20180217_20180307_01_T1'
                    # ,'LC08_L1TP_125053_20170214_20170228_01_T1'
                    # ,'LC08_L1TP_125053_20190220_20190222_01_T1'
                    # ]
    # print (landsat_folders)
    #create a dictionary of all diriect folder, incase process many images once
    all_sum_direct_folder = list()
    #process each tar then add final to a tuple all_sum_direct_folder
    for landsat_folder in landsat_folders:
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
        #pick a name of first TIF to get date, scene...
        basename = config_this.getFoldTiff(landsat_folder)
        basename = pathOfFile(basename[0])
        #create a direct which will be lately moved tif into
        sum_direct_folder  = direct_folder+ '/'+ direct_folder + '_' + basename.datein

        if not os.path.exists(sum_direct_folder):
            os.mkdir(sum_direct_folder)
        else:
            pass

        direct_folder = direct_folder+ '/'+ direct_folder + '_'+basename.datein+'_'+basename.scene

        if not os.path.exists(direct_folder):
            os.mkdir(direct_folder)
        else:
            pass
        


        #atmospheric correction
        histo.run(landsat_folder)

        ########
        remove_cloud.removeCloud(landsat_folder,'B2product2')
        remove_cloud.removeCloud(landsat_folder,'B3product2')
        remove_cloud.removeCloud(landsat_folder,'B4product2')
        remove_cloud.removeCloud(landsat_folder,'B5product2')
        remove_cloud.removeCloud(landsat_folder,'B10')


        #clip band from landsat_folder and put result into direct_folder (province folder)
        clipMosaic.clipFolder(landsat_folder,direct_folder,shp,band = 'B2product3')
        clipMosaic.clipFolder(landsat_folder,direct_folder,shp,band = 'B3product3')
        clipMosaic.clipFolder(landsat_folder,direct_folder,shp,band = 'B4product3')
        clipMosaic.clipFolder(landsat_folder,direct_folder,shp,band = 'B5product3')
        clipMosaic.clipFolder(landsat_folder,direct_folder,shp,band = 'B10')
        clipMosaic.clipFolder(landsat_folder,direct_folder,shp,band = 'BQA')



        #remove zipfile and landsat_folder
        # os.remove(zipFile)
        shutil.rmtree(landsat_folder)
        #cal NDVI and LST then write a record to postgreSQL
        cal.NDVI(direct_folder)
        cal.LST(direct_folder)

        config_this.bring (direct_folder,sum_direct_folder)
        shutil.rmtree(direct_folder)
        #add sumdirect folder to all_direct_folder incase many process once
        all_sum_direct_folder.append(sum_direct_folder)

    all_sum_direct_folder = tuple(all_sum_direct_folder)    
    #mosaic for each folder
    for sum_direct_folder in all_sum_direct_folder:
        # clipMosaic.MosaicFolder(sum_direct_folder,'B2ref2')
        # clipMosaic.MosaicFolder(sum_direct_folder,'B3ref2')
        # clipMosaic.MosaicFolder(sum_direct_folder,'B4ref2')    #mosaic after have folder for true color

        #for process
        clipMosaic.MosaicFolder(sum_direct_folder,'BNDVI')
        clipMosaic.MosaicFolder(sum_direct_folder,'BLST')
        Tifs = config_this.getFoldTiff(sum_direct_folder)
        for Tif in Tifs:
            if 'BNDVI' in Tif:
                pathNDVI = Tif
            elif 'BLST' in Tif:
                pathLST = Tif
            else:
                os.remove(Tif)
        fieldsValues = {
            'location' : pathNDVI,
            'the_geom' : connectPostgres.getGeom(lowLeftLong,lowLeftLat,upRightLong,upRightLat,4326)
        }
        connectPostgres.insertSQL('processed_images',**fieldsValues)

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

    run(args.shp,args.date,args.province)
   # run(arg.shp,args.date,args.province)
if __name__=='__main__':
    main()


#py -3 D:/python/STAC_intern_project/NDVI_LST/test.py -s D:/python/STAC_intern_project/NDVI_LST/bentre/bentre_tinh_polygon.shp -d 20190619 -p BenTr