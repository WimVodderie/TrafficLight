import xmlrpc.client
import sys

with xmlrpc.client.ServerProxy("http://127.0.0.1:8000") as proxy:

    if len(sys.argv)>1:
        if sys.argv[1].lower()=='stop':
            print("stop")
            proxy.stop()
        else:
            print("off")
            proxy.red(0)
            proxy.orange(0)
            proxy.blue(0)
    else:
        print("on")
        proxy.red(25)
        proxy.orange(50)
        proxy.blue(75)



