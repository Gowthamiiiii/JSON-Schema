import json
import jsonschema
import sys
import xmlschema
from jsonschema import validate, Draft7Validator

if len(sys.argv)-1 != 3:
    print("DB Schema file, DB Instance file and Generated Schema file should be sent as command line arguments in order")
 
else:   
    #schema
    with open(sys.argv[1], 'r') as schema_file:
        db_schema = json.load(schema_file)
        
    #instance
    with open(sys.argv[2], 'r') as instance_file:
        db_instance = json.load(instance_file)
        
    #generated schema
    with open(sys.argv[3], 'r') as generated_schema_file:
        db_generated_schema = json.load(generated_schema_file)
        
    type_map = {
        'str': 'string',
        'int': 'integer',
        'float': 'number',
        'bool': 'boolean',
        'list': 'array',
        'dict': 'object'
    }


    try:
        jsonschema.validate(db_instance, db_generated_schema)
        print('Validation succeeded against the generated schema')
    except jsonschema.exceptions.ValidationError as e:
        print('Validation failed:', e.message)
        
        
        
    def schema_errors(db_schema,type_map):
        schema_error_flag = False
        # finding duplicate entities/relationships
        def duplicate_name(name):
            nonlocal schema_error_flag
            entity_name = {}
            for i in db_schema[name]:
                if 'name' in i:
                    if i['name'] in entity_name:
                        print("Duplicate", name, "name", "that is", i['name'])
                        schema_error_flag = True
                        break
                    else:
                        entity_name[i['name']] = 1
                        continue
            return schema_error_flag
        if duplicate_name('entities') or duplicate_name('relationships'):
            schema_error_flag = True


        # finding duplicate attributes from entities/relationships
        def duplicate_attr(name):
            running = True
            nonlocal schema_error_flag
            attribute_name = {}
            for i in db_schema[name]: 
                if 'attributes' in i:  
                    for j in i['attributes']:
                        if 'name' in j:
                            if j['name'] in attribute_name:
                                print("Duplicate attribute" ,j['name'] ,"in" ,name, "definition")
                                schema_error_flag = True
                                running = False
                                break
                            else:
                                attribute_name[j['name']] = 1
                                continue
                attribute_name = {}
            return schema_error_flag
        if duplicate_attr('entities') or duplicate_attr('relationships'):
            schema_error_flag = True

        # finding duplicate arrtibutes in primary_key set
        running = True
        attribute_name = {}
        for i in db_schema['entities']:  
            if "primaryKey" in i: 
                for j in i['primaryKey']:
                    if j in attribute_name:
                        print("Duplicate attribute",j,"found in primarykey definition")
                        schema_error_flag = True
                        running = False
                        break
                    else:
                        attribute_name[j] = 1
                        continue
                attribute_name = {}
        
            
        # Key attribute not in entity definition
        fla = True
        for i in db_schema['entities']:   
            no_keys = 0
            if "primaryKey" in i:
                keys_total = []
                for k in i['attributes']:
                    keys_total.append(k['name'])
                    for j in i['primaryKey']:
                        no_keys += 1
                        if j not in keys_total:
                            print("Key attribute not in entity definition",j, "in", i['name'])
                            schema_error_flag = True
                            fla = False
                    if no_keys == 0:
                        print("Key attribute not in entity definition found no keys in",i['name'])
                        schema_error_flag = True
                        fla = False
                        break
                    if not fla:
                        break

                        


        # Entity in relationship not defined
        for i in db_schema['relationships']:   
            no_entities = 0
            if 'entities' in i:
                for j in i['entities']:
                    no_entities += 1
                if no_entities == 1:
                    print("Entity in relationship not defined, only one entity is defined")
                    schema_error_flag = True
                    break
                if no_entities != 2:
                    print("Entity in relationship not defined")
                    schema_error_flag = True
                    break
        return schema_error_flag

    if not schema_errors(db_schema,type_map):
        print("schema is valid.")
    else:
        print("Errors are displayed above")


    def schema_errors(db_schema,db_instance,type_map):
        instance_error_flags = False
        # Check for Data type error in entity or relationship instance
        def type_error(name):
            running_type = True
            nonlocal instance_error_flags
            for entity, instances in db_instance[name].items():
                for inst in instances:
                    for attr, value in inst.items():
                        for i in db_schema[name]: 
                            if 'name' in i and i['name'] == entity: 
                                for attrr in i['attributes']:
                                    if 'name' in attrr and attrr['name'] == attr:
                                        if attrr['type'] == 'integer':
                                            if attrr['type'] != type_map[type(int(value)).__name__]:
                                                print("Data type error in" ,name, "instance at",entity, "in",attr,"with", type(value).__name__)
                                                instance_error_flags = True
                                                running_type = False
                                                break
                                        else:
                                            if 'type' in attrr and attrr['type'] != type_map[type(value).__name__]:
                                                print("Data type error in" ,name, "instance at",entity, "in",attr,"with", type(value).__name__)
                                                instance_error_flags = True
                                                running_type = False
                                                break
                                if not running_type:
                                    break
                        if not running_type:
                            break
                    if not running_type:
                        break
            return instance_error_flags
        if type_error('entities') and type_error('relationships'):
            instance_error_flags = True


        # Check for Primary key in entity error
        for i in db_schema['entities']:  
            if "primaryKey" in i: 
                for j in i['primaryKey']:
                    count = 0
                    for entity, instances in db_instance['entities'].items():
                        attr_values = []
                        for inst in instances:
                            for attr, value in inst.items():
                                attr_values.append(attr)
                        if 'name' in i and i['name'] == entity:
                            if j in attr_values:
                                count += 1
            if count != 1:
                print("Primary key in entity error",j, "found",count,"times")
                instance_error_flags = True
                break
                
                        
        #Check for Invalid attributes in relationship
        running_attr = True
        for entity in db_schema['relationships']: 
            my_list = []
            if len(entity['attributes']) != 0:
                for i_entity, i_instances in db_instance['relationships'].items():
                    if entity['name'] == i_entity and len(entity['attributes']) != 0:
                        for item in entity['attributes']:
                            my_list.append(item['name'])
                    for instt in i_instances:
                        if len(list(instt)) > 2:
                            add_data = []
                            for data in range(2, len(list(instt))):
                                add_data.append(list(instt)[data])
                            if not all(elem in my_list for elem in add_data):
                                print(entity['name'],"Invalid attributes in relationship")
                                instance_error_flags = True
                                break
                            
                        
                    
                    
        #Check for Participation error in relationship error
        parti_values = {}
        for entity, instances in db_instance['entities'].items():
            att_values = []
            for inst in instances:
                for attr, value in inst.items():
                    att_values.append(attr)
            att_values = list(set(att_values))
            parti_values[entity] = att_values
        #print(parti_values)
        for entity in db_schema['relationships']:
            for i in entity['entities']:
                if 'paricipation' in i and i['participation'] == "mandatory":
                    my_name = i['name']
                    #print(parti_values[i['name']])
            flag_ent = True
            for r_entity, r_instances in db_instance['relationships'].items():
                x = entity['name']
                if 'name' in entity and entity['name'] not in db_instance['relationships']:
                    xx = entity['entities']
                    for i in xx:
                        if i['participation'] == "mandatory":
                            print(entity['name'],'Participation error in relationship error')
                            instance_error_flags = True
                            flag_ent = False
                            break
                        if not flag_ent:
                            break
                elif 'name' in entity and entity['name'] in db_instance['relationships'] and len(db_instance['relationships'][x]) == 0:
                    #print(entity['name'])
                    for i in entity['entities']:
                        if i['participation'] == "mandatory" and entity['name'] == r_entity:
                            print(entity['name'],'Participation error in relationship error')
                            instance_error_flags = True
                            break
                else:
                    for i in entity['entities']:
                        if 'participation' in i and i['participation'] == "mandatory" and entity['name'] == r_entity:
                            attribu_values = []
                            for instt in r_instances:
                                for i_attr, i_value in instt.items():
                                    attribu_values.append(i_attr)
                            if not any(value in attribu_values for value in parti_values[i['name']]):
                                print(entity['name'],'Participation error in relationship error')
                                instance_error_flags = True
                                break


        #check for Cardinality error in relationship error
        parti_values = {}
        for entity, instances in db_instance['entities'].items():
            att_values = []
            for inst in instances:
                for attr, value in inst.items():
                    att_values.append(attr)
            att_values = list(set(att_values))
            parti_values[entity] = att_values
        for r_entity, r_instances in db_instance['relationships'].items():
            att_data = {}
            for entity in db_schema['relationships']:
                if entity['name'] == r_entity:
                    entities = entity['entities']
                    if any(e['cardinality'] == 'one' for e in entities):
                        if len(r_instances) != 0:
                            for record in r_instances:
                                my_list = list(inst.keys())
                                for r_ins in r_instances:
                                    my_list = list(r_ins.keys())
                                break
                            add_data = [[] for _ in range(len(entities))]
                            for i, entity in enumerate(entities):
                                for index, rec in enumerate(r_instances):
                                    if entity['cardinality'] == "many":
                                        list3 = parti_values[entity['name']]
                                        matching_words = [word for word in my_list if word in list3]
                                        add_data[i].append(rec[matching_words[0]])
                                    if entity['cardinality'] == "one":
                                        list2 = parti_values[entity['name']]
                                        matching_wordss = [word for word in my_list if word in list2]
                                        add_data[i].append(rec[matching_wordss[0]])
                            transposed_add_data = [list(x) for x in zip(*add_data)]
                            for item in transposed_add_data:
                                if transposed_add_data.count(item) > 1:
                                    print(entity['name'],"Cardinality error in relationship error")
                                    instance_error_flags = True
                                    break
    if not schema_errors(db_schema,db_instance,type_map):
        print("Instance file is valid against the given schema.")
    else:
        print("Errors are displayed above")
                    

                                
                        

            

