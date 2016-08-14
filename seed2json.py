# reads pipe delimited data from names.txt and generates
# test healthcare data ready for a graph database

import json, datetime, csv, random, uuid, os, shutil

shutil.rmtree("output", ignore_errors=True, onerror=None) 
os.mkdir("output")
os.mkdir("output/edges") 

# write formatted JSON to file
def write_json(path, doc):
  f = open(path, "w")
  f.write(json.dumps(doc, indent=4, sort_keys=True))
  f.close()

# parse pipe-delimited record
def parse_fields(record):
  fields = record.split("|")
  lookup = {}
  lookup["gender"] = fields[1]
  lookup["firstname"] = fields[4]
  lookup["lastname"] = fields[6]
  lookup["street"] = fields[7]
  lookup["city"] = fields[8]
  lookup["state"] = fields[9]
  lookup["zip"] = fields[11]
  lookup["country"] = fields[12]
  lookup["email"] = fields[14]
  lookup["username"] = fields[15]
  lookup["password"] = fields[16]
  lookup["telephone"] = fields[17]
  lookup["countrycode"] = fields[18]
  lookup["mothersmaidenname"] = fields[19]
  lookup["birthday"] = fields[20]
  lookup["nationalid"] = fields[21];
  lookup["ocupation"] = fields[22]
  lookup["company"] = fields[23]
  lookup["bloodtype"] = fields[24]
  lookup["weightkilograms"] = fields[25]
  lookup["heightcentimeters"] = fields[26]
  lookup["age"] = fields[27].strip()
  return lookup

# generate random day in last x years
def gen_random_date(years):
  from_date = datetime.date.today().replace(year=datetime.date.today().year - years).toordinal()
  random_day = datetime.date.fromordinal(random.randint(from_date, datetime.date.today().toordinal()))
  return random_day

# read pipe-delimited seed file into list
with open("seed/names.txt") as f:
    content = f.readlines()
    content.remove(content[0]) # remove header from data set 

# Attribute groupings
class ATTS(object):
    PERSONAL = ["firstname", "lastname", "gender", "birthday", "nationalid", "ocupation"]
    PHYSICAL = ["bloodtype", "weightkilograms", "heightcentimeters", "age"]
    CONTACT = ["street", "city", "state", "zip", "country", "telephone", "countrycode", "email"]
    SECURITY = ["username", "password", "mothersmaidenname"]

class Commandset(object):
  
    # constructor
    def __init__(self, commandName, elementType, content):
        self.commandName = commandName
        self.elementType = elementType
        self.content = content
        
    # builds an add command
    def buildCommand(self, commandName, elementType, id, record, attributes):
      
      # construct command element of type elementType
      command = {}
      command["commandName"] = commandName
      command["elementType"] = elementType

      # parse the raw pipe-delimited record into a dict
      lookup = parse_fields(record)

      payload = {}

      # set id
      payload["id"] = id
      
      # include all attributes requested by client
      for attribute in attributes:
        payload[attribute] = lookup[attribute]

      command["payload"] = payload
      return command

    # create command set from seed data
    def gen_add_commandset(self, range, attributes):
      Commandset = []
      for index in range:   
        id = str(uuid.uuid4()) # unique id for new record
        Commandset.append(self.buildCommand(self.commandName, self.elementType, id, self.content[index], attributes))
      return Commandset

# define docs
encounters_doc = []
patients_doc = []
doctors_doc = []
researchers_doc = []
encounters_doc = []
clearing_houses_doc = []
hospitals_doc = []
research_orgs_doc = []
researchers_doc = []

# create patients json file from first 25k records
print "Generating patients..." 
attributes = ATTS.PERSONAL + ATTS.PHYSICAL + ATTS.CONTACT + ATTS.SECURITY
patients_doc = Commandset("ADD", "PATIENT", content).gen_add_commandset(range(0, 24999), attributes)
write_json("output/patients.json", patients_doc)

# create doctors json file from next 2k records
print "Generating doctors..."
attributes = ATTS.PERSONAL + ATTS.CONTACT + ATTS.SECURITY
doctors_doc = Commandset("ADD", "DOCTOR", content).gen_add_commandset(range(25000, 26999), attributes)
write_json("output/doctors.json", doctors_doc)

