import datetime
import json
import requests

timeThresholdMins = 15 #1 min = 60k ms; 1440 mins = 1 day
distThresholdDegs = 0.015 #0.02 is ~ 1 mile at average coordinates within the US

print('Program started at '+ str(datetime.datetime.now().strftime('%H:%M:%S')))

def runFile():   
    #with open('Mini_sample_data.json', 'r') as file:
    with open('Records.json', 'r') as file:
        data = json.load(file)
    print('File loaded at '+ str(datetime.datetime.now().strftime('%H:%M:%S')))
    return getResponse(data)
    
def getResponse(data):
    APISuccessful, APIFailure = 0, 0
    previousTime, previousLat, previousLong = 0, 0, 0
    monthYear = None
    counties = set()
    status_codes = set()
    for item in data['locations']:
        lat = item['latitudeE7']
        long = item['longitudeE7']
        lat = addDecimal(lat, 7)
        long = addDecimal(long, 7)
        
        try: #Because sometimes there's milliseconds, and sometimes there isn't
            latestTime = datetime.datetime.strptime(item['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            latestTime = datetime.datetime.strptime(item['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
        if (monthYear != (latestTime.strftime('%B %Y'))):
            monthYear = latestTime.strftime('%B %Y')
            print (monthYear)
        
        #print('Lat: '+str(lat)+ '  Long: '+str(long))
        if ((abs(lat - previousLat) < distThresholdDegs) or (abs(long - previousLong) < distThresholdDegs)):
            continue
        #print('Distance Threshold Surpassed')

        latestTime = int(latestTime.timestamp()) #Try flipping the order of the time and location thresholds to see which one is faster to compute, and run that first
        if ((latestTime - previousTime) < (timeThresholdMins * 60)):
            continue 
        #print('Threshold surpassed at timestamp '+ str(datetime.datetime.fromtimestamp(latestTime/1000.0)))
        #print('')

        previousTime = latestTime
        previousLat = lat
        previousLong = long
        
        if sendAPI is False:
            APISuccessful += 1
            continue
        try:
            url = f"https://geo.fcc.gov/api/census/block/find?latitude={lat}&longitude={long}&censusYear=2020&showall=true&format=json"
            response = requests.get(url)
            response.raise_for_status()
            response_data = response.json()
            APISuccessful += 1
    
            county = getCounty(response_data)
            if county == None:
                continue    
            if county not in counties:
                counties.add(county)
                print('*** County added to list: ' +county + ' ***')
        except requests.HTTPError as ex:
            #print('Error with response: '+ str(ex))
            status_codes.add(response.status_code)
            APIFailure += 1
        except requests.Timeout:
            status_codes.add(response.status_code)
            print('Request Timeout for item '+ str(item))
            APIFailure += 1
    print('API load finished at '+ str(datetime.datetime.now().strftime('%H:%M:%S')))
    print('API called '+ str(APISuccessful)+ ' times')
    print('API failed '+ str(APIFailure)+ ' times')
    if (len(status_codes) > 0):
        print('Encountered error codes: '+str(status_codes))
    return counties

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
        return input['County']['name'].replace(' ', '_') + '__' +input['State']['code']
    except:
        #print('Coordinates not matching a US county')
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


allCounties = runFile() #Will return list of counties
print('Number of unique US Counties: '+ str(len(allCounties)))
formatOutput(allCounties)

#exec(open("MapchartWebBot.py").read()) #Temporarily tried connecting to a web bot script to learn how that works, but preferrably want to get away from using any existing site in the long term




#TODO - PreAPI Call
#Degree threshold to round and decrease the number of API calls, Run as an OR with the time threshold
#DONE - Skip threshold based to decrease duplicates (maybe leverage the timestampMs field for locations under ~30 mins apart)
#DONE - Timestamp each of the sessions for update
#HOLD - Really rough boundaries for US-only calls. Longitude < -70e7. Latitude between 20e7 and 70e7

#TODO - PostAPI Call
#IN PROGRESS - Review for mismatched county names and add to known exceptions file. Convert API counties to exceptions if they exist
#IN PROGRESS - Review keywords to remove, such as 'county', 'borough', 'municipality'
#DONE - Convert non-alphanumeric characters to underscores (St. Louis, Prince George's, Miami-Dade)
#DONE - Verify success, throw away errors (maybe log them for a bit first)
#DONE - Create blank array for county+state. Check if county.name + state.name combination already present, if not push
#DONE - Look into array alternatives (numPy arrays for example) to increase performance. Just using sets

#LATER
#Add previous pre-2017 counties in a JSON (have them color-coded separate)
#DONE - Format the output file
#Look into color options based on timeframe (going to be hard if using sets)
#Clean out one-off locations (flying or location spoofing) from Google Maps directly
#Save the webpage for https://www.mapchart.net/usa-counties.html locally
#Research options with https://public.opendatasoft.com/explore/dataset/georef-united-states-of-america-county/api/?flg=en-us&disjunctive.ste_code&disjunctive.ste_name&disjunctive.coty_code&disjunctive.coty_name&sort=year&location=6,35.49646,-82.88086&basemap=jawg.light

#WAY LATER
#Auto-download my google takout file to my local storage (or a web server)
#Automate the running of this program
#Open the website and upload the response file automatically
#Send the result to my email monthly