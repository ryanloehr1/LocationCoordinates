
#pip install geopandas matplotlib us

import geopandas as gpd

# Load the shapefiles
counties = gpd.read_file('cb_2022_us_county_20m.shp')

# Assuming 'your_list' contains the official county codes
your_list = ['56041', '56043', '56045']  # Example list

print(counties.columns)
input("Press Enter to continue...")

# Filter the counties
filtered_counties = counties[counties['COUNTYFP'].isin(your_list)]

import matplotlib.pyplot as plt

# Plot the map
fig, ax = plt.subplots(1,  1)
filtered_counties.plot(ax=ax, color='red', linewidth=0.8, edgecolor='0.8')

# Set the title and labels
ax.set_title('US Counties Map')
ax.set_axis_off()

# Show the plot
plt.show()

plt.savefig('us_counties_map.png')