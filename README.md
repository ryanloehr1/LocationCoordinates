# LocationCoordinates: A Google Timeline History Visualization

This program is intended to visualize travel history by leveraging locations tracked in Google Maps
For this to work:
* Users must be set up to have location history enabled on their account: https://support.google.com/maps/answer/3118687?hl=en
* To save this history, navigate to https://takeout.google.com/ and download 'Location History (Timeline)' in JSON format
* The file will be emailed to your account email specified. Unzip and save the 'Records.JSON' file to the same folder as the python LocationCoordinates solution

Notes for App v1.0:
* The basic setup for the first iteration of this app outputs a txt file to then use with an existing 3rd party website: Mapchart.net
* Future iterations of the app will aim to make the program self-sufficient without the use of an external website. Researching options for importing shape files and outputting files to user locally
