
All Parts works for both studentDB and DrinksDB

Part 1:

ModelSchema.json is valid for both StudentDBSchema.json and DrinksDBSchema.json

Part 2:

python3 GenerateInstanceSchema.py DrinksDBSchema.json  
output file is stored in filename GeneratedSchema.json

DB Schema file should be sent in command line argument as input.

Part 3:

python3 Validate.py DrinksDBSchema.json DrinksDBInstance.json GeneratedSchema.json

DB Schema file, DB Instance file and Generated Schema file should be sent as command line arguments in order

Part 4:

python3 GenerateRelationalDesign.py DrinksDBSchema.json 

only DB Schema file should be sent in command line argument as input