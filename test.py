import sys
sys.path.insert(0, "/home/negat/credentials")
sys.path.insert(0, "/home/negat/credentials/aad")

import json
import time
import copy
import azurerm
import thread
from aadcredentials import *
from password import *
from sshpublickey import *

AUTH_TYPES = ["password", "sshPublicKey"]
NAMING_INFIX = "longlonglonglonglonglonglonglonglonglonglonglonglonglonglonglong"[0:61-16]

parameters_json_base = {"location": {"value": "westus"},
                        "vmSku": {"value": "Standard_D1_v2"},
                        "instanceCount": {"value": "2"},
                        "username": {"value": "negat"}}

parameters_json = {}
parameters_json["password"] = copy.deepcopy(parameters_json_base)
parameters_json["password"]["password"] = {"value": password}

parameters_json["sshPublicKey"] = copy.deepcopy(parameters_json_base)
parameters_json["sshPublicKey"]["sshPublicKey"] = {"value": ssh_public_key}


with open('linux.json', 'r') as linux_file:
    linux_json_string = linux_file.read()
    linux_json = json.loads(linux_json_string)

with open('windows.json', 'r') as windows_file:
    windows_json_string = windows_file.read()
    windows_json = json.loads(windows_json_string)

linux_images = linux_json["parameters"]["image"]["allowedValues"]
windows_images = windows_json["parameters"]["WindowsServerVersion"]["allowedValues"]

linux_locations = linux_json["parameters"]["location"]["allowedValues"]
windows_locations = windows_json["parameters"]["location"]["allowedValues"]

#linux_skus = linux_json["parameters"]["vmSku"]["allowedValues"]
#windows_skus = windows_json["parameters"]["vmSku"]["allowedValues"]
#vmSkus = ["Standard_A0", "Standard_A10", "Standard_D1", "Standard_D11", "Standard_D1_v2", "Standard_D11_v2", "Standard_DS1", "Standard_DS11"]

access_token = azurerm.get_access_token(tenant_id, application_id, application_secret)

def test_linux(linux_image, auth_type, local_naming_infix, wl):
    return_val = False
    rg_name = local_naming_infix + "rg"
    dep_name = local_naming_infix[0:20] + "dep"

    res = azurerm.create_resource_group(access_token, subscription_id, rg_name, 'westus')

    cur_parameters_json = copy.deepcopy(parameters_json[auth_type])
    if wl == "l":
        cur_parameters_json["image"] = {"value": linux_image}
        cur_parameters_json["authenticationType"] = {"value": auth_type}
        json_string = linux_json_string
    else:
        cur_parameters_json["WindowsServerVersion"] = {"value": linux_image}
        json_string = windows_json_string

    #print(local_naming_infix)
    cur_parameters_json["vmssName"] = {"value": local_naming_infix}
    cur_parameters_json_string = json.dumps(cur_parameters_json)


    res = azurerm.deploy_template(access_token, subscription_id, rg_name, dep_name, json_string, cur_parameters_json_string)
    #print(res.text)

    while True:
        time.sleep(10)
        res = azurerm.show_deployment(access_token, subscription_id, rg_name, dep_name)
        if "properties" not in res:
            print("properties not in res")
            print(res)

        else:
            if res["properties"]["provisioningState"] == "Failed":
                #print("provisioning state failed")
                break

            if res["properties"]["provisioningState"] == "Succeeded":
                return_val = True
                break


    
    res = azurerm.delete_resource_group(access_token, subscription_id, rg_name)
    return return_val

def test_linux_wrapper(linux_image, auth_type):
    local_naming_infix = NAMING_INFIX + linux_image[0:2] + auth_type[0]

    try:
        res = test_linux(linux_image, auth_type, local_naming_infix, 'l')
        
    except:
        res = False
        
    finally:
        with open('output/' + local_naming_infix + '.txt', 'w') as out:
            out.write('[' + linux_image + ', ' + auth_type + ']: ' + str(res))

def test_all_linux():
    for linux_image in linux_images:
        for auth_type in AUTH_TYPES:
            # (*** start_new_thread tries to use system python, which doesn't have ssl ***)
            #thread.start_new_thread( test_linux_wrapper, (linux_image, auth_type, ) )
            try:
                test_linux_wrapper(linux_image, auth_type)
            except:
                print (sys.exc_info()[0])

def test_all_windows():
    for windows_image in windows_images:
        test_linux(windows_image, "password", NAMING_INFIX + "".join(windows_image.split("-")), 'w')

#test_all_linux()
#test_all_windows()

#test_linux("Ubuntu14.04.4-LTS", "password", NAMING_INFIX + "e")
#test_linux("CentOs7.2", "password", NAMING_INFIX)
#test_linux("Debian8.0", "password", NAMING_INFIX)
