# reads pipe delimited data from names.txt and generates
# test healthcare entities, augments with alt set,
# and creates edges

import json, datetime, csv, random, uuid, os, shutil, copy

shutil.rmtree("./output", ignore_errors=True, onerror=None) 
os.mkdir("./output")

# write formatted JSON to file
def write_json(path, doc):
  f = open(path, "w")
  f.write(json.dumps(doc, indent=4, sort_keys=True))
  f.close()

#
# BUILD ENTITIES from names.txt
#

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
  lookup["occupation"] = fields[22]
  lookup["company"] = fields[23]
  lookup["bloodtype"] = fields[24]
  lookup["weightkilograms"] = fields[25]
  lookup["heightcentimeters"] = fields[26]

  # data cleanup

  # we don't like newborns as doctors, etc... let's just have everyone 18+
  birthYear = int(lookup["birthday"][-4:]);
  if birthYear >= 1998:
    lookup["birthday"] = lookup["birthday"][:-4] + str(birthYear - 18)

  return lookup

# generate random day in last x years
def gen_random_date(years):
  from_date = datetime.date.today().replace(year=datetime.date.today().year - years).toordinal()
  random_day = datetime.date.fromordinal(random.randint(from_date, datetime.date.today().toordinal()))
  return random_day

# read pipe-delimited seed file into list
with open("./seed_files/names.txt") as f:
    content = f.readlines()
    content.remove(content[0]) # remove header from data set 

# Attribute groupings
class ATTS(object):
    PERSONAL = ["firstname", "lastname", "gender", "birthday", "nationalid", "occupation"]
    PHYSICAL = ["bloodtype", "weightkilograms", "heightcentimeters"]
    CONTACT = ["street", "city", "state", "zip", "country", "telephone", "countrycode", "email"]
    SECURITY = ["username", "password", "mothersmaidenname"]

class Commandset(object):
  
    # constructor
    def __init__(self, elementType, content):
       
        self.elementType = elementType
        self.content = content
        
    # builds and
    def buildEntity(self, id, record, attributes):
      
      # construct command element of type elementType
      entity = {}
  
      entity["element_type"] = self.elementType

      # parse the raw pipe-delimited record into a dict
      lookup = parse_fields(record)

      payload = {}

      # set id
      payload["id"] = id
      
      # include all attributes requested by client
      for attribute in attributes:
        payload[attribute] = lookup[attribute]

      entity["payload"] = payload
      return entity

    # create command set from seed data
    def gen_commandset(self, range, attributes):
      Commandset = []
      for index in range:   
        id = str(uuid.uuid4()) # unique id for new record
        Commandset.append(self.buildEntity(id, self.content[index], attributes))
      return Commandset

# define docs
encounters_doc = []
patients_doc = []
doctors_doc = []
researchers_doc = []
encounters_doc = []
clearing_houses_doc = []
facilities_doc = []
research_orgs_doc = []
researchers_doc = []

# create patients json file from first ~11k records
print "Generating patients..." 
attributes = ATTS.PERSONAL + ATTS.PHYSICAL + ATTS.CONTACT + ATTS.SECURITY
patients_doc = Commandset("PATIENT", content).gen_commandset(range(0, 11000), attributes)

# create doctors json file from next 2k records
print "Generating doctors..."
attributes = ATTS.PERSONAL + ATTS.CONTACT + ATTS.SECURITY
doctors_doc = Commandset("DOCTOR", content).gen_commandset(range(11000, 13000), attributes)

# create facilities json file from next 1k records (leverage contact fields only)
print "Generating facilities..."
facility_types = ["Doctor's Office", "Diagnostic Clinic", "Home Health Visit", "Hospital", "ER"]
attributes = ATTS.CONTACT
facilities_doc = Commandset("FACILITY", content).gen_commandset(range(13000, 14000), attributes)
for index, elements in enumerate(facilities_doc): # add a unique facility name
  facility_type = facility_types[random.randint(0, len(facility_types)-1)] # random type
  elements["payload"]["name"] = elements["payload"]["email"].split("@")[0] + facility_type + " of " + elements["payload"]["city"]

# create clearing house orgs json file from next 1k records (leverage contact fields only)
print "Generating clearing house organizations..."
attributes = ATTS.CONTACT
clearing_houses_doc = Commandset("CLEARINGHOUSE_ORGANIZATION", content).gen_commandset(range(14000, 15000), attributes)
for elements in clearing_houses_doc: # add a unique resarch org name
  elements["payload"]["name"] = elements["payload"]["email"].split("@")[0] + " Clearinghouse of " + elements["payload"]["city"]

# create research orgs json file from next 1k records (leverage contact fields only)
print "Generating research organizations..."
attributes = ATTS.CONTACT
research_orgs_doc = Commandset("RESEARCH_ORGANIZATION", content).gen_commandset(range(15000, 16000), attributes)
for elements in research_orgs_doc: # add a unique resarch org name
  elements["payload"]["name"] = elements["payload"]["email"].split("@")[0] + " Research Organization of " + elements["payload"]["city"]

