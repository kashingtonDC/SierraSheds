# Sierra Nevada Watersheds
Use notebook 00 to demo DEM + flow routing algorithms + reservoir locations to delineate upstream catchments; key for reservoir operations, agricultural, and domestic water supply in California
### Get the data and preproces
* Use Digital Elevation Models (DEMs) and flow routing algorithms
* Shuttle radar topography mission (SRTM) DEMS downloaded from: http://srtm.csi.cgiar.org/srtmdata/
* Merged by running from command line:
`gdal_merge.py -o srtm_dem.tif srtm_12_04.tif srtm_12_05.tif srtm_13_04.tif srtm_13_05.tif srtm_13_06.tif`

* Clipped by running from command line:
`gdalwarp -cutline ../shape/cvws.shp -crop_to_cutline srtm_dem.tif hu6_srtm_dem.tif`

### Follow instructions / demo in `code/sierra_wshed_delineation.ipynb`
