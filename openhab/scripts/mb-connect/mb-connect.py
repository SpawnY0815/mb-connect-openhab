#
# Use the Mercedes Benz Connect API to feed your openHAB smarthome system with vehicle data | by spawny0815 / Christopher Pattison
# openHAB Community Forum: https://community.openhab.org/t/mercedes-connected-car-api/39673
# GitHub Repository: https://github.com/SpawnY0815/mb-connect-openhab
# Version 1.1
#

import requests
import base64
import sys
import datetime
from openhab import OpenHAB  # https://github.com/sim0nx/python-openhab


## Local settings

# REDIRECT URL EXAMPLE: "http://openhabian:8080/static/mb-connect/mb-connect_auth.html" or "http://192.168.10.50:8080/static/mb-connect/mb-connect_auth.html" Must be the same as in the Mercedes-Benz APP!
REDIRECT_URL = 'http://192.168.150.10:8080/static/mb-connect/mb-connect_auth.html'

# OPTIONAL: you can adjust the item name prefix to your structure, DO THE SAME ON THE TOP OF THE "mb-connect_auth.html" AND IN YOUR ITEMS FILE!!!! Default: 'mbc_'
ITEM_PREFIX = 'mbc_'
# OPTIONAL: you can set here the relative path where the images will be stored. Default: '../../html/mb-connect/vehicle_images/'
IMAGEPATH = '../../html/mb-connect/vehicle_images/'
# OPTIONAL: you can set a image file prefix to better identifie you images. e.g. = 'Eclass_'
IMAGNAME_PREFIX = ''
# OPTIONAL: If you have problems and need more error texts you can set this variable to "True". Default is "False"
DEBUG = False

#####################################################################################################################
# Do not change anything below this line
# Changes below this line should not be necessary.


API_AUTH_URL = 'https://id.mercedes-benz.com/as/authorization.oauth2'
API_TOKEN_URL = 'https://id.mercedes-benz.com/as/token.oauth2'
API_DATA_URL = 'https://api.mercedes-benz.com/vehicledata/v2/vehicles/'
API_IMAGE_URL = 'https://api.mercedes-benz.com/vehicle_images/v1/'


