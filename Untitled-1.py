import json

with open('instance_file.json') as f:
    data = json.load(f)

# Check for data type errors in entity and relationship instances
for entity_name, entity_instances in data['entities'].items():
    for instance in entity_instances:
        for attribute_name, attribute_value in instance.items():
            schema = data['refersTo']['entities'][entity_name]['attributes'][attribute_name]
            if schema['dataType'] != type(attribute_value).__name__:
                print(f"Data type error in {entity_name} entity: {attribute_name} should be of type {schema['dataType']}, but found {type(attribute_value).__name__}")

# Check for primary key errors in entity instances
for entity_name, entity_instances in data['entities'].items():
    primary_key_attribute = data['refersTo']['entities'][entity_name]['primaryKey']
    primary_key_values = set()
    for instance in entity_instances:
        primary_key_value = instance[primary_key_attribute]
        if primary_key_value in primary_key_values:
            print(f"Primary key error in {entity_name} entity: {primary_key_value} is not unique")
        else:
            primary_key_values.add(primary_key_value)

# Check for cardinality errors in relationship instances
for relationship_name, relationship_instances in data['relationships'].items():
    schema = data['refersTo']['relationships'][relationship_name]
    if schema['cardinality'] == 'one-to-one':
        for instance in relationship_instances:
            if instance in relationship_instances[1:]:
                print(f"Cardinality error in {relationship_name} relationship: multiple instances of {instance}")
    elif schema['cardinality'] == 'one-to-many':
        for instance in relationship_instances:
            if instance in relationship_instances[1:]:
                print(f"Cardinality error in {relationship_name} relationship: multiple instances of {instance}")
    elif schema['cardinality'] == 'many-to-one':
        for instance in relationship_instances:
            if instance in relationship_instances[1:]:
                print(f"Cardinality error in {relationship_name} relationship: multiple instances of {instance}")
    elif schema['cardinality'] == 'many-to-many':
        for instance in relationship_instances:
            if instance in relationship_instances[1:]:
                print(f"Cardinality error in {relationship_name} relationship: multiple instances of {instance}")

# Check for participation errors in relationship instances
for relationship_name, relationship_instances in data['relationships'].items():
    schema = data['refersTo']['relationships'][relationship_name]
    for instance in relationship_instances:
        for participant_role in schema['participants']:
            entity_name = participant_role['entity']
            cardinality = participant_role['cardinality']
            if cardinality == 'one' and not any(instance.get(attribute_name) for attribute_name in data['refersTo']['entities'][entity_name]['attributes']):
                print(f"Participation error in {relationship_name} relationship: missing {entity_name} instance")
            elif cardinality == 'many' and not any(instance.get(attribute_name) for attribute_name in data['refersTo']['entities'][entity_name]['attributes']):
                print(f"Participation error in {relationship_name} relationship: missing {entity_name} instance")
                
# Check for invalid attributes in relationship instances
for relationship_name, relationship_instances in data['relationships'].items():
    schema = data['refersTo']['relationships'][relationship_name]
    for instance in relationship_instances:
        for attribute_name in instance:
            if attribute_name not in schema['participants'][0]['attributes'] and attribute_name not in schema['participants'][1]['attributes']:
                print(f"Invalid attribute")
