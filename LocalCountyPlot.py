#pip install geopandas matplotlib us

import geopandas as gpd
import matplotlib.pyplot as plt

def loadShapeFile(file_name):
    file = gpd.read_file(file_name)
    return file

# Filter the counties
def plotCounties(counties, projection= None):
    if projection == None:
        projection = str(counties.crs).replace("EPSG:","") #if no projection defined, default to layout listed as "CRS" in the SHP file
    state_county_fips = counties['STATEFP']+counties['COUNTYFP']
    visited_counties = counties[state_county_fips.isin(county_list)]
    #print(filtered_counties)
    visited_counties = visited_counties.to_crs(epsg=projection)

    fig, ax = plt.subplots(figsize=(10,  10))
    counties.to_crs(epsg=projection).plot(ax=ax, color='lightgrey', alpha=0.5)  # Plot all counties for an outline
    visited_counties.plot(ax=ax, color='red', alpha=1)  # Highlight visited counties on top
    ax.set_title('Filtered Counties Map')
    plt.show()

local_list = {'34039', '35015', '44007', '15009', '06075', '25027', '54061', '34003', '25013', '25021', '36021', '06085', '36119', '55039', '01127', '24033', '53067', '36071', '16001', '36087', '25025', '36111', '11001', '36081', '06077', '48453', '06073', '09001', '08123', '02122', '36061', '06037', '50015', '36027', '49055', '08013', '08117', '32003', '06081', '15001', '51013', '08089', '53011', '24003', '24005', '12011', '47037', '06001', '36039', '25005', '17031', '23011', '25009', '09003', '36047', '12086', '08031', '42003', '34013', '27123', '53033', '24015', '51059', '04005', '24027', '36079'}

if 'allCounties' in locals(): #allows for counties to be passed in from another python script, but default to a sample list if not
    county_list = allCounties
else:
    county_list = local_list

shapefile = 'cb_2022_us_county_20m.shp'
counties = loadShapeFile(shapefile)
plotCounties(counties, 5070)


#Need to play around with different EPSG projections. Standard options:
# 5070: Albers Equal Area Conic
# 5072: Lambert Conformal Conic
# 3395: Mercator
# 6933: Modified Stereographic
