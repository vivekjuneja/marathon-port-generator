from sys import argv
import re
from sets import Set
import random
import json
import requests


startPortNum=1
endPortNum=1000

def get_unique_ports(fileName):
	f = open(fileName, 'rt')
	data = str(f.read())
	f.close()

	'''Store the unique ports that are declared in the manifest. Used to find out number of ports to be generated'''
	unique_set=Set()
	
	for m in re.finditer('SERVICE-DISCOVERY-PORT[0-9][0-9]', data):
         #print(data[m.end()-2: m.end()])
         unique_set.add(data[m.end()-2: m.end()])
        
   #	print unique_set
    	return len(unique_set)


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
				#	print each_group["apps"][0]["ports"]
					used_ports.append(each_group["apps"][0]["ports"][0])
				#print "\n"

			#print "\n"

	#print used_ports
	return used_ports


def get_max_used_port_number(marathon_endpoint, only_use_groups):
	'''parse Marathon manifest to find used service discovery ports'''
	#print marathon_endpoint	
	return max(get_used_ports(marathon_endpoint, only_use_groups))


def generate_port_numbers(num_of_ports, max_used_port_number):
	
	port_num=[]
	port_counter=0
	#print "max_used_port_number : "+ str(max_used_port_number)
	#print "num_of_ports : " + str(num_of_ports)

	for i in range(1,num_of_ports+1):
		port_num.append(max_used_port_number + i)

	return port_num


def render_bash_output(array):
	bash_array=""
	for item in array:
		bash_array += str(item) + " "
	return (bash_array.strip())


if __name__ == '__main__':
	max_used_portnum = 0
	max_used_portnum = get_max_used_port_number(argv[1:][0], True)
	#print "max_used_portnum : " + str(max_used_portnum)
	port_numbers = generate_port_numbers(get_unique_ports(argv[1:][1]), max_used_portnum)
	print str(render_bash_output(port_numbers))
	#print generate_port_numbers(get_unique_ports(argv[1:][0]))

