import sys
from test import *


image = sys.argv[1]
auth_type = sys.argv[2]
local_naming_infix = sys.argv[3]
wl = sys.argv[4]


res = test_linux(image, auth_type, local_naming_infix, wl)
with open ('output/' + image + auth_type + '.txt', 'w') as out:
    out.write(str(res))
