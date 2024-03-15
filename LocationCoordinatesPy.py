import datetime
import json
import requests
import os
import glob

import LocalCountyPlot

shapefile = 'cb_2022_us_county_20m.shp'

FIPS_run = True
runType = 'semantic' #Options: 'semantic' (New Google Timeline Option Fall 2023 for month-by-month breakdown) or 'legacy' (Entire timeline in one bulk JSON file)
refresh_interval = 'monthly' #Options: 'monthly' or 'yearly'

timeThresholdMins = 20 #1 min = 60k ms; 1440 mins = 1 day
distThresholdDegs = 0.04 #0.02 is ~ 1 mile at average coordinates within the US

print('Welcome! Your location coordinate files are currently loading. This program has started at '+ str(datetime.datetime.now().strftime('%H:%M:%S')))

def runFile(input_file):
    print(f"Processing file: {input_file}")
    try:
        with open(input_file, 'r', encoding="utf-8") as file:
            data = json.load(file)
        print('File loaded successfully '+ str(datetime.datetime.now().strftime('%H:%M:%S')))
        return getResponse(data)
    except IOError:
        print('Could not find a file titled '+input_file + ' - Please verify file name and location and try again')
        
def loadMainFolderFile(base_path):
    if (runType == 'legacy'):
        runFile('Records.json')
    elif (runType == 'semantic'):
        semantic_history_path = os.path.join(base_path, 'Semantic Location History')
        directories = [d for d in os.listdir(semantic_history_path) if os.path.isdir(os.path.join(semantic_history_path, d))]
        year_folders = [d for d in directories if d.isdigit()]
        year_folders.sort()
        for year in year_folders:
            year_path = os.path.join(semantic_history_path, year)
            month_files = glob.glob(os.path.join(year_path, "*.json"))
            month_files.sort(key=sortMonthFiles)
            for month_file in month_files:
                monthly_counties, monthly_states = runFile(month_file)
                plot_data = {'title': str('US Counties Visited: '+ extractMonthFromPath(month_file)[0] + ' '+ extractMonthFromPath(month_file)[1]),
                             'refresh_info': str(monthly_states),
                             'epsg_format': 5070
                    }
                LocalCountyPlot.plotCounties(county_map, monthly_counties, plot_data)
    else:
        print('Run type not properly defined. Please set to \'semantic\' or \'legacy\'')

def sortMonthFiles(path):#This is Windows OS specific, for now
    month_extract = extractMonthFromPath(path)[0]
    return datetime.datetime.strptime(month_extract, '%B')

def extractMonthFromPath(path): #This is Windows OS specific, for now
    return path.split('\\')[-1].split('_')[1].split('.')[0], path.split('\\')[-1].split('_')[0].split('.')[0] #Pull the Month and Year
      
