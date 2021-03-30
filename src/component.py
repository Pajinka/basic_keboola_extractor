'''
Template Component main class.

'''

import csv
import logging
import sys
import requests

from kbc.env_handler import KBCEnvHandler
import ET_Client

# configuration variables
KEY_URL_CFG = 'api_url'
KEY_RESULT_FILE = 'result_file_name'

# #### Keep for debug
KEY_DEBUG = 'debug'

MANDATORY_PARS = []
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

    def run(self):
        '''
        Main execution code
        '''

        stubObj = ET_Client.ET_Client(
            False, False,
            {
                'clientid': os.environ['clientId'],
                'clientsecret': os.environ['clientSecret'],
                'authenticationurl': 'https://' + os.environ['SFMC_URI'] + '.auth.marketingcloudapis.com/',
                'useOAuth2Authentication': 'True',
                'accountId': os.environ['mid']
            })

        getSub = ET_Client.ET_Subscriber()
        getSub.props = ["SubscriberKey", "EmailAddress", "Status"]
        getSub.auth_stub = stubObj
        getResponse = getSub.get()

        result = getResponse.results
        subscribers = [(x['EmailAddress'], x['SubscriberKey'], x['Status']) for x in result]

        output_file = DEFAULT_TABLE_DESTINATION + 'subscribers.csv'
        logging.info(output_file)

        with open(output_file, 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(['email', 'subscriber_key', 'status'])
            for row in subscribers:
                csv_out.writerow(row))

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
