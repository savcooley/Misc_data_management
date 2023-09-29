# -*- coding: utf-8 -*-
"""
GEDI L4A granule retrieval - https://github.com/ornldaac/gedi_tutorials/blob/main/1_gedi_l4a_search_download.ipynb
"""
"""
# ImportError: The 'read_file' function requires the 'pyogrio' or 'fiona' package, but neither is installed or imports correctly.
# Importing fiona resulted in: No module named 'fiona'
# Importing pyogrio resulted in: No module named 'pyogrio'

#conda install -c conda-forge geopandas
#conda remove geopandas fiona
#pip install geopandas fiona

##Because I did not want to uninstall geopandas, I solved the issue by upgrading fiona via pip
#pip install --upgrade fiona

"""

import requests
import datetime as dt 
import pandas as pd
import geopandas as gpd
import shapely.geometry
from shapely.geometry import MultiPolygon, Polygon, box, LinearRing
#from shapely.ops import orient

doi = '10.3334/ORNLDAAC/2056'# GEDI L4A DOI 

# CMR API base url
cmrurl='https://cmr.earthdata.nasa.gov/search/' 

doisearch = cmrurl + 'collections.json?doi=' + doi
response = requests.get(doisearch)
response.raise_for_status()
concept_id = response.json()['feed']['entry'][0]['id']

print(concept_id)


bound = (7.7, -79, -16,-47) # # Amazon bounding box
#bound = (-12.73565813040767,-60.14364444330287,-18.802240528224388,-52.62487999261823) # SE Amazon

# time bound
start_date = dt.datetime(2019, 4, 17) # specify your own start date
end_date = dt.datetime(2023, 1, 31)  # specify your end start date

# CMR formatted start and end times
dt_format = '%Y-%m-%dT%H:%M:%SZ'
temporal_str = start_date.strftime(dt_format) + ',' + end_date.strftime(dt_format)

# CMR formatted bounding box
bound_str = ','.join(map(str, bound))

page_num = 1
page_size = 2000 # CMR page size limit

granule_arr = []



while True:
    
    # defining parameters
    cmr_param = {
        "collection_concept_id": concept_id, 
        "page_size": page_size,
        "page_num": page_num,
        "temporal": temporal_str,
        "bounding_box[]": bound_str
    }
    
    granulesearch = cmrurl + 'granules.json'

    response = requests.get(granulesearch, params=cmr_param)
    response.raise_for_status()
    granules = response.json()['feed']['entry']
    
    if granules:
        for g in granules:
            granule_url = ''
            granule_poly = ''
            
            # read file size
            granule_size = float(g['granule_size'])
            
            # reading bounding geometries
            if 'polygons' in g:
                polygons= g['polygons']
                multipolygons = []
                for poly in polygons:
                    i=iter(poly[0].split (" "))
                    ltln = list(map(" ".join,zip(i,i)))
                    multipolygons.append(Polygon([[float(p.split(" ")[1]), float(p.split(" ")[0])] for p in ltln]))
                granule_poly = MultiPolygon(multipolygons)
            
            # Get URL to HDF5 files
            for links in g['links']:
                if 'title' in links and links['title'].startswith('Download') \
                and links['title'].endswith('.h5'):
                    granule_url = links['href']
            granule_arr.append([granule_url, granule_size, granule_poly])
               
        page_num += 1
    else: 
        break

# adding bound as the last row into the dataframe
# we will use this later in the plot
b = list(bound)
granule_arr.append(['bound', 0, box(b[0], b[1], b[2], b[3])]) 

# creating a pandas dataframe
l4adf = pd.DataFrame(granule_arr, columns=["granule_url", "granule_size", "granule_poly"])

# Drop granules with empty geometry
l4adf = l4adf[l4adf['granule_poly'] != '']

print ("Total granules found: ", len(l4adf.index)-1)
print ("Total file size (MB): ", l4adf['granule_size'].sum())




l4adf.head()

# We can now plot the bounding geometries of the granules (shown with green lines in the figure below) using geopandas. The bounding box (of Brazil) is plotted in red color.

gdf = gpd.GeoDataFrame(l4adf, geometry=l4adf.granule_poly)
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
base = world.plot(color='white', edgecolor='black', figsize  = (7, 7))

# last row contains the bounding box (Red)
#ax= gdf[-1:].plot(ax=base, color='white', edgecolor='red', alpha=0.5)

# all but the last row contains granule bounding geometry (Green)
#ax= gdf[:-1].plot(ax=base, color='green', edgecolor='green', alpha=0.7)

#minx, miny, maxx, maxy = gdf[-1:].geometry.total_bounds
#ax.set_xlim(minx-1, maxx+1)
#ax.set_ylim(miny-1, maxy+1)


