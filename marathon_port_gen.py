from sys import argv
import re
from sets import Set
import random
import json
import requests


'''
Read the Marathon deployment manifest template file and search for all places where SERVICE-DISCOVERY-PORT term exists.
Add all such occurences into a Set
Return the length 
'''
init_discovery_port = 20000

def get_num_unique_ports(fileName):
	f = open(fileName, 'rt')
	data = str(f.read())
	f.close()

	'''Store the unique ports that are declared in the manifest. Used to find out number of ports to be generated'''
	unique_set=Set()
	
	for m in re.finditer('SERVICE-DISCOVERY-PORT[0-9][0-9]', data):
         #print(data[m.end()-2: m.end()])
         unique_set.add(data[m.end()-2: m.end()])
        
   	#print unique_set
    	return len(unique_set)




def get_num_unique_ports_map(fileName):
	f = open(fileName, 'rt')
	data = str(f.read())
	f.close()

	'''Store the unique ports that are declared in the manifest. Used to find out number of ports to be generated'''
	unique_set=Set()
	
	for m in re.finditer('SERVICE-DISCOVERY-PORT[0-9][0-9]', data):
         print(data[m.end()-2: m.end()])
         unique_set.add(data[m.end()-2: m.end()])
        
        
   	print unique_set
    	return len(unique_set)



'''
Get all ports currently allocated by Marathon
'''
def get_used_ports_for_app_grp(marathon_endpoint, app_grp_id):
	r = requests.get("http://" + marathon_endpoint + "/v2/groups/"+app_grp_id)
	#json_file = open(fileName)
	data = json.loads(r.content) 

	#print "--------- : " + str(data["groups"])
	used_ports=[]

	for app in data["groups"]:
			#print "apps:" + str(app)
			
			for port in app["apps"][0]["ports"]:
				#print port
				#print app["apps"][0]["id"] + " : " + str(port)
				used_ports.append(port)
				#print "\n"

			#print "\n"

	#print used_ports
	return used_ports




'''
Get all ports currently allocated by Marathon
'''
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
		print render_bash_output(get_used_ports_for_app_grp(argv[1:][1], argv[1:][2]))
		#print get_num_unique_ports_map(argv[1:][3])

