import os
import json
from datetime import datetime


def values_check(func):
    """ 
    Decorator function to check validity of key value pair inputs and the 
    existence of a schema term 
    """

    def func_wrapper(self, key, value, schema_val):
        if (key == 0) or (value == 0):
            raise Exception('A Key and Value must both be supplied')
        if key in ['id', '@id']:
            raise Exception('Graph Element ID can only be set during initialization')
        if key in ['type', '@type']:
            raise Exception('Graph Element type can only be set during initialization')
        if schema_val == '':
            raise Exception('A schema value must be supplied')

        res = func(self, key, value, schema_val)
        return res

    return func_wrapper


class Catalog:
    """ 
    A Catalog class 
    """

    def __init__(self):
        self.context = {}
        self.graph = []
        self.graph_element_ids = []

    def graph_element(self, id, type):
        """ 
        Instantiate and Append a new Graph Element to parent Catalog 
        """
        if id in self.graph_element_ids:
            raise Exception('A Graph Element with this ID already exists')

        ge = GraphElement(id, type, self)
        self.graph.append(ge)
        # Add the ID to the list of IDs for this catalog
        self.graph_element_ids.append(ge.id)

        return ge

    def context_append(self, key, schema_val):
        """ 
        Add a new context entry if it doesn't exist, else ignore 
        """

        if key not in self.context:
            self.context[key] = schema_val

    def export(self, path):
        """ Serialize myself to a JSON file """

        graph_serial = []
        for ge in self.graph:
            graph_serial.append(ge.data)
        data = {"@context": self.context, "@graph": graph_serial}

        with open(os.path.join(path, 'CATALOG.json'), 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4)


class GraphElement:
    """ An individual @graph element class """

    def __init__(self, id, type, catalog):
        self.id = id
        self.type = type
        self.catalog = catalog
        self.data = {}
        self.data['@id'] = self.id
        self.data['@type'] = self.type

    @values_check
    def add_attribute(self, key, value, schema_val):
        """ 
        Add or append a new key-value pair and schema definition 
        """

        # Check if a value already exists for this key and append value if so
        if key in self.data:
            if isinstance(self.data[key], str):
                self.data[key] = [self.data[key], value]
            elif isinstance(self.data[key], list):
                self.data[key].append(value)
        else:
            self.data[key] = value

        # Add schema value to context if not already existing
        self.catalog.context_append(key, schema_val)

    @values_check
    def add_link(self, key, value, schema_val):
        """ 
        Add or append a new link element 
        """

        # Check if a value already exists for this key and append value if so
        if key in self.data:
            self.data[key].append({"id": value})
        else:
            self.data[key] = [{"id": value}]

        # Add to context if not already existing
        if schema_val:
            self.catalog.context_append(key, schema_val)
