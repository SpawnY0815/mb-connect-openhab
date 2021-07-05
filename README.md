# mb-connect-openhab
A Python script to integrate the Mercedes-Benz API (https://developer.mercedes-benz.com) to openHAB (https://www.openhab.org/)

With this script it is possible to get data from your own vehicle via the Mercedes-Benz API. All used APIs in this script are currently free of charge. Some APIs have call limits (for example vehicle images).
The script can be called in different ways (openHAB exec binding, cronjob, by hand) and stores the received data in the openHAB items.
A timestamp (openHAB DateTime item) is also filled for each value, if a corresponding *_ts item was created.
Take into account that the data is fetched from the Merceds-Benz server and not directly from your vehicle. This means that some values for example a door can be a few days old because it was not opened or closed in this time. If some data is not available, please check the vehicle compatibility on the Mercedes me page. If your vehicle should provide the data, try first to drive with the vehicle a little bit, move the windows, ... ,  to load new data on the mercedes server.

openHAB Community: https://community.openhab.org/t/mercedes-benz-integration/117795


### > ! Never show your credentials to others ! <


## min requirements:
* openHAB 2 / 3 installed
* openHAB REST installed
* python 3 installed
* pip installed
* Mercedes-Benz ME User Account
* Mercedes-Benz Devoloper Project
* Your Mercedes-Benz Vehicle ID (VIN) 
    * How to find the VIN? -> https://community.openhab.org/t/mercedes-benz-integration/117795/18?u=spawny0815
* Know your openHAB root URL/IP and port. For example http://openhabian:8080 or http://192.168.1.50:8080/


## optional requirements:
* It makes sense to use an openHAB persistence service. Otherwise you have to enter the credentials after each reboot/restart and start the auth process again. (https://openhab.org/docs/tutorial/persistence.html)
* openHAB Exec Binding (https://openhab.org/addons/bindings/exec/) to run the script from an openHAB item/rule.
* MAP transformation (https://openhab.org/docs/configuration/transformations.html)


# Instructions

1. Copy the files from this repository into openhab conf directory
2. Open the "mb-connect_auth.html" (REDIRECT_URL) in your browser
    * Example: "http://openhabian:8080/static/mb-connect/mb-connect_auth.html" or "http://192.168.10.50:8080/static/mb-connect/mb-connect_auth.html" (with you openHAB IP or dns name)
3. Scroll to the "Copy redirect url" button and click it to copy the redirect url to your clipboard


## Mercedes-Benz Project
1. Open web browser https://developer.mercedes-benz.com/
2. Use you Mercedes Benz ME login data to login to developers platform
3. Select "CONSOLE" in the navigation
4. Select "+ ADD NEW PROJECT"
5. Give the PROJECT a name, this needs to be unique
    * Like: "openhab-yourname-yourvehiclename", "openhab-chris-eclass".
    * ***!Please includ the word "openhab" in your project name to allow the mercedes team to categorize it!***
6. Set your "Redirect URL". Paste the previously copied redirect url here
7. Give business purpose
    * Example: "Connect my car to the openHAB smarthome system"
8. Select "APIs" in the navigation
9. SUBCRIBE to APIs matching your vehicle (use BYOCAR and GET FOR FREE)
    * Fuel Status BYOCAR
    * Pay As You Drive Insurance BYOCAR
    * Vehicle Lock Status BYOCAR
    * Vehicle Status BYOCAR
    * Electric Vehicle Status BYOCAR (only electric or hybrid car)
    * Vehicle Images (Optional)
10. Select "CONSOLE" in the navigation
11. Copy Client_ID, Client_Secret, API Key (optional) data.

## Start the authentication process
1. Open the  mb-connect_auth.html (REDIRECT_URL) in your browser
2. Feed your openHAB items with your Client_ID, Client_Secret, Vehicle ID, API Key directly on the website
3. set your scope items according to your Mercedes-Benz App subscriptions.
4. (optional) set your image items according to your needs.
5. Check again if your requirements fit and click on the button "Authenticate"
6. Log in with your "Mercedes Benz me" account in the following dialog and allow access
7. You should be redirected back to your REDIRECT_URL. There your AUTH_CODE has now been captured and the message "New Mercedes Benz API Auth Code successfully saved to openHAB!" should appear.
8. Check your openHAB item "mbc_auth_code" for new data.

## Setup openHAB
1. Open the mb-connect.py file in OPENHABCONF/scrips/mb-connect/mb-connect.py and change the REDIRECT_URL to your setting. It must be the same as entered in the Mercedes-Benz app!
2. Go to OPENHABCONF/scrips/mb-connect/ in your terminal and run: "pip install -r requirements.txt"
    * Example: cd /etc/openhab/scripts/mb-connect/ && pip3 install -r requirements.txt

## Run the script
1. In terminal run "python3 OPENHABCONF/scrips/mb-connect/mb-connect.py --data" to get all the subscribed data from the mercedes server.
    * Example: python3 /etc/openhab/scripts/mb-connect/mb-connect.py --data
1. Check your openHAB items for incoming data.
* To run the script "--data" automatically you can now configure the exec binding and create a rule in your preferred rule engine (Example: mb-connect.rules, do not forget to enter the command in the ***"misc/exec.whitelist"*** file)

## Vehicle Images (optional)
1. In terminal run "python3 OPENHABCONF/scrips/mb-connect/mb-connect.py --get_images" to retrieve all available vehicle images matching your settings of the oh image items from the Mercedes server.
    1. HINT: The vehicle images API is available only as a trial version with the **limit of 5 free calls**. The limit is bound to the project.
    1. The default file path for the download is: openhabconf/html/mb-connect/vehicle_images/
    1. You can change the image name prefix in the scipt if needed


## Available data (depending on the vehicle)

Item Typ | Name | Description
------------- | ------------- | -------------
 | **Fuel Status API** | 
Number | rangeliquid | Liquid fuel tank range
Number | tanklevelpercent | Liquid fuel tank level
 | | 
 | **Vehicle Status API** | 
Contact | decklidstatus | Deck lid latch status opened/closed state
Contact | doorstatusfrontleft | Status of the front left door
Contact | doorstatusfrontright | Status of the front right door
Contact | doorstatusrearleft | Status of the rear left door
Contact | doorstatusrearright | Status of the rear right door
Switch | interiorLightsFront | Front light inside
Switch | interiorLightsRear | Rear light inside
Number | lightswitchposition | Rotary light switch position
Switch | readingLampFrontLeft | Front left reading light inside
Switch | readingLampFrontRight | Front right reading light inside
Number | rooftopstatus | Status of the convertible top opened/closed
Number | sunroofstatus | Status of the sunroof
Number | windowstatusfrontleft | Status of the front left window
Number | windowstatusfrontright | Status of the front right window
Number | windowstatusrearleft | Status of the rear left window
Number | windowstatusrearright | Status of the rear right window
 | | 
 | **Vehicle Lock Status API** | 
Switch | doorlockstatusdecklid | Lock status of the deck lid
Number | doorlockstatusvehicle | Vehicle lock status
Switch | doorlockstatusgas | Status of gas tank door lock
Number | positionHeading | Vehicle heading position
 | | 
 | **Electric Vehicle Status API** | 
Number | soc | Displayed state of charge for the HV battery
Number | rangeelectric | Electric range
 | | 
 | **Pay As You Drive Insurance API** | 
Number | odo | Odometer
 | | 
*each listed value also has a timestamp | | 


# Changelog
## v1.1
1. Vehicle images
    1. added new openHAB items for image settings
    1. added overview on the auth page
    1. added a function to download the images to your openHAB directory
    1. added a check for the needed auth key from your MB project
    1. added the option to change the name prefix and download path of the images
1. added a check for the correct redirect url in the auth process
1. added new openHAB item for redirect url
1. updated the readme file (app=project, better description, ..)
1. better error description in the script and website
1. You can now customize your itemprefix according to your needs
1. added a oh3 mainui widget to the examples (thanks to muelli1967)
1. Auth website
    1. mouseover tooltips for auth data items
    1. you can now enter the credentials in the auth website
    1. you can now change the switch items in the auth page
    1. better error checking
    1. reload button
    1. button for copy the redirect url


## v1.0
1. oauth2 authentication
1. token refresh
1. retrieve data from the following APIs
    1. "Fuel Status API"               
    1. "Electric Vehicle Status API"   
    1. "Vehicle Lock Status API"       
    1. "Vehicle Status API"            
    1. "Pay As You Drive Insurance API"
1. website checks for prerequisites
1. CSRF attacks protection in website
1. openHAB python integration using (https://github.com/sim0nx/python-openhab)
1. added optional timestamp for each data point
1. error checks

# To do / Ideas
1. OH3 REST API Auth