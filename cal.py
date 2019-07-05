import numpy as np 
import sys
import math
from osgeo import gdal
from osgeo import ogr
from gdalconst import*
import os
import subprocess
import re
import copy
import subprocess
import argparse
import clipMosaic
import config_this
from config_this import pathOfFile
from config_this import getFoldTiff
################################ CALCULATE BY gdal_calc.py ##################################
########### 1) using gdap_calc.py all data type should be float32
########### 2) using numpy array maybe faster but more messy
########### 3) gdal accept only A -> Z as band name
########### 4) call this file by <syste>/cal.py -kind <NDVI or LST....> -folder <your landsat folder>

##raster band math
def calTiff (folder, expression, out_filename):
	#gdal accept only A -> Z as band name
	BandValid = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
				"N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
	bandPaths = getFoldTiff(folder)
	#create dictionary of {bandName:bandPath}
	bandNeed = (re.findall(r"[\w']+", expression))
	bandNeed2 = list()
	for i in bandNeed:
		if i[0] == 'B':
			bandNeed2.append(i)
	bandNeed = bandNeed2
	band2paths = dict()
	for band in bandNeed:
		for bandPath in bandPaths:
			if band in os.path.basename(bandPath):
				band2paths.update({BandValid[bandNeed.index(band)]:bandPath})
				bandPaths.remove(bandPath)

	#astpye(float32) for getting negative value, and return correct number when devide
	for band in set(bandNeed):
		expression = expression.replace(band,str(BandValid[bandNeed.index(band)]+'.astype(float32)'))
	#assign band2paths dictionary into a gdal_calc.py string
	assign = str()
	for key, value in band2paths.items():
		assign = assign + ' -'+ key + ' '+value
	

	#then put all of them in a cmdLine
	cmdLine = ("py -3 C:/Users/USER/AppData/Local/Programs/Python/Python36/Scripts/gdal_calc.py --calc="+
				expression+' --type=Float32 --NoDataValue=0 --outfile='+out_filename+assign)
	p = subprocess.Popen(cmdLine,shell=True)
	p.wait()
	print (cmdLine)

def NDVI (folder):

	pathNDVI = folder+'/'+os.path.basename(folder)+'_'+'_BNDVI.TIF'
	calTiff(folder,'(B5-B4)/(B5+B4)',pathNDVI)
	return pathNDVI

def LST (folder):

	Tiffs = getFoldTiff(folder)
	for Tiff in Tiffs:
		if '_BNDVI' in Tiff:
			pathNDVI = Tiff
	B10 = folder+'/'+os.path.basename(folder)+'_B10.TIF'
	if os.path.exists(pathNDVI ):
		pass
	else:
		NDVI(folder)

	driver = gdal.GetDriverByName('GTiff')
	in_file = gdal.Open(pathNDVI)
	band = in_file.GetRasterBand(1)
	NDVIarray = (band.ReadAsArray()).astype(np.float)
	NDVIarray[np.isnan(NDVIarray)] = 0
	NDVIarray[np.isinf(NDVIarray)] = 0


	NDVImax, NDVImin = np.nanmax(NDVIarray), np.nanmin(NDVIarray)
	print (np.where(NDVIarray == -0.3947368562221527))


	pathT = folder+'/'+os.path.basename(folder)+'_BT.TIF'
	pathE = folder+'/'+os.path.basename(folder)+'_BE.TIF'
	pathLST = folder+'/'+os.path.basename(folder)+'_BLST.TIF'
			# K1=774.89, K2=1321.08, M=3.342*(10**(-4)), A=0.1.
			# lamdaB = B10*(M)+A
			# T = K2/(np.log(1+K1/lamdaB))-273.15
			# lDevideP=float(10.8/14388)
			# e = ((x-NDVImin)/(NDVImax-NDVImin))**2
			# LST = T/(1+(float(10.8/14388)*T)*np.log(e))
	eqT = '1321.08/(log(1+774.89/(B10*3.342*(10**(-4))+0.1)))-273.15'
	eqE = '((BNDVI-%f)/(%f-%f))**2'%(NDVImin,NDVImax,NDVImin)
	eqLST = 'BT/(1+(0.000751)*BT*log(BE))'

	calTiff(folder,eqT,pathT)
	calTiff(folder,eqE,pathE)
	calTiff(folder,eqLST,pathLST)
	os.remove(pathT)
	os.remove(pathE)
	return (pathLST)
def choose (kind,folder):
	if kind == 'NDVI':
		NVDI(folder)
	elif  kind == 'LST':
		LST(folder)
def main ():
	parser = argparse.ArgumentParser()
	parser.add_argument('-k', dest= "kind",help = "interest index", type = str)
	parser.add_argument('-f', dest="folder",help = "interest index", type = str)
	args = parser.parse_args()
	choose (args.kind,args.folder)

if __name__=='__main__':
    main()  



#py -3 D:/python/STAC_intern_project/NDVI_LST/dtek2.py -s D:/python/STAC_intern_project/NDVI_LST/bentre/bentre_tinh_polygon.shp -d 20190619 -p BenTre