# create researchers json file from next 2k records
print "Generating researchers..."
attributes = ATTS.PERSONAL + ATTS.CONTACT + ATTS.SECURITY
researchers_doc = Commandset("RESEARCHER", content).gen_commandset(range(16000, 18000), attributes)

# create researchers json file from next 1k records
print "Generating labs..."
attributes = ATTS.PERSONAL + ATTS.CONTACT + ATTS.SECURITY
labs_doc = Commandset("LAB", content).gen_commandset(range(18000, 19000), attributes)

# create insurance providers
# read pipe-delimited seed file into list
insurance_doc = []
print "Generating insurance entities..." 
with open("./seed_files/set_from_andy/insurance.txt") as f:
    content = f.readlines()
for name in content:
  entity = {}
  entity["element_type"] = "INSURANCE_PROVIDER"
  payload = {}
  payload["id"] = str(uuid.uuid4()) 
  payload["name"] = name.strip()
  entity["payload"] = payload
  insurance_doc.append(entity)

#
#  AUGMENT ABOVE CREATED DATA WITH SET FROM ANDY
#

# FIRST PATIENTS DATA

# augment patient data with insurer info from Andy's set
with open('./seed_files/set_from_andy/patients.json') as data_file:    
    content = json.load(data_file)

# copy over a few fields
for index, entity in enumerate(content):
  patients_doc[index]["payload"]["primary_insurance_carrier"] = entity["PrimaryInsuranceCarrier"] 
  patients_doc[index]["payload"]["primary_insurance_carrier_id"] = entity["PrimaryInsuranceCarrierId"] 
  patients_doc[index]["payload"]["mrn"] = entity["MRN"]
patients_doc = patients_doc[:(len(content))] # reduce larger set to set count from andy's set

# THEN LABS
with open("./seed_files/set_from_andy/labs.txt") as f:
    content = f.readlines()

# copy over lab name
for index, name in enumerate(content):
  labs_doc[index]["payload"]["name"] = name.strip()
labs_doc = labs_doc[:(len(content))] # reduce larger set to set count from andy's set

# THEN DOCTORS

# augment doctor data with info from Andy's set
with open('./seed_files/set_from_andy/providers.json') as data_file:    
    content = json.load(data_file)

# copy over a few fields
for index, entity in enumerate(content):
  doctors_doc[index]["payload"]["insurance_accepted"] = entity["InsuranceAccepted"] 
  doctors_doc[index]["payload"]["specialty"] = entity["Specialty"] 
  doctors_doc[index]["payload"]["npi"] = entity["NPI"]
  doctors_doc[index]["payload"]["provider_name"] = entity["ProviderName"]
doctors_doc = doctors_doc[:len(content)] # reduce larger set to set count from andy's set

# INCLUDE LAB OUTPUT
# augment doctor data with info from Andy's set
with open('./seed_files/set_from_andy/lab_output.json') as data_file:    
    content = json.load(data_file)

# make doc
lab_output_doc = []
print "Generating lab results..." 
for index, entity in enumerate(content["results"]):
  element = {}
  element["element_type"] = "LAB_RESULTS"
  element["payload"] = entity
  element["payload"]["id"] = str(uuid.uuid4()) 
  lab_output_doc.append(element)

#
# CREATE ENCOUNTERS WHICH WILL ANCHOR DOCTORS, PATIENTS, FACILITIES, AND CLEARING_HOUSES TO AN ENCOUNTER
#

# create encounters json file
print "Generating 10k encounters..."
for index in range(0, 10000): 
  element = {}
  element["element_type"] = "ENCOUNTER"
  payload = {}
  # unique id for new record
  payload["id"] = str(uuid.uuid4()) 
  payload["timestamp"] = gen_random_date(2).isoformat()
  element["payload"] = payload
  encounters_doc.append(element)


#
# CREATE EDGES AND TRIM ENTITY SETS
#

# build index on a list based on keyType, return map
# lower and trims key for loose match
def map(list, keyType):
  m = {}
  for entry in list:

    key = entry["payload"][keyType]
    key = key.strip().lower()
    
    if not key in m:
      m[key] = []

    m[key].append(entry)  
  return m