class MercedesBenzAPI(object):
    """
    A wrapper for the Mercedes Benz Connect API
    https://developer.mercedes-benz.com
    for connection your vehicle data to your openHAB system
    """

    def __init__(self):
        """
        Check all requirements, get item states from openHAB and initialize the api connection.
        """
        self.oh = OpenHAB(REDIRECT_URL.split('/static/')[0] + '/rest')

        self.client_id = self.oh.get_item(ITEM_PREFIX + 'client_id').state
        self.client_secret = self.oh.get_item(ITEM_PREFIX + 'client_secret').state
        self.vehicle_id = self.oh.get_item(ITEM_PREFIX + 'vehicle_id').state
        self.api_key = self.oh.get_item(ITEM_PREFIX + 'api_key').state

        self.auth_code = self.oh.get_item(ITEM_PREFIX + 'auth_code').state
        self.auth_code_trigger = self.oh.get_item(ITEM_PREFIX + 'auth_code_trigger').state
        self.auth_state = self.oh.get_item(ITEM_PREFIX + 'auth_state').state

        self.access_token = self.oh.get_item(ITEM_PREFIX + 'access_token').state
        self.refresh_token = self.oh.get_item(ITEM_PREFIX + 'refresh_token').state
        self.token_issued = self.oh.get_item(ITEM_PREFIX + 'token_issued').state
        self.token_expiry = self.oh.get_item(ITEM_PREFIX + 'token_expiry').state

        self.scope_fuelstatus = self.oh.get_item(ITEM_PREFIX + 'scope_fuelstatus').state
        self.scope_evstatus = self.oh.get_item(ITEM_PREFIX + 'scope_evstatus').state
        self.scope_vehiclelock = self.oh.get_item(ITEM_PREFIX + 'scope_vehiclelock').state
        self.scope_vehiclestatus = self.oh.get_item(ITEM_PREFIX + 'scope_vehiclestatus').state
        self.scope_payasyoudrive = self.oh.get_item(ITEM_PREFIX + 'scope_payasyoudrive').state

        self.imageoption_night = self.oh.get_item(ITEM_PREFIX + 'data_imageoption_night').state
        self.imageoption_roofOpen = self.oh.get_item(ITEM_PREFIX + 'data_imageoption_roofOpen').state
        self.imageoption_background = self.oh.get_item(ITEM_PREFIX + 'data_imageoption_background').state
        self.imageoption_cropped = self.oh.get_item(ITEM_PREFIX + 'data_imageoption_cropped').state
        self.imageoption_jpeg = self.oh.get_item(ITEM_PREFIX + 'data_imageoption_jpeg').state

        if self.auth_code is None:
            print('# No authorization code found. Visit "' + REDIRECT_URL + '" to get authorization code.')
            sys.exit()
        if self.client_id is None:
            print('# No CLIENT ID found. Please fill the openHAB item "' + ITEM_PREFIX + 'client_id" with data.')
            sys.exit()
        if self.client_secret is None:
            print('# No CLIENT SECRET found. Please fill the openHAB item "' + ITEM_PREFIX + 'client_secret" with data.')
            sys.exit()
        if self.vehicle_id is None:
            print('# No VEHICLE ID found. Please fill the openHAB item "' + ITEM_PREFIX + 'vehicle_id" with data.')
            sys.exit()

        self.auth_base64 = base64.b64encode(bytes(self.client_id + ':' + self.client_secret, 'utf-8'), altchars=None).decode('ascii')

        if self.auth_code_trigger is None or self.refresh_token is None or self.token_expiry is None or self.access_token is None or self.token_expiry is None:
            self._generateCredentials()
            if self.auth_code_trigger == 'ON':  # New Auth Code in openHAB
                self.oh.get_item(ITEM_PREFIX + 'auth_code_trigger').command('OFF')
        else:
            if (datetime.datetime.now().timestamp() > float(self.token_expiry)):
                self._refreshCredentials()

    def _generateCredentials(self):
        """
        Generate access token for the API connection.
        """

        if len(self.auth_code) > 15:
            # Request to exchange the authorization code with an access token
            headers = {'Authorization': 'Basic ' + self.auth_base64, 'content-type': 'application/x-www-form-urlencoded'}
            payload = 'grant_type=authorization_code&code=' + self.auth_code + '&redirect_uri=' + REDIRECT_URL

            print("# Exchange the authorization code with an access token")

            try:
                r = requests.post(API_TOKEN_URL, headers=headers, params=payload)
                if (DEBUG):
                    print(r.json())
            except:
                print("# Token request failed")
                sys.exit()

            if list(r.json().keys())[0] == 'error_description':
                print('# Error get new token: ' + r.json()['error_description'])
                print('# Visit "' + REDIRECT_URL + '" to get a new authorization code.')
                sys.exit()

            resp = r.json()

            if(r.status_code == 200):
                access_token = resp['access_token']
                refresh_token = resp['refresh_token']
                expires_in = resp['expires_in']

                # Set and Save the access token
                self.access_token = access_token
                self.refresh_token = refresh_token
                self.token_expiry = str(datetime.datetime.now().timestamp() + float(expires_in))
                self.token_issued = datetime.datetime.now()
                self._saveCredentials()

            else:
                print('# Error get new token: ' + r.json())
                sys.exit()

        else:
            print('# No Auth Code found in openHAB item!')

    def _refreshCredentials(self):
        """
        If previous access token expired, get a new one with refresh token.
        """

        #   Send OAuth2 payload to get access_token
        headers = {'Authorization': 'Basic ' + self.auth_base64, 'content-type': 'application/x-www-form-urlencoded'}
        payload = 'grant_type=refresh_token&refresh_token=' + self.refresh_token

        print("# The access token has expired, use the refresh token to get a new one.")

        try:
            r = requests.post(API_TOKEN_URL, headers=headers, params=payload)
            resp = r.json()

            if (DEBUG):
                print(resp)

            if(r.status_code == 200):
                access_token = resp['access_token']
                expires_in = resp['expires_in']
                if('refresh_token' in resp):
                    refresh_token = resp['refresh_token']
                    self.refresh_token = refresh_token

                #  Set and Save the access token
                self.access_token = access_token
                self.token_expiry = str(datetime.datetime.now().timestamp() + float(expires_in))
                self.token_issued = datetime.datetime.now()
                self._saveCredentials()

            else:
                print('# Error get new token: ' + r.json())

        except:
            print('# Error refreshing token:' + str(sys.exc_info()[1]))

    def _saveCredentials(self):
        """
        Save the new token data to openHAB.
        """
        self.oh.get_item(ITEM_PREFIX + 'access_token').command(self.access_token)
        self.oh.get_item(ITEM_PREFIX + 'refresh_token').command(self.refresh_token)
        self.oh.get_item(ITEM_PREFIX + 'token_expiry').command(self.token_expiry)
        self.oh.get_item(ITEM_PREFIX + 'token_issued').command(self.token_issued)

    def _helper_data_switch(self, switch):
        """ Translate Mercedes Benz API values to openHAB switch item definition. "true"="ON", "false"="OFF". """
        if switch == 'true':
            return 'ON'
        else:
            return 'OFF'

    def _helper_data_contact(self, contact):
        """ Translate Mercedes Benz API values to openHAB contact item definition. "true"="OPEN", "false"="CLOSED". """
        if contact == 'true':
            return 'OPEN'
        else:
            return 'CLOSED'

    def _helper_data_number(self, number):
        """ Translate Mercedes Benz API values to openHAB number item definition. Check for float or int value. """
        if '.' in str(number):
            return float(number)
        else:
            return int(number)

    def _helper_oh_switch_state(self, switch):
        """ Check the state of an openhab switch item and return True or False. """
        if switch == 'ON':
            return True
        else:
            return False

    def call(self):
        """
        Call the available resources of the API's and check for data.
        """
        print('# Mercedes Benz API connection successfully established!')
        print('# Searching resources for selected scopes:')

        url = API_DATA_URL + self.vehicle_id + '/resources'
        headers = {'accept': 'application/json;charset=utf-8', 'authorization': 'Bearer ' + self.access_token}

        r = requests.get(url, headers=headers)
        if(r.status_code < 200 and r.status_code > 299):
            if (DEBUG):
                print('# Response Code = ' + str(r.status_code))
            if (DEBUG):
                print(r.content)
            print('# Error: ' + r.content)
            sys.exit()
        if r.status_code == 200:
            for resources in range(len(r.json())):
                self._get_endpoint(r.json()[resources]['href'])
        else:
            print('# Response Error')
            sys.exit()

        print('# All available data has been sent to openHAB!')
        self._done()

    def _transform_data(self, data):
        """
        Check the underlying openHAB item, transform the value to match it and send the value to openHAB.

        Args:
            data (dict): requested endpoint data
        """
        key = list(data.keys())[0]
        value_raw = data[key]['value']
        ts = data[key]['timestamp']

        item_value = self.oh.get_item(ITEM_PREFIX + 'data_' + key)

        if 'Switch' in str(item_value):
            value = self._helper_data_switch(value_raw)
        elif 'Contact' in str(item_value):
            value = self._helper_data_contact(value_raw)
        elif 'Number' in str(item_value):
            value = self._helper_data_number(value_raw)
        elif 'String' in str(item_value):
            value = value_raw
        else:
            print('# Error:   ' + data)
            return
        item_value.update(value)

        try:
            item_ts = self.oh.get_item(ITEM_PREFIX + 'data_' + key + '_ts')
            item_ts.update(datetime.datetime.utcfromtimestamp(ts / 1000))
            ts_text = 'and'
        except:
            ts_text = 'without'
        print('# Update data "' + key + '" with value "' + str(value) + '" ' + ts_text + ' timestamp "' + str(datetime.datetime.utcfromtimestamp(ts / 1000)) + '" to openHAB item "' + ITEM_PREFIX + 'data_' + key + '".')

    def _get_endpoint(self, endpoint):
        """
        Retrieve the individual resources and extract the data.

        Args:
            endpoint (dict): a single endpoint from the resources dict

        Returns:
            [dict]: requested entpoint whit name, value, timestamp
        """

        if (DEBUG):
            print('# try Call Endpoint')

        url = API_DATA_URL + endpoint[10:]
        headers = {'accept': 'application/json;charset=utf-8', 'authorization': 'Bearer ' + self.access_token}

        r = requests.get(url, headers=headers)
        if(r.status_code < 200 and r.status_code > 204):
            print('# Response Code = ' + str(r.status_code))
            if (DEBUG):
                print(r.content)
            if (DEBUG):
                print('# Error')
            return str(r.reason)
        if r.status_code == 200:
            if (DEBUG):
                print(r.json())
            self._transform_data(r.json())
            return r.json()
        if r.status_code == 204:
            print('# No data available for "' + endpoint.split('/')[-1] + '".')
        else:
            if (DEBUG):
                print(r)
            if (DEBUG):
                print('# Error')
            return str(r.reason)
    
    def get_images(self):
        """
        Retrieve the available resources of the image api.
        """
        print('# Mercedes Benz API connection successfully established!')

        def confirm_prompt(question: str) -> bool:
            reply = None
            while reply not in ("y", "n"):
                reply = input(f"{question} (y/n): ").lower()
            if reply.lower() == 'n':
                print('# Cancel image download!')
                sys.exit()
            if reply.lower() == 'y':
                return

        reply = confirm_prompt("# There is a call limit of 5 for the vehicle image trail. Confirm?")

        if self.api_key is None:
            print('# No API KEY found. Please fill the openHAB item "' + ITEM_PREFIX + 'api_key" with data.')
            sys.exit()

        print('# Searching image resources')

        url = API_IMAGE_URL + 'vehicles/' + self.vehicle_id + '?roofOpen=' + str(self._helper_oh_switch_state(self.imageoption_roofOpen)).lower() + '&night=' + str(self._helper_oh_switch_state(self.imageoption_night)).lower() + '&background=' + str(self._helper_oh_switch_state(self.imageoption_background)).lower() + '&cropped=' + str(self._helper_oh_switch_state(self.imageoption_cropped)).lower() + '&jpeg=' + str(self._helper_oh_switch_state(self.imageoption_jpeg)).lower() + '&apikey=' + self.api_key
        headers = {'accept': 'application/json;charset=utf-8'}

        r = requests.get(url, headers=headers)

        if(r.status_code < 200 and r.status_code > 299):
            if (DEBUG):
                print('# Response Code = ' + str(r.status_code))
            if (DEBUG):
                print(r.content)
            print('# Error: ' + r.content)
            sys.exit()
        if r.status_code == 200:
            img_counter = 0
            print('Found ' + str(len(r.json())) + ' image IDs')
            print('Start downloading')
            for key, value in r.json().items():
                self._download_images(key,value)
                img_counter += 1
                print('# Image ' + key + ' (' + str(img_counter) + ' of ' + str(len(r.json())) + ') downloaded successfully')
            
            print('the default location of your vehicle images are: "openHAB conf directory"/html/mb-connect/vehicle_images/')

        else:
            print('# Response Error')
            print('# Response Code = ' + str(r.status_code))
            print('# Response Text = ' + str(r.text))
            sys.exit()
    
    def _download_images(self, imageName, imageId):
        """
        Download the received images.
        """
        url = API_IMAGE_URL + 'images/' + imageId + '?apikey=' + self.api_key
        headers = {'accept': 'image/png'}

        r = requests.get(url, headers=headers)


        if(r.status_code < 200 and r.status_code > 299):
            if (DEBUG):
                print('# Response Code = ' + str(r.status_code))
            if (DEBUG):
                print(r.text)
            print('# Error: ' + r.text)
            sys.exit()
        if r.status_code == 200:

            if self._helper_oh_switch_state(self.imageoption_roofOpen): 
                img_option_roof = '_roofOpen' 
            else: 
                img_option_roof = ''
            if self._helper_oh_switch_state(self.imageoption_night): 
                img_option_night = '_night' 
            else: 
                img_option_night = ''
            if self._helper_oh_switch_state(self.imageoption_background): 
                img_option_background = '_background' 
            else: 
                img_option_background = ''
            if self._helper_oh_switch_state(self.imageoption_cropped): 
                img_option_cropped = '_cropped' 
            else: 
                img_option_cropped = ''
            if self._helper_oh_switch_state(self.imageoption_jpeg): 
                img_option_fileFormat = '.jpeg' 
            else: 
                img_option_fileFormat = '.png'
            with open(IMAGEPATH + IMAGNAME_PREFIX + imageName + img_option_roof + img_option_night + img_option_background + img_option_cropped + img_option_fileFormat, 'wb') as f:
                f.write(r.content)
            
        else:
            print('# Response Error')
            print('# Response Code = ' + str(r.status_code))
            print('# Response Text = ' + str(r.text))
            sys.exit()


    def _done(self):
        self.oh.get_item(ITEM_PREFIX + 'lastConnectionDateTime').command(datetime.datetime.now())


def main():

    def help_cmd():
        """
        Print the help text in terminal
        """

        print('# Available commands:')
        print('# --data: Get the available vehicle information as configured with the openHAB items.')
        print('# --get_images: Download the vehicle images according to the openHAB item settings')

    print('-------------------------------------------------------------------')
    print('## Starting Mercedes Benz API connection ##')


    t1 = datetime.datetime.now().timestamp()

    args = sys.argv

    if len(args) == 1:
        help_cmd()
    else:
        if args[1] == '--data':
            api = MercedesBenzAPI()
            api.call()
        elif args[1] == '--help':
            help_cmd()
        elif args[1] == '--get_images':
            api = MercedesBenzAPI()
            api.get_images()
        else:
            print('#- Wrong argument')
            help_cmd()

    t2 = datetime.datetime.now().timestamp()

    print('# Done in ' + str(t2-t1) + ' seconds')


if __name__ == '__main__':
    main()
