import config_this
import numpy.ma as ma
from osgeo import gdal
from osgeo import ogr
import numpy as np 
import os



def removeCloud (folder, inBand): 

    bands = config_this.getFoldTiff(folder)
    for band in bands:
    	if 'BQA' in band:
    		break

    BQA = gdal.Open(band)
    BQA = BQA.ReadAsArray().astype(np.float)
    BQA = np.array(BQA)

    bands = config_this.getFoldTiff(folder)
    for band in bands:
    	if inBand in band:
    		break

    print (band)
    band_buffer = band
    new = gdal.Open(band)
    new = new.ReadAsArray().astype(np.float)
    new = np.array(new)

    noise = [2976, 2980, 2984, 2988, 3008, 3012, 3016, 3020, 7072, 7076, 7080, 7084, 7104, 7108, 7112, 7116, 2800, 2804, 2808, 2812, 6896, 6900, 6904, 6908]
    for i in noise:
        new[np.where(BQA==i)] = np.nan

    newband = band_buffer.replace('2.TIF','3.TIF')
    print (newband)
    config_this.createTiff(new, band_buffer, newband)
