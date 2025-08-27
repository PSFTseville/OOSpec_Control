from src.server.server import OHRServer
import sys
import os

if __name__=="__main__":


    match len(sys.argv):
        case 1:
            OHRS = OHRServer(PORT=12345)
        case 2:
            OHRS = OHRServer(PORT=sys.argv[1])

    OHRS.run()
