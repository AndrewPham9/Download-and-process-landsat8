from osgeo import gdal
from osgeo import ogr
import numpy as np 
import matplotlib.pyplot as plt
import os
import copy 
import math
import argparse
from cal import calTiff
import config_this
	
##need to set to nodata after do atmospheric correction
def run(folder):

	#dump metadata ls8 to dictionary
	def metadata_ls8 (metadata):
		metadata = open(metadata)
		metadata_dict = dict()
		for line in metadata:
			if '    ' in line.split('=')[0]:
				try:
					D = {(line.split('=')[0]).replace('    ','').replace(' ',''):line.split('=')[1].replace(' ','').replace('\n','')}
					metadata_dict.update(D)
				except:
					'last line have no split'
		return metadata_dict

	#convert to reflectance
	def  reflectance (band,Mp,Ap,sinSE):
		band = gdal.Open(band)
		band.GetRasterBand(1)
		band = band.ReadAsArray().astype(np.float)
		band[np.where(band==0)] = np.nan
		band = (band*Mp+Ap)/sinSE
		return band
	#find F5bins as first bin that have frequency > 50 and next right to it also > 50
	def find_1st_valid_detail (band):
		bandVals = band.ravel()
		unique, counts = np.unique(bandVals, return_counts = True)

		count_next = np.append([0],counts[0:len(counts)-1])
		count_next_2 = np.append([0],count_next[0:len(count_next)-1])
		#idea is take (x1 - x) if >50 then (x2 - x1) >50 choose x1
		A = np.where(count_next-counts > 50)
		B = np.where(count_next_2-count_next > 50)
		C = np.array(B)[0] - np.array(A)[0]
		for i in C:
			if i == 1:
				break
		loc = np.array(A)[0][i]
		return unique[loc]
	def setNotadata_0(band, no):
	    band_buffer = band
	    outband = band.replace('1.TIF','2.TIF')
	    driver = gdal.GetDriverByName("GTiff")
	    band = gdal.Open(band)
	    band.GetRasterBand(1)
	    band = band.ReadAsArray().astype(np.float)
	    band[np.where(band<0)] = no
	    config_this.createTiff(band, band_buffer, outband)

	def do_ats_correct(folder, band):
		path_band = path['%s'%(band)]
		Fbin5_band =  find_1st_valid_detail(reflectance(path_band,Mp,Ap,sinSE))
		#((DN*Mp)+ Ap)/sinSE
		expression = '((%s*%f)+%f)/%f-%f' % (band, Mp, Ap, sinSE, Fbin5_band)
		out_filename = folder+'/'+os.path.basename(folder)+'_' + band + 'product1.TIF'
		calTiff (folder, expression, out_filename)
		setNotadata_0(out_filename,np.nan)

	#config section
	driver = gdal.GetDriverByName("GTiff")
	metadata = folder + '/' +os.path.basename(folder) + '_MTL.txt'
	metadata = metadata_ls8(metadata)
	SUN_ELEVATION = metadata['SUN_ELEVATION']
	SUN_ELEVATION = math.radians(float(SUN_ELEVATION))
	sinSE = math.sin(SUN_ELEVATION)

	#from landsat 8 metadata
	Mp = 0.00002
	Ap = -0.1

	Fbin5s = dict()
	path = dict()
	path['B2'] = folder + '/' +os.path.basename(folder) + '_B2.TIF'
	path['B3'] = folder + '/' +os.path.basename(folder) + '_B3.TIF'
	path['B4'] = folder + '/' +os.path.basename(folder) + '_B4.TIF'
	path['B5'] = folder + '/' +os.path.basename(folder) + '_B5.TIF'

	bands = ['B2','B3','B4','B5']

	for band in bands:
		do_ats_correct(folder,band)


def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f",dest = "folder",help = "insert folder need to do correction", type = str)
    args = parser.parse_args()
    run(args.folder)
   # run(arg.shp,args.date,args.province)
if __name__=='__main__':
    main()


#'LC08_L1TP_125052_20180217_20180307_01_T1'