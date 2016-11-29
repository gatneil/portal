import sys
sys.path.insert(0, "/home/negat/credentials")

import json
import argparse
import random
import azurerm
import subprocess

from password import *

parser = argparse.ArgumentParser(description='test that all images in Public work')
parser.add_argument('--pathToMainTemplate', required=True)

args = parser.parse_args()
random.seed()

with open('imageList.json', 'r') as imageListFile:
#with open('testImageList.json', 'r') as imageListFile:
    imageList = json.loads(imageListFile.read())


namingBases = []
for autoscaleSetting in ['Yes', 'No']:
    for osType in ['Windows', 'Linux']:
        for element in imageList['Public'][osType.lower()][0:1]:
            namingBase = 'nsgvmss' + str(random.randint(0, 100000))
            namingBases.append(namingBase)
            image = element['value']
            parameters = {'$schema': 'http://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json',
                          'contentVersion': '1.0.0.0',
                          'parameters': {
                              'location': {'value': 'japanwest'},
                              'pipName': {'value': 'pip'},
                              'pipLabel': {'value': namingBase},
                              'vmSku': {'value': 'Standard_D1_v2'},
                              'osType': {'value': osType},
                              'image': {'value': image},
                              'vmssName': {'value': namingBase},
                              'instanceCount': {'value': '2'},
                              'authenticationType': {'value': 'password'},
                              'username': {'value': 'negat'},
                              'password': {'value': password},
                              'sshPublicKey': {'value': ''},
                              'autoscaleYesOrNo': {'value': autoscaleSetting},
                              'autoscaleMin': {'value': '1'},
                              'autoscaleMax': {'value': '10'},
                              'autoscaleDefault': {'value': '1'},
                              'scaleOutCPUPercentageThreshold': {'value': '75'},
                              'scaleOutInterval': {'value': '1'},
                              'scaleInCPUPercentageThreshold': {'value': '25'},
                              'scaleInInterval': {'value': '1'},
                              'baseUrl': {'value': 'https://raw.githubusercontent.com/gatneil/portal/hostMetrics'}
                          }
            }
            
            with open('tmp/' + namingBase + '.json', 'w') as parametersFile:
                parametersFile.write(json.dumps(parameters))

            cmd = ['azure', 'group', 'create', '-n', namingBase, '-d', namingBase, '-l', 'japanwest', '-f', 'mainTemplate.json', '-e', 'tmp/' + namingBase + '.json']
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
