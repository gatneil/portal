import json
import copy
import argparse
import subprocess
from pprint import pprint

parser = argparse.ArgumentParser(description="Generate zips for marketplace.")
parser.add_argument('--version', help='semver package version', required=True)
parser.add_argument('--hidekey', help='generate with vmss hidekey')
args = parser.parse_args()

with open('imageList.json') as imageListFile:
    imageList = json.load(imageListFile)

with open('CreateUiDefinition.json') as baseFile:
    base = json.load(baseFile)

with open('mainTemplate.json') as mainTemplateFile:
    mainTemplate = json.load(mainTemplateFile)

with open('manifests/basePackage/Manifest.json') as manifestFile:
    manifest = json.load(manifestFile)

with open('manifests/basePackage/strings/resources.resjson') as resourceJsonFile:
    resourceJson = json.load(resourceJsonFile)

manifest["version"] = args.version
if args.hidekey:
    print("generating with hidekey")
    manifest["filters"] = [{"type": "HideKey", "value": "vmss"}]

resourceJson["description"] += " (Portal VMSS version " + args.version + ")."
outputRootFolder = "releases/" + args.version + "/"
subprocess.call(['mkdir', outputRootFolder])

def getStepByName(d, name):
    for step in d["parameters"]["steps"]:
        if step["name"] == name:
            return step

    return None

def getElementByNameInVMSSStep(d, name):
    vmssStep = getStepByName(d, "vmssServiceConfig")
    for element in vmssStep["elements"]:
        if element["name"] == name:
            return element

    return None

for environment in imageList:
    print(environment)
    mainTemplate["parameters"]["baseUrl"]["defaultValue"] = imageList[environment]["urlBase"] + "/artifact/20151001/microsoft.vmss." + args.version + "/Artifacts"
    data = copy.deepcopy(base)
    imageWindowsElement = getElementByNameInVMSSStep(data, "imageWindows")
    imageLinuxElement = getElementByNameInVMSSStep(data, "imageLinux")
    imageWindowsElement["constraints"]["allowedValues"] = imageList[environment]["windows"]
    imageWindowsElement["defaultValue"] = imageList[environment]["windowsDefault"]
    imageLinuxElement["constraints"]["allowedValues"] = imageList[environment]["linux"]
    #pprint(data)

    if not environment == "Public":
        autoscaleYesOrNoElement = getElementByNameInVMSSStep(data, "autoscaleYesOrNo")
        autoscaleYesOrNoElement["visible"] = False
        autoscaleYesOrNoElement["constraints"]["allowedValues"] = [{"label": "Disabled", "value": "No"}]

    environmentRoot = outputRootFolder + environment + '/'
    subRoot = environmentRoot + 'microsoft.vmss.' + args.version + '/'
    subprocess.call(['mkdir', environmentRoot])
    subprocess.call(['cp', '-R', 'manifests/basePackage/', subRoot])
    with open(subRoot + 'Manifest.json', 'w') as manifestOutFile:
        manifestOutFile.write(json.dumps(manifest))

    with open(subRoot + 'strings/resources.resjson', 'w') as resourceJsonOutFile:
        resourceJsonOutFile.write(json.dumps(resourceJson))
        
    with open(subRoot + 'Artifacts/CreateUiDefinition.json', 'w') as outFile:
        outFile.write(json.dumps(data))

    with open(subRoot + 'Artifacts/mainTemplate.json', 'w') as mainTemplateOutFile:
        mainTemplateOutFile.write(json.dumps(mainTemplate))

    subprocess.call(['cp', 'autoscaleNo.json', 'autoscaleYes.json', subRoot + 'Artifacts/'])


subprocess.call(['cp', '-r', outputRootFolder, '/home/negat/vmssPortal' + args.version])
