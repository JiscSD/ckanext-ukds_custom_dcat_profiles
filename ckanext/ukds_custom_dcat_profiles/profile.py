from rdflib import BNode, Literal
from rdflib.namespace import Namespace, RDF

from ckanext.dcat.profiles import RDFProfile, CleanedURIRef
from ckanext.dcat.utils import resource_uri

import json

# copied from ckanext.dcat.profiles
DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
ADMS = Namespace("http://www.w3.org/ns/adms#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace('http://schema.org/')
TIME = Namespace('http://www.w3.org/2006/time')
LOCN = Namespace('http://www.w3.org/ns/locn#')
GSP = Namespace('http://www.opengis.net/ont/geosparql#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
SPDX = Namespace('http://spdx.org/rdf/terms#')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
VOID = Namespace('http://rdfs.org/ns/void#')


namespaces = {
    # copied from ckanext.dcat.profiles
    'dct': DCT,
    'dcat': DCAT,
    'adms': ADMS,
    'vcard': VCARD,
    'foaf': FOAF,
    'schema': SCHEMA,
    'time': TIME,
    'skos': SKOS,
    'locn': LOCN,
    'gsp': GSP,
    'owl': OWL,
    'void': VOID,
}

DISTRIBUTION_LICENSE_FALLBACK_CONFIG = 'ckanext.dcat.resource.inherit.license'

custom = 'ukds:'


def create_node_properties(graph, node, object, ignored_fields = []):

    #Go through keys to create the properties.
    for key in object.keys():

        # Only create properties that are not listed as 'ignored'
        if key not in ignored_fields:
            
            # Only create primitive properties
            if isinstance(object.get(key), (str,int,float,bool)):

                graph.add((node,Literal(custom + key),Literal(object.get(key))))

            #If the property is None, you create the value as ""
            elif object.get(key) is None:

                graph.add((node,Literal(custom + key),Literal("")))

#Creating a comma separated string from a str list
def create_node_property_from_list(graph,node, list ,key = ""):

    
    at_str = ','.join(list)
    graph.add((node,Literal(custom + key),Literal(at_str)))

class UkdsCustomDcatProfilesProfile(RDFProfile):
    '''
    RDF Profile for UKDS CKAN
    Implementing custom profile based on the dataset properties (Following the writing custom profiles documentation ) for the UKDS CKAN platform.
    '''
    


    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        #Fields to handle specifically
        dataset_fields = [
            "geographic_spatial",
            "area_types",
            "frequency",
            "organization",
            "topics",
            "units",
            "years",
            "resources",
            "tags",
            "groups",
            "relationships_as_subject",
            "relationships_as_object"
        ]
        g.add((dataset_ref,RDF.type,DCAT.Dataset))

        create_node_properties(g,dataset_ref,dataset_dict,dataset_fields)

        #Dataset fields

        # area_types
        create_node_property_from_list(g,dataset_ref,dataset_dict.get('area_types'),'area_types')

        # frequency
        create_node_property_from_list(g,dataset_ref,dataset_dict.get('frequency'),'frequency')

        # topics
        create_node_property_from_list(g,dataset_ref,dataset_dict.get('topics'),'topics')

        # units
        create_node_property_from_list(g,dataset_ref,dataset_dict.get('units'),'units')

        # years
        create_node_property_from_list(g,dataset_ref,dataset_dict.get('years'),'years')

        # geographic_spatial
        gs_object = dataset_dict.get('geographic_spatial')

        #Create the node
        gs_node = BNode()

        #add a reference to the new node in the parent node
        g.add((dataset_ref, Literal(custom + 'geographic_spatial') , gs_node))
        
        # Start adding properties to the new node.
        g.add((gs_node,RDF.type,DCT.spatial))

        create_node_properties(g,gs_node,json.loads(gs_object))

        # Tags
        for tag in dataset_dict.get('tags'):

            g.add((dataset_ref, Literal(custom + 'tags') , Literal(tag['display_name'])))


        #Create the node for the organization
        organization = dataset_dict.get('organization')

        org_node = CleanedURIRef(organization.get('id'))

        g.add((dataset_ref, FOAF.organization, org_node))

        g.add((org_node,RDF.type,FOAF.organization))

        create_node_properties(g,org_node,organization)

        for resource in dataset_dict.get('resources'):
            
            #Create the node for the resource
            resource_node = CleanedURIRef(resource_uri(resource))
            
            #Reference the resource inside the dataset
            g.add((dataset_ref, DCAT.distribution, resource_node))

            #Add type
            g.add((resource_node,RDF.type,DCAT.distribution))

            #Create all the other properties
            create_node_properties(g,resource_node,resource)





        




        



