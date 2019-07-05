from osgeo import gdal
from osgeo import ogr
import os
import copy
import subprocess
def getFoldTiff (folder):
	folders = copy.copy(folder)
	bandPaths = []
	allFiles = os.listdir(folders)
	for i in allFiles:
		if '.TIF' in i:
			i = folder+'//' + i
			bandPaths.append(i)
	return bandPaths

def clip (shp,inRaster,outRaster):
	command="gdalwarp -cutline " +shp + " -crop_to_cutline -of GTiff -dstnodata NaN -overwrite " + inRaster +' '+ outRaster 
	p1 = subprocess.Popen(command,shell=True)
	p1.wait()	

def clipFolder (inFolder, outFolder, shp, band = None):
	shpName = os.path.basename(shp)
	print (shp)
	print ('hereherehere')
	print (shpName)
	print ('hereherehere')
	if band:
		for inRaster in getFoldTiff(inFolder):
			if inRaster.split('_')[-1].split('.')[0] == band:
				pathRow = os.path.basename(inRaster).split('_')[2]
				outRaster = outFolder + '/' + os.path.basename(inRaster)
				clip(shp,inRaster,outRaster)
	else:
		for inRaster in getFoldTiff(inFolder):
			pathRow = os.path.basename(inRaster).split('_')[2]
			outRaster = outFolder + '/' + os.path.basename(inRaster)
			clip(shp,inRaster,outRaster)
