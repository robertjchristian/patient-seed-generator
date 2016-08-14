# patient-seed-generator
Generates fake patient and health data into a graph model for testing big data pipelines and analytics functionality

## Project Structure

### ./seed/names.txt
* Pipe delimited set of fake identities from http://www.fakenamegenerator.com/

###  ./seed2json.py
* Python script that builds json files (lists of entity add commands) of fake patient data from seed file
* Warning - running this script will delete existing output directory

### ./output 
* Contains files of json commands for depositing generated health info to a graph database
* This is wiped on each run of ./seed2json.py
* This is checked in to save generation time

## Names seed file
Contains the following information from which entities can be built
* **Personal**: firstname, lastname, gender, birthday, nationalid, ocupation, company, bloodtype, weightkilograms, heightcentimeters, age
* **Location**: street, city, state, zip, country
* **Contact**: email, telephone, countrycode,
* **Security**: username, password, mothersmaidenname

## Entity models

The seed2json.py generates a simplified data model for testing...

![alt text](https://raw.githubusercontent.com/robertjchristian/patient-seed-generator/master/patient_entity_model.png "Logo Title Text 1")

* **Encounter**:  
  *  Currently generating 50k encounters
  *  And encounter is the equivalent of an office visit, trip to ER, surgery, hospital stay, etc.  An encounter joins patients with doctors and a physical hospital location.  At each encounter, a patient may report symptoms or be diagnosed by doctor.  Drugs are not associated with encounters since presecriptions and usage start and end outside of the scope of an encounter.
* **Patient**:  
  * Currently generating 25k patients
  * Patient data includes personal, contact, location, and security data
* **Drugs** (not yet implemented):  
* **Doctor**:  
  * Currently generating 2k doctors 
  * Doctor records are similar to patient data but without health information
* **Hospital**:   
  * Currently generating 500 hospitals
  * Hospital records contain just a name and location information
* **Diagnosis** (not yet implemented):  
* **Symptoms** (not yet implenebted):  
* **Clearing house**:  
  * Currently generating 100 clearing houses
  * Clearing house records contain just a name and location information
* **Research Organization**:  
  * Currently generating 100 research organizations
  * Research organizations obtain cleansed personal health info through clearing houses
  * Research organization records contain just a name and location information
* **Researcher**: 
  * Currently generating 1,000 researchers
  * Researchers are associated with a research organization
* **Edges**:
  * Currently generating one random edge per encounter to research org, doctor, hospital, patient, and clearing house.
  * Currently generating one random research org edge per clearing house.
  * Currently generating one random research org edge per researcher.

## Neo4j setup

Setup neo4j and python connectivity

  * Install neo4j community edition
  * Start server without pointing to a database
  * Change password at http://localhost:7474/browser/
  * Change password in testneo4j.py to new password
  * Install python driver:  pip install neo4j-driver (https://neo4j.com/developer/python/)
  * run testneo4j.py - should see "King Arthur" print

## Seed Neo4j

...

## To do
* Add symptoms, drugs, diagnosis
* Client for pushing files to http endpoint and graph database