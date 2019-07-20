from osgeo import gdal
from osgeo import ogr
import numpy as np 
import os
import copy
import subprocess


def clip (shp,inRaster,outRaster):
	command="gdalwarp -cutline " +shp + " -crop_to_cutline -of GTiff -dstnodata 0 -overwrite " + inRaster +' '+ outRaster 
	p1 = subprocess.Popen(command,shell=True)
	p1.wait()	
	shpName = os.path.basename(shp)
	return outRaster

def createTiff(arr, imageDim, outband):
    imageDim = gdal.Open(imageDim)
    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outband,imageDim.RasterXSize,imageDim.RasterYSize,1,6)
    outDs.SetMetadata(imageDim.GetMetadata())
    outDs.SetGeoTransform(imageDim.GetGeoTransform())
    outDs.SetProjection(imageDim.GetProjection())
    outDs.GetRasterBand(1).WriteArray(arr)
    del outDs

def average (raster, shp):
	outRaster = raster.replace('.TIF','ho.TIF')
	raster = clip (shp, raster, outRaster)
	#open raster after cutline
	raster = gdal.Open(raster)
	raster.GetRasterBand(1)
	raster = raster.ReadAsArray().astype(np.float)
	print (raster)
	average = raster[raster>0].mean()
	
	os.remove(outRaster)
	print (average)
	return average

def heat_island (raster, value):
	raster_buffer = raster
	raster_heat_island = raster.replace('.TIF','-HUI.TIF')
	raster = gdal.Open(raster)
	raster.GetRasterBand(1)
	raster = raster.ReadAsArray().astype(np.float)
	raster = raster - value
	createTiff(raster, raster_buffer, raster_heat_island)

def getFoldTiff (folder):
    folders = copy.copy(folder)
    TIFs = []
    allFiles = os.listdir(folders)
    for i in allFiles:
        if '.TIF' in i:
            i = folder+'//' + i
            TIFs.append(i)
    return TIFs
shp = 'C:/Users/USER/Desktop/average_T/CuChi.shp'
folder = 'C:/Users/USER/Desktop/average_T/result'



Tiffs = getFoldTiff(folder)
for Tiff in Tiffs:

	heat_island(Tiff, average(Tiff, shp))