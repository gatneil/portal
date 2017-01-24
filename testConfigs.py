import sys
sys.path.insert(0, "/home/negat/credentials")

import json
import argparse
import random
import azurerm
import subprocess

from password import *

parser = argparse.ArgumentParser(description='test that various configs work')
parser.add_argument('--pathToMainTemplate', required=True)

args = parser.parse_args()
random.seed()


namingBases = []
for autoscaleSetting in ['Yes', 'No']:
    for diskType in ['Unmanaged', 'Managed']:
            namingBase = 'nsgvmss' + str(random.randint(0, 100000))
            namingBases.append(namingBase)
            parameters = {'$schema': 'http://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json',
                          'contentVersion': '1.0.0.0',
                          'parameters': {
                              'location': {'value': 'eastus2'},
                              'pipName': {'value': 'pip'},
                              'pipLabel': {'value': namingBase},
                              'vmSku': {'value': 'Standard_D1_v2'},
                              'osType': {'value': "Linux"},
                              'image': {'value': "Ubuntu14.04.5-LTS"},
                              'vmssName': {'value': namingBase},
                              'instanceCount': {'value': '2'},
                              'authenticationType': {'value': 'password'},
                              'username': {'value': 'negat'},
                              'password': {'value': password},
                              'sshPublicKey': {'value': ''},
                              'diskType': {'value': diskType},
                              'autoscaleYesOrNo': {'value': autoscaleSetting},
                              'autoscaleMin': {'value': '1'},
                              'autoscaleMax': {'value': '10'},
                              'autoscaleDefault': {'value': '1'},
                              'scaleOutCPUPercentageThreshold': {'value': '75'},
                              'scaleOutInterval': {'value': '1'},
                              'scaleInCPUPercentageThreshold': {'value': '25'},
                              'scaleInInterval': {'value': '1'},
                              'baseUrl': {'value': 'https://raw.githubusercontent.com/gatneil/portal/md'}
                          }
            }
            
            with open('tmp/' + namingBase + '.json', 'w') as parametersFile:
                parametersFile.write(json.dumps(parameters))

            cmd = ['azure', 'group', 'create', '-n', namingBase, '-d', namingBase, '-l', 'eastus2', '-f', 'mainTemplate.json', '-e', 'tmp/' + namingBase + '.json']
            print(cmd)
            subprocess.call(cmd)        

'''
for i in xrange(0, 100):
    for namingBase in namingBases:
        try:
            cmd = ['azure', 'vmss', 'list', namingBase, '|', 'grep', namingBase, '|', 'awk', "'{ print $3 }'"]
            print(cmd)
            print(subprocess.check_output(cmd))
        except:
            ''    
'''
