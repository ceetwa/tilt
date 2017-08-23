#!/usr/bin/python
import argparse
import blescan
import sys
import requests
import datetime
import time
import bluetooth._bluetooth as bluez
import pygame
import os

active = True

#Assign uuid's of various colour tilt hydrometers. BLE devices like the tilt work primarily using advertisements. 
#The first section of any advertisement is the universally unique identifier. Tilt uses a particular identifier based on the colour of the device
colours = {'red': 'a495bb10c5b14b44b5121370f02d74de', 'green': 'a495bb20c5b14b44b5121370f02d74de', 'black': 'a495bb30c5b14b44b5121370f02d74de',
		'purple': 'a495bb40c5b14b44b5121370f02d74de', 'orange': 'a495bb50c5b14b44b5121370f02d74de', 'blue': 'a495bb60c5b14b44b5121370f02d74de',
		'yellow': 'a495bb70c5b14b44b5121370f02d74de', 'pink': 'a495bb80c5b14b44b5121370f02d74de'}

#The default device for bluetooth scan. If you're using a bluetooth dongle you may have to change this.
dev_id = 0

#function to calculate the number of days since epoch (used by google sheets)
#In python time.time() gives number of seconds since epoch (Jan 1 1970).
#Google Sheets datetime as a number is the number of days since the epoch except their epoch date is Jan 1 1900
def sheetsDate(date1):
    temp = datetime.datetime(1899, 12, 30)
    delta=date1-temp
    return float(delta.days) + (float(delta.seconds) / 86400)

#scan BLE advertisements until we see one matching our tilt uuid
def getdata(colour, beerName):
    try:
        sock = bluez.hci_open_dev(dev_id)

    except:
        print("error accessing bluetooth device...")
        sys.exit(1)

    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)

    gotData = 0
    while (gotData == 0):

        returnedList = blescan.parse_events(sock, 10)

        for beacon in returnedList: #returnedList is a list datatype of string datatypes seperated by commas (,)
            output = beacon.split(',') #split the list into individual strings in an array
            if output[1] == colours[colour]: #Change this to the colour of you tilt
                tempf = float(output[2]) #convert the string for the temperature to a float type

                gotData = 1

                tiltTime = sheetsDate(datetime.datetime.now())
                tiltSG = float(output[3])/1000
                tiltTemp = tempf
                tiltColour = colour.upper()
                tiltBeer = beerName #Change to an identifier of a particular brew

    #assign values to a dictionary variable for the http POST to google sheet
    data=     {
            'Timepoint': tiltTime,
            'SG': tiltSG,
            'Temp': tiltTemp,
            'Color': tiltColour,
            'Beer': tiltBeer,
            'Comment': "From RasPi cron"
            }
    blescan.hci_disable_le_scan(sock)
    return data
        

def main():

    global screen

    parser = argparse.ArgumentParser(description='Read all Tile hydrometers in the vacinity and upload data from the specified colour to THE CLOUD!')
    parser.add_argument('colour', nargs=1,
                   help='colour of Tilt to read')
    parser.add_argument('name', nargs=1,
                   help='Beer name, including the comma and number')
    parser.add_argument('url', nargs=1,
                   help='URL of the Tilt spreadsheet app')
 
    args = parser.parse_args()
    print(args.colour[0])
    print(args.name[0])
    updateSecs = 600 #time in seconds between updating the google sheet
    
    timestamp = time.time() #Set time for beginning of loop
    updateTime = timestamp + updateSecs #Set the time for the next update to google sheets

    
    data = getdata(args.colour[0], args.name[0])
        
    print(data)
    if active:
        r = requests.post(args.url[0], data)
        print(r.text)
            


if __name__ == "__main__": #dont run this as a module
    main()

