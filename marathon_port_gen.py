from sys import argv
import re
from sets import Set
import random
import json
import requests
from collections import OrderedDict


'''
Read the Marathon deployment manifest template file and search for all places where SERVICE-DISCOVERY-PORT term exists.
Add all such occurences into a Set
Return the length 
'''
init_discovery_port = 20000
service_discovery_port_regex = "SERVICE-DISCOVERY-PORT[0-9][0-9]"

''' Common Method to parse and read content from a file '''
def get_data_from_file(fileName):
	f = open(fileName, 'rt')
	data = str(f.read())
	f.close()
	return data


''' Find out unique occurences of service discovery port template variable'''
def get_num_unique_ports(fileName):
	
	data = get_data_from_file(fileName)

	'''Store the unique ports that are declared in the manifest. Used to find out number of ports to be generated'''
	unique_set=Set()
	
	for m in re.finditer(service_discovery_port_regex, data):
         #print(data[m.end()-2: m.end()])
         unique_set.add(data[m.end()-2: m.end()])
        
   	#print unique_set
    	return len(unique_set)


''' Find App ID and relevant assigned port '''
def get_appid_port_map(json_data):

	appid_port_dict=OrderedDict()

	for app in json_data["groups"]:
			ports = []
			ports_counter = 0
			
			for port in app["apps"][0]["ports"]:
				ports.append(str(port))
				ports_counter =+ 1 
				#print port 

			appid_withgroup = app["apps"][0]["id"]
			appid = appid_withgroup.rfind("/")
			appid_port_dict[appid_withgroup[appid+1:]] = ports
				
	return appid_port_dict


''' Find App ID and relevant assigned port in the Manifest '''
def get_appid_ports_map_manifest(fileName):
	data = get_data_from_file(fileName)

	json_data = json.loads(data) 

	return get_appid_port_map(json_data)


''' Find App ID and relevant assigned port for an existing deployed app grp'''
def get_appid_ports_map_deployed(marathon_endpoint, app_grp_id):
	r = requests.get("http://" + marathon_endpoint + "/v2/groups/"+app_grp_id)
	json_data = json.loads(r.content) 

	if "message" in json_data:
		return []

	return get_appid_port_map(json_data)


def get_ports_to_replace(marathon_endpoint, app_grp_id, fileName):
	appid_port_map = get_appid_ports_map_manifest(fileName)

	appid_port_map_deployed = get_appid_ports_map_deployed(marathon_endpoint, app_grp_id)

	ports = []
	
	for deployed_appId in appid_port_map:
		port_array =  appid_port_map_deployed[deployed_appId]
		for port in port_array:
			ports.append(port)

	return ports

''' Get all ports currently allocated by Marathon '''
def get_used_ports(marathon_endpoint, only_use_groups):
	r = requests.get("http://" + marathon_endpoint + "/v2/groups")
	#json_file = open(fileName)
	data = json.loads(r.content) 
	used_ports=[]
 
 	if(only_use_groups==False):
		for app in data["apps"]:
		#	print app["ports"]
			used_ports.append(app["ports"][0])

	for group in data["groups"]:
			#print "group:" + str(group["groups"])
			for each_group in group["groups"]:
				if (len(each_group["apps"])>0):
					#print each_group["apps"][0]["ports"]
					for each_port in each_group["apps"][0]["ports"]:
						used_ports.append(each_port)
				#print "\n"

			#print "\n"

	#print used_ports
	return used_ports


'''
Return the largest Port allocated till now
'''
def get_max_used_port_number(marathon_endpoint, only_use_groups):
	'''parse Marathon manifest to find used service discovery ports'''
	#print marathon_endpoint	
	used_ports = get_used_ports(marathon_endpoint, only_use_groups)
	max_used_port = 0
	if len(used_ports)==0:
		max_used_port = init_discovery_port
	else:
		max_used_port = max(used_ports)
	return max_used_port


'''
Generate a new set of port port_numbers
''' 
def generate_port_numbers(num_of_ports, max_used_port_number):
	
	port_nums=[]
	port_counter=0
	#print "max_used_port_number : "+ str(max_used_port_number)
	#print "num_of_ports : " + str(num_of_ports)

	for i in range(1,num_of_ports+1):
		port_nums.append(max_used_port_number + i)

	return port_nums


'''
For decorating the output as per needs of Bash Script
'''
def render_bash_output(array):      
	bash_array=""
	for item in array:
		bash_array += str(item) + " "
	return (bash_array.strip())


if __name__ == '__main__':
	max_used_portnum = 0
	deploy_type = argv[1:][0]
	if (deploy_type=="new"):
		#print "getting port allocated for all deployed apps on marathon" 
		max_used_portnum = get_max_used_port_number(argv[1:][1], True)
		port_numbers = generate_port_numbers(get_num_unique_ports(argv[1:][2]), max_used_portnum)
		print str(render_bash_output(port_numbers))
	elif (deploy_type=="update"):
		#print "getting port allocated for existing app " + argv[1:][2]
		#print render_bash_output(get_appid_ports_map_deployed(argv[1:][1], argv[1:][2]))
		#print get_appid_ports_map_deployed(argv[1:][1], argv[1:][2])
		#print get_appid_ports_map_manifest(argv[1:][3])
		print render_bash_output(get_ports_to_replace(argv[1:][1], argv[1:][2], argv[1:][3]))