def getResponse(data):
    APISuccessful, APIFailure = 0, 0
    previousTime, previousLat, previousLong = 0, 0, 0
    monthYear = None
    counties = set()
    states = set()
    status_codes = set()
    #for item in data['locations']:
    for place in data['timelineObjects']:
        if 'placeVisit' in place:
            try:
                lat = place['placeVisit']['location']['latitudeE7']
                #lat = item['latitudeE7']
                long = place['placeVisit']['location']['longitudeE7']
                #long = item['longitudeE7']
                lat = addDecimal(lat, 7)
                long = addDecimal(long, 7)
            except:
                #print(place['placeVisit'])
                continue
        
            try: #Because sometimes there's milliseconds, and sometimes there isn't
                #latestTime = datetime.datetime.strptime(place['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
                latestTime = datetime.datetime.strptime(place['placeVisit']['duration']['startTimestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                #latestTime = datetime.datetime.strptime(place['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
                latestTime = datetime.datetime.strptime(place['placeVisit']['duration']['startTimestamp'], "%Y-%m-%dT%H:%M:%SZ")
            if (monthYear != (latestTime.strftime('%B %Y'))):
                monthYear = latestTime.strftime('%B %Y')
                print (monthYear)
        
            if ((abs(lat - previousLat) < distThresholdDegs) or (abs(long - previousLong) < distThresholdDegs)):
                continue
            #print('Distance Threshold Surpassed')

            latestTime = int(latestTime.timestamp()) #Running distance calculation first because of time to compute
            if ((latestTime - previousTime) < (timeThresholdMins * 60)):
                continue 
            #print('Threshold surpassed at timestamp '+ str(datetime.datetime.fromtimestamp(latestTime/1000.0)))

            previousTime = latestTime
            previousLat = lat
            previousLong = long
        
            try:
                url = f"https://geo.fcc.gov/api/census/block/find?latitude={lat}&longitude={long}&censusYear=2020&showall=true&format=json"
                response = requests.get(url)
                response.raise_for_status()
                response_data = response.json()
                APISuccessful += 1
    
                county, state = getCounty(response_data)
                if county == None:
                    continue    
                if county not in counties:
                    counties.add(county)
                    print('County added to list: ' +county)
                if state not in states:
                    states.add(state)
                
            except requests.HTTPError as ex:
                #print('Error with response: '+ str(ex))
                status_codes.add(response.status_code)
                APIFailure += 1
            except requests.Timeout:
                status_codes.add(response.status_code)
                print('Request Timeout for item '+ str(place))
                APIFailure += 1
    #print('API load finished at '+ str(datetime.datetime.now().strftime('%H:%M:%S')))
    #print('API called '+ str(APISuccessful)+ ' times')
    #print('API failed '+ str(APIFailure)+ ' times')
    if (len(status_codes) > 0):
        print('Encountered error codes: '+str(status_codes))
    return counties, states

def addDecimal(num, decimal_place):
   try:
       n_str = str(abs(num)).rjust(7, '0') #Pad zeros to ensure correct length, but just took the abs of this so flip back
       n_str = n_str[:-decimal_place] + '.' + n_str[-decimal_place:]
       n_float = float(n_str)
       if num < 0:
           n_float = n_float * -1
       return n_float
   except:
       print('Problematic decimal conversion on value '+ str(num))
       return 0

def getCounty(input):
    try:
        if (FIPS_run):
            return input['County']['FIPS'], input['State']['code']#Two letter state abbreviation
        else:
            return input['County']['name'].replace(' ', '_') + '__' +input['State']['code']
    except:
        #print('Coordinates not matching a US county')
        return None
    
def getState(input): ##maybe just delete this and merge with above
    try:
        return input['State']['code'] #Two letter state abbreviation
    except:
        #print('Coordinates not matching a US state')
        return None
    
def formatOutput(countySet):
    countyCleanup = cleanupCountyNames(countySet)
    print(countyCleanup)
    formattedCounties = str(', '.join(f'"{item}"' for item in countyCleanup))
    with open('InputTemplate.txt', 'r') as file:
        text = file.read()
        text = text.replace('_ALL_COUNTIES_', formattedCounties)
    with open('OutputTemplate.txt', 'w') as file:
        file.write(text)
    print('Output file saved at '+ str(datetime.datetime.now().strftime('%H:%M:%S')))
    
def cleanupCountyNames(countySet):
    
    #1 - Remove keyword due to API mismatches, such as 'County' or 'Borough'
    with open ('KeywordReplacement.txt', 'r') as file:
        removeWords = file.read()
    removeWords = set(removeWords.split('\n'))
    cleanCountySet = {
        '_'.join(word for i, word in enumerate(string.split('_')) if word not in removeWords or i == 0)
        for string in countySet}
    
    #2 - Swap out known exceptions, such as 'District_of_Columbia' with 'Washington'
    with open('KnownExceptions.json', 'r') as file:
        exceptions = json.load(file)
    countySet = {exceptions[county] if county in exceptions else county for county in countySet}

    #3 - Remove non-alpha characters, such as 'Miami-Dade' or 'St. Louis'
    cleanCountySet = {''.join('_' if not char.isalpha() and char != '_' else char for char in string) for string in cleanCountySet}

    return cleanCountySet


county_map = LocalCountyPlot.loadShapeFile(shapefile)
base_path = 'Location History (Timeline)'
loadMainFolderFile(base_path)

#allCounties = runFile('Records.json') #Will return list of counties
#print('Number of unique US Counties: '+ str(len(allCounties)))


if FIPS_run:
    #print(allCounties)
    print()
else:
    formatOutput(allCounties)
    
#plotVars = {'allCounties': allCounties}
#exec(open('LocalCountyPlot.py').read(), plotVars) #Logic handled in separate file to generate map, allowing both local or new plots


#TODO
#Output to user the new regions (States?) visited that interval/month in a list on the figure
#Clean out one-off locations (flying or location spoofing) from Google Maps directly
#Determine options for mapping pre-2017 counties (Prior to Google Timeline History being logged)
#Create separate versions for US (by county) and international (by regions TBD)

#OPTIONS
#Look at options for color-coding map based on timeframe of when first/last visied
##As of Fall 2023, Google Takeout changed their output files to be separated by year or month, so this is an easy possibility
##Could even load one file at a time and start refreshing the map real time by month for better UX
#Look at options for color-coding based on frequency of counties visited. Need to differentiate by time versus number of responses. May majorly increase runtime

#WAY LATER
#Auto-download my google takout file to cloud storage
#Automate the running of this program and send the result to my email monthly