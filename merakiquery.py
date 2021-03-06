import requests
import ConfigParser


def getorganization(server,merakiAPIkey):

    print "Unfortunately, you have not specified an organization ID in the configuration file"
    print "Currently, the following organizations exist:\n"


    base_url = "https://" + server + "/api/v0/organizations"
    headers = {'X-Cisco-Meraki-API-Key': merakiAPIkey}

    # Send the query to the Meraki API
    r = requests.get(base_url,headers=headers)

    # Retrieve the results in JSON format
    json_string = r.json()


    for org in json_string:
        print "Organization: {}, ID: {}".format(org.get("name"), org.get("id"))

    print"\nPlease select one of the above organizations and place it in the configuration file."
    exit()



print "Meraki Query Engine Starting...\n"

# Open up the configuration file and get all application defaults
config = ConfigParser.ConfigParser()
config.read('package_config.ini')

serveraddress = config.get("application","serveraddress")
merakiAPIkey = config.get("application","merakiAPIkey")
try:
    organization = config.get("application","organization")

except ConfigParser.NoOptionError:
    getorganization(serveraddress,merakiAPIkey)
    exit()
except:
    print "Unexpected Error"
    exit()

if organization is "":
    print "No Organization"
    getorganization(serveraddress,merakiAPIkey)
    exit()

print "Meraki Configuration:"
print "Meraki Server Address: "+serveraddress
print "Meraki API Key: "+merakiAPIkey
print "Organization ID: "+organization


# Construct the url for querying the Meraki API
base_url="https://"+serveraddress+"/api/v0"
config_url="/organizations/"+organization+"/networks"
headers = {'X-Cisco-Meraki-API-Key':merakiAPIkey}


# Send the query to the Meraki API
r = requests.get(base_url+config_url,headers=headers)

if r.status_code != 200:
    print "ERROR: Unable to connect to Meraki API: Status Code "+str(r.status_code)

    if r.status_code == 400:
        print "400: Bad Request- You did something wrong, e.g. a malformed request or missing parameter."
    elif r.status_code == 403:
        print "403: Forbidden- You don't have permission to do that."
    elif r.status_code == 404:
        print "404: Not found- No such URL, or you don't have access to the API or organization at all."
    else:
        print "Unknown Return Code"

    exit()


# Retrieve the results in JSON format
json_string = r.json()

for network in json_string:

    if network['type'] == "combined" or network['type'] == "wireless" or network['type'] == "switch"  or \
            network['type'] == "appliance":

        network_id = network['id']
        found_network = True

        print "\nQuerying Meraki for Devices on Network: "+network['name']+",  ID: "+network_id

        config_url = "/networks/"+network_id+"/devices"
        r = requests.get(base_url+config_url,headers=headers)
        json_string = r.json()

        print '{0:20} {1:20} {2:20} {3:30} {4:20}'.format("Switch Name", "MAC Address", "Device Vendor", "IP Address","Device Type")
        print '==============================================================================================================================='

        serialnumlist=[]

        for item in json_string:
        # Iterate through each record that was returned from the Meraki API


            # Extract all the appropriate fields
            devicename = item.get("name")
            macAddress = item.get("mac")
            serialnum = item.get("serial")

            serialnumlist.append(item)

            devicetype = item.get("model")
            ipaddress = item.get("lanIp")

            # Print the resulting data to the screen
            print '{0:20} {1:20} {2:20} {3:30} {4:20}'.format(devicename, macAddress, serialnum,ipaddress, devicetype)



        for item in serialnumlist:
            print "\nQuerying Meraki for clients on Network: " + item.get("name")+ " (" + item.get("serial") + ")"

            if item.get('model')[:2] == "MV":
                print "Currently Cameras are not suppported"
                continue

            print '{0:20} {1:30} {2:16} {3:18} {4:10}   {5:11}  {6:11}'.format("Hostname", "Description", "IP Address", "MAC Address",
                                                              "Switchport", "Sent KBytes", "Recv KBytes")
            print '===================================================================================================================================================='

            config_url = "/devices/" + item.get("serial") + "/clients?timespan=86400"
            r = requests.get(base_url + config_url, headers=headers)
            json_string = r.json()

            for client in json_string:

                hostname = client.get("dhcpHostname")
                description = client.get("description")
                ipaddress = client.get("ip")
                macaddress = client.get("mac")
                switchport = client.get("switchport")
                usage = client.get("usage")
                sentbytes = usage.get("sent")
                recvbytes = usage.get("recv")

                print '{0:20.20} {1:30} {2:16} {3:18} {4:^10}   {5:11.2f}  {6:11.2f}'.format(hostname, description, ipaddress, macaddress, switchport,sentbytes, recvbytes)

exit()





