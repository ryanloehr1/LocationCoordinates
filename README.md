# LocationCoordinates: A Google Timeline History Visualization

This program is intended to visualize travel history by leveraging locations tracked in Google Maps
For this to work:
* Users must be set up to have location history enabled on their account: https://support.google.com/maps/answer/3118687?hl=en
* To save this history, navigate to https://takeout.google.com/ and download 'Location History (Timeline)' in JSON format
* The file will be emailed to your account email. Unzip and save the 'Records.JSON' file to the same folder as the python LocationCoordinates solution

Notes for App v1.0 (in main branch):
* The basic setup for the first iteration of this app outputs a txt file to then use with an existing 3rd party website: Mapchart.net

Notes for the Geopandas_FIPS branch:
* This is in progress for plotting the map of visited locations locally using SHP files, eliminating the dependency on uploading the file to a website
