import demandimport
def log(msg, *args):
    print(msg % args)
demandimport.set_logfunc(log)
demandimport.enable()

import one
import two

print(one.x)
