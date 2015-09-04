import os
import sys
import socket
import telnetlib

def main(argv=sys.argv):
    try:
        tn = telnetlib.Telnet("localhost", "4242", 5)
        print "Connect to VTY SUCCESS!"
    except socket.error, e:
        sys.exit("Create VTY connection failed!")

    try:
        tn.read_until("OpenBSC>", 5)
        print "Read VTY welcome message SUCSESS!"
    except socket.error, e:
        sys.exit("Read VTY wellcome message failed!")

    try:
        tn.write("enable\n")
        tn.read_until("OpenBSC#", 5)
        tn.write("configure terminal\n")
        tn.read_until("OpenBSC(config)#", 5)

        tn.write("mncc-int\n")
        tn.read_until("OpenBSC(config-mncc-int)#", 5)
        tn.write("meas-feed destination 127.0.0.1 8888\n")
        tn.read_until("OpenBSC(config-mncc-int)#", 5)
        
        tn.write("exit\n") 
        tn.read_until("OpenBSC(config)#", 5)	

        tn.write("smpp\n")
        tn.read_until("OpenBSC(config-smpp)#", 5)
        tn.write("no smpp-first\n")
        tn.read_until("OpenBSC(config-smpp)#", 5)
    
        tn.write("write file\n")
        tn.read_until("OpenBSC(config-smpp)#", 5)

        print "Configuration smpp SUCCSESS!"
    except socket.error, e:
        sys.exit("Configuration OpenBSC FAILED!")



if __name__ == "__main__":
    main()
