
#pip install geopandas matplotlib us

import geopandas as gpd
import matplotlib.pyplot as plt

# Load the shapefiles
counties = gpd.read_file('cb_2022_us_county_20m.shp')
print(counties.columns)

sample_list = ['56041', '36027', '36111', '06081']  # Example list

# Filter the counties
state_county_fips = counties['STATEFP']+counties['COUNTYFP']
filtered_counties = counties[state_county_fips.isin(sample_list)]
#print(filtered_counties)

# Get EPSG code of SHP file dynamically to account for other file types
print(counties.crs) # change this
filtered_counties = filtered_counties.to_crs(epsg='4269')

fig, ax = plt.subplots(figsize=(10,  10))
filtered_counties.plot(ax=ax, color='lightgrey')
ax.set_title('Filtered Counties Map')
plt.show()