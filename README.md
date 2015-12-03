# What does this tool do ?

1. Read the Marathon deployment Manifest to identify number of "Service Discovery Ports" using the placeholder SERVICE-DISCOVERY-PORT[00-99]. 
This information is used to devise how many Ports need to be generated. 

2. Call the Marathon API Endpoint to identify all allocated ports. This information is used to devise the MAX(All ports allocated). 

3. Generate unique ordered port numbers based on number of ports needed and Maximum port already allocated. 


# To use the Tool

```
python deploy_template_replace.py <Marathon_Endpoint> <Marathon-Deployment-Manifest-Template-File>
```

Example:- 

python deploy_template_replace.py 10.53.15.219:18080 wcs-deployment-manifest-template1.json