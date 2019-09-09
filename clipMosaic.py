from osgeo import gdal
from osgeo import ogr
import os
import copy
import subprocess
import shutil
import config_this

py_scripts = config_this.config_py()['py_3_scripts']

def getFoldTiff (folder):
	folders = copy.copy(folder)
	bandPaths = []
	allFiles = os.listdir(folders)
	for i in allFiles:
		if '.TIF' in i:
			i = folder+'//' + i
			bandPaths.append(i)
	return bandPaths


def clipFolder (inFolder, outFolder, shp, band = None):

	def clip (shp,inRaster,outRaster):
		command="gdalwarp -cutline " +shp + " -crop_to_cutline -of GTiff -dstnodata NaN -overwrite " + inRaster +' '+ outRaster 
		p1 = subprocess.Popen(command,shell=True)
		p1.wait()	
		shpName = os.path.basename(shp)
		print (command)

	if band:
		for inRaster in getFoldTiff(inFolder):
			if inRaster.split('_')[-1].split('.')[0] == band:
				pathRow = os.path.basename(inRaster).split('_')[2]
				outRaster = outFolder + '/' + os.path.basename(inRaster)
				clip(shp,inRaster,outRaster)
				return outRaster
	else:
		for inRaster in getFoldTiff(inFolder):
			pathRow = os.path.basename(inRaster).split('_')[2]
			outRaster = outFolder + '/' + os.path.basename(inRaster)
			clip(shp,inRaster,outRaster)


def MosaicFolder (inFolder = None,band= None):
		#
		alpha = 'NaN'
		inRaster = str()
		inRasterList = list()
		Tifs = 	getFoldTiff (inFolder)
		for Tif in Tifs:
			if band in Tif:
				inRaster = inRaster + ' ' + Tif
				inRasterList.append(Tif)
				
		outRaster = inFolder + '/' + os.path.basename(inFolder) + '_'+band
		# -a_nodata = NaN for no color out side the image when display in pyplot
		command="py -3 "+py_scripts+"/gdal_merge.py -o "+outRaster+".TIF -of GTiff -ot Float32 -n " + alpha + " -a_nodata NaN"+ inRaster
		p1 = subprocess.Popen(command,shell=True)
		p1.wait()
		print ('xoa nhung anh nay')
		print (inRasterList)
		for tif in inRasterList:
			os.remove(tif)
# MosaicFolder('D:/python/STAC_intern_project/Download-and-process-landsat8/HoChiMinhIMAGES/HoChiMinhIMAGES_20140326', 'BNDVI')
