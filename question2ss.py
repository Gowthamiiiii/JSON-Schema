import json
import sys


if len(sys.argv)-1 != 1:
    print("only DB Schema file should be sent as command line argument")

else:
    #schema
    with open(sys.argv[1], 'r') as db_sch:
        db_schema = json.load(db_sch)

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": [],
        "properties": {}
    }
    
    outer_schema = []
    
    refersTo_schema = {
        "type": "string"
    }
    
    outer_schema.append(refersTo_schema)
    entity_schema = {
        "type": "object",
        "required": [],
        "properties": {}
    }
    outer_schema.append(entity_schema)
    entities = db_schema['entities']
    for entity in entities:
        e_name = entity['name']
        
        e_prop = {}
        for attribute in entity['attributes']:           
            a_prop = {}
            if attribute['type'] == 'string':
                a_prop['type'] = ["string","integer"]
                a_prop['maxLength'] = attribute['size']
            elif attribute['type'] == 'integer':
                a_prop['type'] = ["string","integer"]
                a_prop['maximum'] = 10 ** attribute['size'] - 1
            
            e_prop[attribute['name']] = a_prop
        
        entity_schema['properties'][e_name] = {
            "type": ["string","integer","array"],
            "items": {
                "type": "object",
                "properties": e_prop,
                "required": [attribute['name'] for attribute in entity['attributes']]
            }
        }
    

    relation_schema = {
        "type": "object",
        "required": [],
        "properties": {}
    }
    outer_schema.append(relation_schema)
    for relationship in db_schema["relationships"]:
        r_name = relationship["name"]
        r_prop = {
            "type": ["string","integer","array"],
            "items": {
                "type": "object",
                "properties": {},
                "required": [],
                 "additionalItems": False,
                 "additionalProperties": False,
            }
        }

        for entity in relationship["entities"]:
            e_name = entity["name"]
            for i in db_schema['entities']:
                #print(i['name'],attribute_name)
                if i['name']==e_name:
                    e_name=i['primaryKey'][0]
                    if entity["participation"] == "mandatory":
                        r_prop['items']['required'] = [e_name]
            if entity["cardinality"] == "many":
                e_prop = {
                    "type": ["string","integer","array"],
                    "items": {"type": "integer"},
                    "required": [],
                     "additionalItems": False,
                    "additionalProperties": False,
                }
            else:
                e_prop = {"type": ["string","integer","array"]}

            r_prop["items"]["properties"][e_name] = e_prop

        for attribute in relationship["attributes"]:
            if attribute["type"] == "integer":
                a_prop = {"type": ["string","integer","array"]}
            else:
                a_prop = {
                    "type": "string",
                    "maxLength": attribute["size"],
                    "required": [],
                    "additionalItems": False,
                    "additionalProperties": False,
                }

            r_prop["items"]["properties"][attribute["name"]] = a_prop
        relation_schema["properties"][r_name] = r_prop
        
    for index,i in enumerate(db_schema):
        if i == 'name':
            schema["required"].append("refersTo")
            schema["properties"]['refersTo'] = outer_schema[index]
        else:
            schema["required"].append(i)
            schema["properties"][i] = outer_schema[index]
            
    with open('instance_schema.json', 'w') as files:
        json.dump(schema, files)
    print(json.dumps(schema, indent=2))