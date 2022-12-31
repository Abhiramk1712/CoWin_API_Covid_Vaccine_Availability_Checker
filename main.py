import requests
from optparse import OptionParser
import sys
import datetime
import time
import os
from playsound import playsound


class Main:
    def __init__(self):
        self.dateFlag = False
        self.availableFlag = False

    def clearConsole(self):
        # For clearing the command prompt screen
        command = 'clear'
        if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
            command = 'cls'
        os.system(command)

    def getOptions(self):
        parser = OptionParser()

        # ask options
        parser.add_option("-d", "--district", dest="district", help="Select district number")
        parser.add_option("-p", "--pin", dest="pincode", help="Enter pincode")
        parser.add_option("-a", "--age", dest="age", help="Enter min age: 18 or 45")
        parser.add_option("-c", "--date", dest="date", help="Enter date in dd-mm-yyyy format")
        parser.add_option("-v", "--vaccine", dest="vaccine", help="Enter vaccine name 'COVAXIN', 'COVISHIELD', 'SPUTNIK'")
        parser.add_option("-n", "--dose", dest="dose", help="Enter dose no: 1 or 2")
        parser.add_option("-i", "--interval", dest="interval", help="Enter time interval in minutes", default="2")

        (options, args) = parser.parse_args()
        return options


    def inputValidation(self, options):

        def ifConditionsNotSatisfied(text):
            # if conditions are not satisfied execute this
            print(text)
            print("[+] Use -h or --help for help")
            sys.exit()

        # Verifying that only one in pincode or distirct options are given
        if options.district is not None and options.pincode is not None:
            ifConditionsNotSatisfied("[-] Please give only District or Pincode")

        # Verifying that atleast one from pincode or district options are given
        if options.district is None and options.pincode is None:
            ifConditionsNotSatisfied("[-] Please give any one District or Pincode")

        # Verifying if proper vaccine is given or not
        if options.vaccine is None or options.vaccine not in ['COVAXIN', 'COVISHIELD', 'SPUTNIK']:
            ifConditionsNotSatisfied("[-] Please enter vaccine 'COVAXIN','COVISHIELD', 'SPUTNIK'")

        # Correcting the name for sputnik
        if options.vaccine == "SPUTNIK":
            options.vaccine = "SPUTNIK V"

            # Verifying the dose number option
        if options.dose is None or int(options.dose) not in [1, 2]:
            ifConditionsNotSatisfied("[-] Please enter dose number 1 or 2")
        elif int(options.dose) == 1:
            options.dose = "available_capacity_dose1"
        elif int(options.dose) == 2:
            options.dose = "available_capacity_dose2"

        # Verifying the age option
        if options.age is None or int(options.age) not in [18, 45]:
            ifConditionsNotSatisfied("[-] Please enter age 18 or 45")

        # verifying if the date option is given
        if options.date is None:
            self.dateFlag = False
            options.date = datetime.datetime.now().strftime("%d-%m-%y")
        else:
            self.dateFlag = True


        # Verifying the interval option is a number
        if not options.interval.isnumeric():
            ifConditionsNotSatisfied("[-] Please enter a number as interval")


    def callFunction(self, options):
        # For calling the functions based on user input

        if options.district is not None:
            # if district option is given
            calDisUrl = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=" + str(options.district) + "&date=" + str(options.date)
            self.calenderByX(calDisUrl, options)

        if options.pincode is not None:
            # if pincode option is given
            calPinUrl = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=" + str(options.pincode) + "&date=" + str(options.date)
            self.calenderByX(calPinUrl, options)


    def calenderByX(self, url, options):
        # The function where we get the data and format it as we need

        def outputCalByX(finalDict2, session2):
            # For printing the output
            print("\n\n")
            print("Name : ", finalDict2["name"])
            print("District : ", finalDict2["district_name"])
            print("State : ", finalDict2["state_name"])
            print("Pincode : ", finalDict2["pincode"])
            print("Date : ", session2["date"])
            print("Age : ", session2["min_age_limit"])
            print("Vaccine : ", session2["vaccine"])
            print("Availability : ", session2[options.dose])

        response = requests.get(url)
        responseJson = response.json()

        # Formatting the data based on the user's input
        for finalDict in responseJson["centers"]:
            for session in finalDict["sessions"]:
                if not self.dateFlag and session[options.dose] > 0 and session["vaccine"] == options.vaccine and session["min_age_limit"] == int(options.age):
                    self.availableFlag = True
                    outputCalByX(finalDict, session)

                elif self.dateFlag and session[options.dose] > 0 and session["vaccine"] == options.vaccine and session["min_age_limit"] == int(options.age) and session["date"] == options.date:
                    self.availableFlag = True
                    outputCalByX(finalDict, session)

                else:
                    self.availableFlag = False



obj = Main()
opt = obj.getOptions()
obj.inputValidation(opt)

try:
    while True:
        # Running the code for particular interval until the user stops the execution
        obj.callFunction(opt)
        if obj.availableFlag:
            playsound("resources/sounds/copy of beep.wav")
        time.sleep(int(opt.interval)*60)
        obj.clearConsole()
except KeyboardInterrupt:
    print("\n\n[-] Quitting.....")
