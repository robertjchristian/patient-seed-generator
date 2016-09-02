

from neo4jrestclient.client import GraphDatabase
#from neo4jrestclient.query import Q

from pprint import pprint
import json

def flattenDict(d,result=None,index=None,Key=None):
    if result is None:
        result = {}
    if isinstance(d, (list, tuple)):
        for indexB, element in enumerate(d):
            if Key is not None:
                newkey = Key
            flattenDict(element,result,index=indexB,Key=newkey)            
    elif isinstance(d, dict):        
        for key in d:
            value = d[key]         
            if Key is not None and index is not None:
                newkey = ".".join([Key,(str(key).replace(" ", "") + str(index))])
            elif Key is not None:
                newkey = ".".join([Key,(str(key).replace(" ", ""))])
            else:
                newkey= str(key).replace(" ", "")
            flattenDict(value,result,index=None,Key=newkey)        
    else:
        result[Key]=d        
    return result

gdb = GraphDatabase("http://localhost:7474/db/data", username="neo4j", password="healthcare123")

# delete all nodes and relations from database
query = ("MATCH (n) DETACH DELETE n")
results = gdb.query(query, params={})

# add elements
def addElements(fileName, label):
  elementsLabel = gdb.labels.create(label)
  with open(fileName) as data_file:    
    elements = json.load(data_file)
  for element in elements:
    e = elementsLabel.create(type=label) # overwritten with properties set below
    e.properties = {'type': label} + flattenDict(element)
    e.label = label


addElements("output_small/encounters.json", "ENCOUNTER")
addElements("output_small/clearinghouse_orgs.json", "CLEARINGHOUSE")
addElements("output_small/doctors.json", "DOCTOR")
addElements("output_small/hospitals.json", "HOSPITAL")
addElements("output_small/patients.json", "PATIENT")
addElements("output_small/research_orgs.json", "RESEARCHORG")
addElements("output_small/researchers.json", "RESEARCHER")

# add edges
def addEdges(fileName):
  with open(fileName) as data_file:    
    elements = json.load(data_file)
  for element in elements:
  	tokens = element["elementType"].split("_")
  	leftType = tokens[0]
  	leftId = element["payload"][leftType + "_ID"]
   	rightType = tokens[1]
   	rightId = element["payload"][rightType + "_ID"]
   	query = "MATCH (a:" + leftType + " { `payload.id`: '" + leftId + "' }), (b:" + rightType + " { `payload.id`: '" + rightId + "' }) CREATE (a)-[:" + element["elementType"] + "]->(b)"
   	results = gdb.query((query), params={})
   
addEdges("output_small/edges/encounter_edges.json")
addEdges("output_small/edges/clearinghouse_edges.json")
addEdges("output_small/edges/researchers_edges.json")

