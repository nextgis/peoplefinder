import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:8123')

# Print list of available methods
print s.system.listMethods()

print s.send_sms("asdsdfvfvfvvv")