# create hospitals json file from next 500 records (leverage contact fields only)
print "Generating  hospitals..."
attributes = ATTS.CONTACT
hospitals_doc = Commandset("ADD", "HOSPITAL", content).gen_add_commandset(range(27000, 27499), attributes)
for index, elements in enumerate(hospitals_doc): # add a unique hospital name
  elements["payload"]["name"] = elements["payload"]["email"].split("@")[0] + " Hospital of " + elements["payload"]["city"]
write_json("output/hospitals.json", hospitals_doc)

# create clearing house orgs json file from next 100 records (leverage contact fields only)
print "Generating clearing house organizations..."
attributes = ATTS.CONTACT
clearing_houses_doc = Commandset("ADD", "CLEARINGHOUSE_ORGANIZATION", content).gen_add_commandset(range(28600, 28699), attributes)
for elements in clearing_houses_doc: # add a unique resarch org name
  elements["payload"]["name"] = elements["payload"]["email"].split("@")[0] + " Clearinghouse of " + elements["payload"]["city"]
write_json("output/clearinghouse_orgs.json", clearing_houses_doc)

# create research orgs json file from next 100 records (leverage contact fields only)
print "Generating research organizations..."
attributes = ATTS.CONTACT
research_orgs_doc = Commandset("ADD", "RESEARCH_ORGANIZATION", content).gen_add_commandset(range(27500, 27599), attributes)
for elements in researchers_doc: # add a unique resarch org name
  elements["payload"]["name"] = elements["payload"]["email"].split("@")[0] + " Research Lab of " + elements["payload"]["city"]
write_json("output/research_orgs.json", research_orgs_doc)

# create researchers json file from next 1k records
print "Generating researchers..."
attributes = ATTS.PERSONAL + ATTS.CONTACT + ATTS.SECURITY
researchers_doc = Commandset("ADD", "RESEARCHER", content).gen_add_commandset(range(27600, 28599), attributes)
write_json("output/researchers.json", researchers_doc)

# create encounters json file
print "Generating 100k encounters..."
for index in range(0, 999): 
  element = {}
  element["commandName"] = "ADD"
  element["elementType"] = "ENCOUNTER"
  payload = {}
  # unique id for new record
  payload["id"] = str(uuid.uuid4()) 
  payload["timestamp"] = gen_random_date(2).isoformat()
  element["payload"] = payload
  encounters_doc.append(element)

# write to 
write_json("output/encounters.json", encounters_doc)


print "Generating edges..."

# create leftdoc outter-join right docs with shared timestamp
def make_add_edge_left_outter(leftDoc, right_docs):
  edge_doc = []
  for index in range(0, len(leftDoc)):

    timestamp = gen_random_date(2).isoformat()
    left_edge = leftDoc[index]

    # iterate over outter nodes
    for right_doc in right_docs: 

      # setup left edge
      element = {}
      element["commandName"] = "ADD"
      payload = {}
      payload["id"] = str(uuid.uuid4()) 
      payload["timestamp"] = timestamp
      payload[left_edge["elementType"] + "_ID"] = left_edge["payload"]["id"]

      # setup right edge
      random_right_doc_index = random.randint(0, len(right_doc)-1)
      right_edge = right_doc[random_right_doc_index]
      payload[right_edge["elementType"] + "_ID"] = right_edge["payload"]["id"]
      
      # add payload
      element["payload"] = payload

      # set type
      element["elementType"] = left_edge["elementType"] + "_" + right_edge["elementType"] + "_EDGE"
      
      # add to doc
      edge_doc.append(element)

  return edge_doc
    
# create encounter edges
encounters_edges_doc = make_add_edge_left_outter(encounters_doc, [patients_doc, hospitals_doc, clearing_houses_doc, doctors_doc])
write_json("output/edges/encounter_edges.json", encounters_edges_doc)

# create clearing house research org nodes
clearinghouse_edges_doc = make_add_edge_left_outter(clearing_houses_doc, [research_orgs_doc])
write_json("output/edges/clearinghouse_edges.json", clearinghouse_edges_doc)

# create research org nodes
research_org_edges_doc = make_add_edge_left_outter(research_orgs_doc, [researchers_doc])
write_json("output/edges/resource_org_edges.json", research_org_edges_doc)



 
