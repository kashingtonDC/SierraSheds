import os
import requests

import numpy as np
import pandas as pd
import geopandas as gp

from tqdm import tqdm

# Dict mapping various GCMs to the data directories (these are all for precip, note ppt str)
dl_urls = {
	
	"GISS_26" : "https://cida.usgs.gov/thredds/fileServer/CA-BCM-2014/GISS_rcp26/Monthly/CA_BCM_GISS_rcp26_Monthly_{}_{}.nc",
	"GISS_A1" : "https://cida.usgs.gov/thredds/fileServer/CA-BCM-2014/GISS_AOM_A1B/Monthly/CA_BCM_GISS_AOM_A1B_Monthly_{}_{}.nc", 
	"MPI_26" : "https://cida.usgs.gov/thredds/fileServer/CA-BCM-2014/MRI_rcp26/Monthly/CA_BCM_MRI_rcp26_Monthly_{}_{}.nc",
	"GFDL_B1" : "",
	"GFDF_A2" : ""
}

# Lookup table mapping bands to months, necessary since hte data is in hydrological years, band 1 = october, band 2 = november, band 3 = dec, etc.

band2mon = { 
			"1" : "10",
			"2" : "11",
			"3" : "12",
			"4" : "01",
			"5" : "02",
			"6" : "03",
			"7" : "04",
			"8" : "05",
			"9" : "06",
			"10" : "07",
			"11" : "08",
			"12" : "09"
}


# Main routine: (1) Download data, (2) extract each month, (3) reproject, (4) clip, 

# Set Params
years = range(2007,2100)
dataset = "GISS_26"
var = "aet"
data_dir = "../data/CA_BCM"
cvws = "../shape/cvws.shp"

def main():

	print("Processing {}".format(dataset))

	# Setup write dir(s)
	if not os.path.exists(data_dir):
		os.mkdir(data_dir)

	ds_dir = os.path.join(data_dir, dataset)

	if not os.path.exists(os.path.join(data_dir, dataset)):
		os.mkdir(ds_dir)

	ds_url = dl_urls[dataset] 

	for y in tqdm(years[:]):

		print("Processing {} products for {}".format(dataset,y))
		# Setup outfn 
		cdf_fn = os.path.join(os.path.join(data_dir, dataset, dataset+ "_" + var + "_"+ str(y) + ".nc"))
		# Get the URL for the ncdf file 
		dl_url = ds_url.format(var,y)
		# Execute the dl command using curl 
		dl_cmd = '''curl {} -o {}'''.format(dl_url, cdf_fn)
		print(dl_cmd)
		os.system(dl_cmd)
		# Unpack the yearly ncdf as tiffs 
		for k,v in band2mon.items():

			# account for hydrologic years (starting on oct of previous year)
			if k == "1" or k =="2" or k =="3":
				ystr = str(y-1)
			else:
				ystr = str(y)

			# Gdal translate ncdf --> gtiff 
			tiff_out = os.path.join(ds_dir,dataset+"_"+var+"_"+ystr+"_"+v+".tiff")
			print(tiff_out)
			nc2tiff_cmd = 'gdal_translate -b {} {} {}'.format(k,cdf_fn,tiff_out)
			os.system(nc2tiff_cmd)

			# Reproject files to Wgs 84
			tiff_out_rpj = os.path.join(ds_dir,dataset+"_"+var +"_"+ystr+"_"+v+"_rpj.tiff")
			rpj_cmd = "gdalwarp -t_srs 'EPSG:4326' {} {}".format(tiff_out,tiff_out_rpj)
			os.system(rpj_cmd)

			# Delete original tiff file so we can that write to that fn 
			os.remove(tiff_out)

			# Clip to CVWS, write to original tiff filename 
			clip_cmd = "gdalwarp -of GTiff -cutline {} -crop_to_cutline {} {}".format(cvws, tiff_out_rpj, tiff_out)
			os.system(clip_cmd)

			# Clean up unclipped reprojected file 
			os.remove(tiff_out_rpj)

		# Clean up nc file
		to_remove = [os.path.join(ds_dir,x) for x in os.listdir(ds_dir) if "rpj" in x or x.endswith(".nc") ]
		for fname in to_remove:
			if os.path.isfile(fname):
				os.remove(fname)


if __name__ == "__main__":	
	main()

