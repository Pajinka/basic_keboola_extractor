'''
Template Component main class.

'''

import csv
import logging
import sys

from kbc.env_handler import KBCEnvHandler
import ET_Client

# configuration variables
CLIENT_ID = '#clientId'
CLIENT_SECRET = '#clientSecret'
SUBDOMAIN = '#subdomain'
MID = '#mid'
SCOPE = 'scope'

# #### Keep for debug
KEY_DEBUG = 'debug'

MANDATORY_PARS = [
    CLIENT_ID,
    CLIENT_SECRET,
    SUBDOMAIN,
    MID
]
MANDATORY_IMAGE_PARS = []

APP_VERSION = '0.0.1'

DEFAULT_TABLE_INPUT = "/data/in/tables/"
DEFAULT_FILE_INPUT = "/data/in/files/"

DEFAULT_FILE_DESTINATION = "/data/out/files/"
DEFAULT_TABLE_DESTINATION = "/data/out/tables/"

class Component(KBCEnvHandler):

    def __init__(self, debug=False):
        KBCEnvHandler.__init__(self, MANDATORY_PARS, log_level=logging.DEBUG if debug else logging.INFO)
        # override debug from config
        if self.cfg_params.get(KEY_DEBUG):
            debug = True
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

        try:
            self.validate_config(MANDATORY_PARS)
            self.validate_image_parameters(MANDATORY_IMAGE_PARS)
        except ValueError as e:
            logging.exception(e)
            exit(1)

    def validate_config_params(self, params):
        '''
        Validating if input configuration contain everything needed
        '''

        # Credentials Conditions
        # Validate if config is blank
        if params == {}:
            logging.error(
                'Configurations are missing. Please configure your component.')
            sys.exit(1)

        # Validate if the configuration is empty
        empty_config = {
            '#clientId': '',
            '#clientSecret': '',
            '#subdomain': '',
            '#mid': ''
        }

        if params == empty_config:
            logging.error(
                'Configurations are missing. Please configure your component.')
            sys.exit(1)

        # Validating config parameters
        if params[CLIENT_ID] == '' or params[CLIENT_SECRET] == '':
            logging.error(
                "Credentials missing: Client ID or Client Secret is missing")
            sys.exit(1)
        if params[SUBDOMAIN] == '':
            logging.error(
                "Subdomain name is missing, check your configuration.")
            sys.exit(1)
        if params[MID] == '':
            logging.error(
                "Account name is missing, check your configuration.")
            sys.exit(1)

    def run(self):
        '''
        Main execution code
        '''
        output = []
        output_title = []

        params = self.cfg_params  # noqac

        # Get proper list of tables
        client_id = params.get(CLIENT_ID)
        client_secret = params.get(CLIENT_SECRET)
        subdomain = params.get(SUBDOMAIN)
        sub_id = params.get(MID)
        scope = params.get(SCOPE)

        stubObj = ET_Client.ET_Client(
            False, False,
            {
                'clientid': client_id,
                'clientsecret': client_secret,
                'wsdl_file_local_loc': DEFAULT_FILE_INPUT +'/ExactTargetWSDL.xml',
                'authenticationurl': 'https://' + subdomain + '.auth.marketingcloudapis.com/',
                'useOAuth2Authentication': 'True',
                'accountId': sub_id
            })

        if scope == ('Subscribers').lower():
            getSub = ET_Client.ET_Subscriber()
            getSub.props = ["SubscriberKey", "EmailAddress", "Status"]
            getSub.auth_stub = stubObj
            getResponse = getSub.get()
            result = getResponse.results
            output = [(x['EmailAddress'], x['SubscriberKey'], x['Status']) for x in result]
            output_title = ['email', 'subscriber_key', 'status']
        elif scope == ('DataExtensions').lower():
            de = ET_Client.ET_DataExtension()
            de.auth_stub = stubObj
            de.props = ["CustomerKey", "Name", "Description"]
            getResponse = de.get()
            result = getResponse.results
            output = [(x['CustomerKey'], x['Name'], x['Description']) for x in result]
            output_title = ['customerkey', 'name', 'description']
        elif scope == ('Folders').lower():
            getFolder = ET_Client.ET_Folder()
            getFolder.auth_stub = stubObj
            getFolder.props = ["ID", "Client.ID", "ParentFolder.ID", "ParentFolder.CustomerKey",
                               "ParentFolder.ObjectID", "ParentFolder.Name", "ParentFolder.Description",
                               "ParentFolder.ContentType", "ParentFolder.IsActive", "ParentFolder.IsEditable",
                               "ParentFolder.AllowChildren", "Name", "Description", "ContentType", "IsActive",
                               "IsEditable", "AllowChildren", "CreatedDate", "ModifiedDate", "Client.ModifiedBy",
                               "ObjectID", "CustomerKey", "Client.EnterpriseID", "Client.CreatedBy"]
            getResponse = getFolder.get()
            result = getResponse.results
            output = [(x['Name'], x['ID'], x['CustomerKey'], x['ObjectID']) for x in result]
            output_title = ['name', 'id', 'customerkey', 'objectid']

        output_file = DEFAULT_TABLE_DESTINATION + scope + '.csv'
        logging.info(output_file)

        with open(output_file, 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(output_title)
            for row in output:
                csv_out.writerow(row)

"""
        Main entrypoint
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_arg = sys.argv[1]
    else:
        debug_arg = False
    try:
        comp = Component(debug_arg)
        comp.run()
    except Exception as exc:
        logging.exception(exc)
        exit(1)
