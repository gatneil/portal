import os
import time
from subprocess import Popen, call
from test import *

call(["rm", "-f", "output/*"])

PARALLELISM = 10

def numTestsRunning():
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    res = 0
    for pid in pids:
        try:
            cmdline = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
            if 'run_single' in cmdline:
                res += 1
                
        except IOError: # proc has already terminated
            continue


    return res


for linux_image in linux_images:
    for auth_type in AUTH_TYPES:
        while numTestsRunning() >= PARALLELISM:
            # wait till not at full parallelism
            time.sleep(10)

        cmd = ["/usr/local/lib/python2.7.9/bin/python", "/home/negat/repos/templates/vmssPortal/run_single.py", linux_image, auth_type, NAMING_INFIX + linux_image[0:2] + auth_type[0], 'l', '>', 'output/' + linux_image + auth_type + 'debug.txt']
        print(cmd)
        Popen(cmd)

for windows_image in windows_images:
    while numTestsRunning() >= PARALLELISM:
        # wait till not at full parallelism
        time.sleep(10)

    cmd = ["/usr/local/lib/python2.7.9/bin/python", "/home/negat/repos/templates/vmssPortal/run_single.py", windows_image, "password", NAMING_INFIX + "".join(windows_image.split("-")), 'w', '>', 'output/' + windows_image + auth_type + 'debug.txt']
    print(cmd)
    Popen(cmd)

