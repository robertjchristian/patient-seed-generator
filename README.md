# patient-seed-generator
Generates fake patient and health data into a graph model for testing

h2. Project Structure

h3. seed/names.txt
* Pipe delimited set of fake identities from http://www.fakenamegenerator.com/

h3.  seed2json.py
* Python script that builds json files (lists of entity add commands) of fake patient data from seed file

h3. output 
* Contains files of json commands for depositing generated health info to a graph database

h2. To do

* Add symptoms, drugs, diagnosis
* Client for pushing files to http endpoint and graph database