'''
Template Component main class.

'''

import csv
import logging
import sys
import requests

from kbc.env_handler import KBCEnvHandler

# configuration variables
KEY_URL_CFG = 'api_url'

# #### Keep for debug
KEY_DEBUG = 'debug'

MANDATORY_PARS = []
MANDATORY_IMAGE_PARS = []

APP_VERSION = '0.0.1'


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
        url = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2021-01-08&endtime=2021-01-09'

        res = requests.get(url)
        data_load = res.json()
        fieldnames_prop = data_load['features'][0]['properties'].keys()
        fieldnames_geo = data_load['features'][0]['geometry'].keys()

        with open('properties.csv', 'w') as out:
            dw = csv.DictWriter(out, fieldnames=fieldnames_prop)
            dw.writeheader()
            for index, data in zip(range(10), data_load['features']):
                dw.writerow(data['properties'])

        with open('geometry.csv', 'w') as out:
            dw = csv.DictWriter(out, fieldnames=fieldnames_geo)
            dw.writeheader()
            for index, data in zip(range(10), data_load['features']):
                dw.writerow(data['geometry'])

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