def genDirectedEdge(leftDoc, rightDoc, leftDocKey=None, rightDocKey=None, direction="left_to_right"):
  
  # index the right doc for inner join if applicable
  if leftDocKey is not None and rightDocKey is not None:
    # get an index based on match criteria
    rightDocIndex = map(rightDoc, rightDocKey)

  edges = []

  for leftEntry in leftDoc:
    
    if leftDocKey is not None and rightDocKey is not None:

      # perform join (strip/lower for loose matching)
      joinCriteria = leftEntry["payload"][leftDocKey].strip().lower()

      if not joinCriteria in rightDocIndex:
        print "No match on " + joinCriteria + " for key: " + leftDocKey
        continue

      # find possible right entries for each left entry based on 
      # match criteria... 
      rightEntryPossibilities = rightDocIndex[joinCriteria]
    
    else:
      rightEntryPossibilities = rightDoc
    
    rightEntry = rightEntryPossibilities[random.randint(0, len(rightEntryPossibilities)-1)]

    element = {}
    element["element_type"] = "EDGE" 
    payload = {}

    
    if direction == "left_to_right":

      payload["left_element_type"] = leftEntry["element_type"]
      payload["left_element_id"] = leftEntry["payload"]["id"]
 
      payload["right_element_type"] = rightEntry["element_type"] 
      payload["right_element_id"] = rightEntry["payload"]["id"]
    
    else:

      payload["right_element_type"] = leftEntry["element_type"]
      payload["right_element_id"] = leftEntry["payload"]["id"]
 
      payload["left_element_type"] = rightEntry["element_type"] 
      payload["left_element_id"] = rightEntry["payload"]["id"]

    element["payload"] = payload

    edges.append(element)

  return edges

edges = []

# first connect Andy's set into the following sub graphs:
#   lab results -> doctor, insurance, and lab ( and randomly assign to a patient?  mrns don't match so would have to be random...)
#   patient -> insurance carrier
#   doctor -> insurance accepted
edges = edges + genDirectedEdge(lab_output_doc, doctors_doc, "ordering_provider", "provider_name" ) # result -> doctor
edges = edges + genDirectedEdge(lab_output_doc, insurance_doc, "primary_insurance", "name" ) # result -> insurance
edges = edges + genDirectedEdge(lab_output_doc, labs_doc, "performing_lab", "name" ) # result -> lab

# creating a stripped version of the patients, only containing the ones which have an insurance
patients_insurance_mod = []
for pat in patients_doc:
  if pat["payload"]["primary_insurance_carrier"]:
    patients_insurance_mod.append(pat)
print "Stripped patient array length, all having a single insurance: "+str(len(patients_insurance_mod))
edges = edges + genDirectedEdge(patients_insurance_mod, insurance_doc, "primary_insurance_carrier", "name" ) # patient -> insurance carrier

# creating duplicated of doctor entities where they support multiple insurances; remove the entities where they don't support any
doctors_insurance_mod = []
for doc in doctors_doc:
  if doc["payload"]["insurance_accepted"]:
    providers = doc["payload"]["insurance_accepted"].split(",")
    for provider in providers:
      provider = provider.strip()
      doc_clone = copy.deepcopy(doc)
      doc_clone["payload"]["insurance_accepted"] = provider
      doctors_insurance_mod.append(doc_clone)
print "Extended doctors array length, all having a single insurance: "+str(len(doctors_insurance_mod))
edges = edges + genDirectedEdge(doctors_insurance_mod, insurance_doc, "insurance_accepted", "name" ) # doctor -> insurance accepted

# then connect each lab result to a unique encounter (but save edge as encounter->lab result)
edges = edges + genDirectedEdge(lab_output_doc, encounters_doc, None, None, "right_to_left" )

# now some encounters have a lab result
# connect a patient to each encounter... encounter->patient
edges = edges + genDirectedEdge(encounters_doc, patients_doc, None, None)

# connect a doctor to each encounter... encounter->doctor
edges = edges + genDirectedEdge(encounters_doc, doctors_doc, None, None)

# connect each encounter to 1..n clearing houses
edges = edges + genDirectedEdge(encounters_doc, clearing_houses_doc, None, None)

# connect each clearing house to 1..n research orgs
edges = edges + genDirectedEdge(clearing_houses_doc, research_orgs_doc, None, None)

# connect each researcher to one research org (research org -> researcher)
edges = edges + genDirectedEdge(researchers_doc, research_orgs_doc, None, None, "right_to_left")

# aggregate elements
elements = encounters_doc + patients_doc + doctors_doc + researchers_doc + insurance_doc + lab_output_doc
elements += clearing_houses_doc + facilities_doc + research_orgs_doc + researchers_doc + labs_doc

# create list of connected elements
#elements_in_play = []
#for edge in edges:
#  elements_in_play.append(edge["payload"]["left_element_id"])
#  elements_in_play.append(edge["payload"]["right_element_id"])
# todo remove non connected elements??

meta = {}
meta["num_entities"] = len(elements)
meta["num_encounters"] = len(encounters_doc)
meta["num_patients"] = len(patients_doc)
meta["num_doctors"] = len(doctors_doc)
meta["num_researchers"] = len(researchers_doc)
meta["num_clearing_houses"] = len(clearing_houses_doc)
meta["num_facilities"] = len(facilities_doc)
meta["num_research_orgs"] = len(research_orgs_doc)
meta["num_labs"] = len(labs_doc)
meta["num_insurance_providers"] = len(insurance_doc)
meta["num_lab_results"] = len(lab_output_doc)
meta["num_edges"] = len(edges)

doc = {}
doc["meta"] = meta
doc["entities"] = elements
doc["edges"] = edges

write_json("output/entity_data.json", doc)
print "\nPrinted entities and edges to output/entity_data.json."

print json.dumps(meta, indent=4, sort_keys=True)