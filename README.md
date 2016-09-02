# patient-seed-generator
Generates fake patient and health data into a graph model for testing big data pipelines and analytics functionality

## Project Structure

### ./seed
* Raw data inputs

###  ./seed2json.py
* Builds json entities and edges
* Warning - running this script will delete existing output directory

### ./output 
* Contains files of json commands for depositing generated health info to a graph database
* This is wiped on each run of ./seed2json.py
* This is checked in to save generation time

## Entity models

The seed2json.py generates a simplified data model for testing...

![alt text](https://raw.githubusercontent.com/robertjchristian/patient-seed-generator/master/patient_entity_model.png "Entity Model")

Currently generating:
{
    "num_clearing_houses": 1000, 
    "num_doctors": 500, 
    "num_edges": 43550, 
    "num_encounters": 10000, 
    "num_entities": 32707, 
    "num_facilities": 1000, 
    "num_insurance_providers": 45, 
    "num_lab_results": 5137, 
    "num_labs": 25, 
    "num_patients": 10000, 
    "num_research_orgs": 1000, 
    "num_researchers": 2000
}

## Neo4j setup

Setup neo4j and python connectivity

  * Install neo4j community edition.  Download and extract tar: https://neo4j.com/download/other-releases/
  * Start server: bin/neo4j start
  * Change password at http://localhost:7474/browser/ to healthcare123 (to match scripts)
  * Install python driver:  pip install neo4j-driver (https://neo4j.com/developer/python/)
  * run testneo4j.py - should see "King Arthur" print
  * Install rest client: pip install neo4jrestclient
  * pip install dicttoxml for datums


## Seed Neo4j

...