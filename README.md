# patient-seed-generator
Generates fake patient and health data into a graph model for testing

## Project Structure

### ./seed/names.txt
* Pipe delimited set of fake identities from http://www.fakenamegenerator.com/

###  ./seed2json.py
* Python script that builds json files (lists of entity add commands) of fake patient data from seed file

### ./output 
* Contains files of json commands for depositing generated health info to a graph database

## To do

* Add symptoms, drugs, diagnosis
* Client for pushing files to http endpoint and graph database