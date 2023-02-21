from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, RDFS, XSD

from ckan.common import config
from ckanext.dcat.profiles import RDFProfile, URIRefOrLiteral, CleanedURIRef
from ckanext.dcat.processors import RDFSerializer
import ckan.plugins.toolkit as toolkit
from ckanext.dcat.utils import resource_uri, publisher_uri_organization_fallback

import ckanext.customised_fields_from_tag_vocabulary.plugin as customFields

import json
import logging

log = logging.getLogger(__name__)

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

class UkdsCustomDcatProfilesProfile(RDFProfile):
    '''
    RDF Profile for UKDS CKAN
    Implementing fields just like in European DCAT-AP profile (`euro_dcat_ap`) and including custom fields
    '''

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        schema = toolkit.DefaultDatasetForm.show_package_schema(self)
        g.bind('dataset_schema', dataset_dict.keys())

        for prefix, namespace in namespaces.items():
            g.bind(prefix, namespace)

        g.add((dataset_ref, RDF.type, DCAT.Dataset))

        #UKDS Custom fields 
        # ----------------------------------------------------------------------------------
        #JSON SOLUTION
        # ----------------------------------------------------------------------------------

        # wkt field
        
        g.add((dataset_ref, DCT.spatial , Literal(dataset_dict.get('wkt'))))

        # Citation JSON
        
        citation_item = {
            'doi' : dataset_dict.get('doi'),
            'citation' : dataset_dict.get('citation')
        }

        g.add((dataset_ref, DCT.creator , Literal(json.dumps(citation_item))))
        
        # license JSON

        license_item = {
            'license_id' : dataset_dict.get('license_id'),
            'license_title' : dataset_dict.get('license_title'),
            'license_url' : dataset_dict.get('license_url')
        }
        
        g.add((dataset_ref, DCT.license , Literal(json.dumps(license_item))))

        # ukds_items = [
        #     ('wkt',DCT.spatial,None,Literal),
        #     ('citation', DCT.creator,None,Literal),
        #     ('doi',DCT.creator,None,Literal),
        #     ('license_id',DCT.license, None, Literal ),
        #     ('license_title',DCT.license, None, Literal ),
        #     ('license_url',DCT.license, None, Literal ),
        #     ]
        # self._add_triples_from_dict(dataset_dict, dataset_ref, ukds_items)

        # ----------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------

        # Basic fields
        items = [
            ('title', DCT.title, None, Literal),
            ('notes', DCT.description, None, Literal),
            ('url', DCAT.landingPage, None, URIRef),
            ('identifier', DCT.identifier, ['guid', 'id'], URIRefOrLiteral),
            ('version', OWL.versionInfo, ['dcat_version'], Literal),
            ('version_notes', ADMS.versionNotes, None, Literal),
            ('frequency', DCT.accrualPeriodicity, None, URIRefOrLiteral),
            ('access_rights', DCT.accessRights, None, URIRefOrLiteral),
            ('dcat_type', DCT.type, None, Literal),
            ('provenance', DCT.provenance, None, Literal),
        ]
        self._add_triples_from_dict(dataset_dict, dataset_ref, items)

        # Tags
        for tag in dataset_dict.get('tags', []):
            g.add((dataset_ref, FOAF.topic_interest, Literal(tag['name'])))

        # Dates
        items = [
            ('issued', DCT.issued, ['metadata_created'], Literal),
            ('modified', DCT.modified, ['metadata_modified'], Literal),
        ]
        self._add_date_triples_from_dict(dataset_dict, dataset_ref, items)

        #  Lists
        items = [
            ('language', DCT.language, None, URIRefOrLiteral),
            ('theme', DCAT.theme, None, URIRef),
            ('conforms_to', DCT.conformsTo, None, Literal),
            ('alternate_identifier', ADMS.identifier, None, URIRefOrLiteral),
            ('documentation', FOAF.page, None, URIRefOrLiteral),
            ('related_resource', DCT.relation, None, URIRefOrLiteral),
            ('has_version', DCT.hasVersion, None, URIRefOrLiteral),
            ('is_version_of', DCT.isVersionOf, None, URIRefOrLiteral),
            ('source', DCT.source, None, URIRefOrLiteral),
            ('sample', ADMS.sample, None, URIRefOrLiteral),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

        # Contact details
        if any([
            self._get_dataset_value(dataset_dict, 'contact_uri'),
            self._get_dataset_value(dataset_dict, 'contact_name'),
            self._get_dataset_value(dataset_dict, 'contact_email'),
            self._get_dataset_value(dataset_dict, 'maintainer'),
            self._get_dataset_value(dataset_dict, 'maintainer_email'),
            self._get_dataset_value(dataset_dict, 'author'),
            self._get_dataset_value(dataset_dict, 'author_email'),
        ]):

            contact_uri = self._get_dataset_value(dataset_dict, 'contact_uri')
            if contact_uri:
                contact_details = CleanedURIRef(contact_uri)
            else:
                contact_details = BNode()

            g.add((contact_details, RDF.type, VCARD.Organization))
            g.add((dataset_ref, DCAT.contactPoint, contact_details))

            self._add_triple_from_dict(
                dataset_dict, contact_details,
                VCARD.fn, 'contact_name', ['maintainer', 'author']
            )
            # Add mail address as URIRef, and ensure it has a mailto: prefix
            self._add_triple_from_dict(
                dataset_dict, contact_details,
                VCARD.hasEmail, 'contact_email', ['maintainer_email',
                                                  'author_email'],
                _type=URIRef, value_modifier=self._add_mailto
            )

        # Publisher
        if any([
            self._get_dataset_value(dataset_dict, 'publisher_uri'),
            self._get_dataset_value(dataset_dict, 'publisher_name'),
            dataset_dict.get('organization'),
        ]):

            publisher_uri = self._get_dataset_value(dataset_dict, 'publisher_uri')
            publisher_uri_fallback = publisher_uri_organization_fallback(dataset_dict)
            publisher_name = self._get_dataset_value(dataset_dict, 'publisher_name')
            if publisher_uri:
                publisher_details = CleanedURIRef(publisher_uri)
            elif not publisher_name and publisher_uri_fallback:
                # neither URI nor name are available, use organization as fallback
                publisher_details = CleanedURIRef(publisher_uri_fallback)
            else:
                # No publisher_uri
                publisher_details = BNode()

            g.add((publisher_details, RDF.type, FOAF.Organization))
            g.add((dataset_ref, DCT.publisher, publisher_details))

            # In case no name and URI are available, again fall back to organization.
            # If no name but an URI is available, the name literal remains empty to
            # avoid mixing organization and dataset values.
            if not publisher_name and not publisher_uri and dataset_dict.get('organization'):
                publisher_name = dataset_dict['organization']['title']

            g.add((publisher_details, FOAF.name, Literal(publisher_name)))
            # TODO: It would make sense to fallback these to organization
            # fields but they are not in the default schema and the
            # `organization` object in the dataset_dict does not include
            # custom fields
            items = [
                ('publisher_email', FOAF.mbox, None, Literal),
                ('publisher_url', FOAF.homepage, None, URIRef),
                ('publisher_type', DCT.type, None, URIRefOrLiteral),
            ]

            self._add_triples_from_dict(dataset_dict, publisher_details, items)

        # Temporal
        start = self._get_dataset_value(dataset_dict, 'temporal_start')
        end = self._get_dataset_value(dataset_dict, 'temporal_end')
        if start or end:
            temporal_extent = BNode()

            g.add((temporal_extent, RDF.type, DCT.PeriodOfTime))
            if start:
                self._add_date_triple(temporal_extent, SCHEMA.startDate, start)
            if end:
                self._add_date_triple(temporal_extent, SCHEMA.endDate, end)
            g.add((dataset_ref, DCT.temporal, temporal_extent))

        # Use fallback license if set in config
        resource_license_fallback = None
        if toolkit.asbool(config.get(DISTRIBUTION_LICENSE_FALLBACK_CONFIG, False)):
            if 'license_id' in dataset_dict and isinstance(URIRefOrLiteral(dataset_dict['license_id']), URIRef):
                resource_license_fallback = dataset_dict['license_id']
            elif 'license_url' in dataset_dict and isinstance(URIRefOrLiteral(dataset_dict['license_url']), URIRef):
                resource_license_fallback = dataset_dict['license_url']
        
        # Resources
        for resource_dict in dataset_dict.get('resources', []):

            distribution = CleanedURIRef(resource_uri(resource_dict))

            #UKDS customization
            # ----------------------------------------------------------------------------------
            # ----------------------------------------------------------------------------------
            # distribution_item = {
            #     'cache_last_updated' : resource_dict.get('cache_last_updated'),
            #     'cache_url' : resource_dict.get('cache_url'),
            #     'created' : resource_dict.get('created'),
            #     'datastore_active' : resource_dict.get('datastore_active'),
            #     'description' : resource_dict.get('description'),
            #     'format' : resource_dict.get('format'),
            #     'hash' : resource_dict.get('hash'),
            #     'id' : resource_dict.get('id'),
            #     'last_modified' : resource_dict.get('last_modified'),
            #     'metadata_modified' : resource_dict.get('metadata_modified'),
            #     'mimetype' : resource_dict.get('mimetype'),
            #     'mimetype_inner' : resource_dict.get('mimetype_inner'),
            #     'name' : resource_dict.get('name'),
            #     'package_id' : resource_dict.get('package_id'),
            #     'position' : resource_dict.get('position'),
            #     'resource_type' : resource_dict.get('resource_type'),
            #     'size' : resource_dict.get('size'),
            #     'state' : resource_dict.get('state'),
            #     'url' : resource_dict.get('url'),
            #     'url_type' : resource_dict.get('url_type'),
            # }

            # g.add((dataset_ref, DCAT.distribution, Literal(json.dumps(distribution_item))))
            
            # ----------------------------------------------------------------------------------
            # ----------------------------------------------------------------------------------

            g.add((dataset_ref, DCAT.distribution, distribution))

            #  Simple values
            items = [
                ('name', DCT.title, None, Literal),
                ('description', DCT.description, None, Literal),
                ('status', ADMS.status, None, URIRefOrLiteral),
                ('rights', DCT.rights, None, URIRefOrLiteral),
                ('license', DCT.license, None, URIRefOrLiteral),
                ('access_url', DCAT.accessURL, None, URIRef),
                ('download_url', DCAT.downloadURL, None, URIRef),
            ]

            self._add_triples_from_dict(resource_dict, distribution, items)

            #  Lists
            items = [
                ('documentation', FOAF.page, None, URIRefOrLiteral),
                ('language', DCT.language, None, URIRefOrLiteral),
                ('conforms_to', DCT.conformsTo, None, Literal),
            ]
            self._add_list_triples_from_dict(resource_dict, distribution, items)

            # Set default license for distribution if needed and available
            if resource_license_fallback and not (distribution, DCT.license, None) in g:
                g.add((distribution, DCT.license, URIRefOrLiteral(resource_license_fallback)))
            
             # Format
            mimetype = resource_dict.get('mimetype')
            fmt = resource_dict.get('format')

            # IANA media types (either URI or Literal) should be mapped as mediaType.
            # In case format is available and mimetype is not set or identical to format,
            # check which type is appropriate.
            if fmt and (not mimetype or mimetype == fmt):
                if ('iana.org/assignments/media-types' in fmt
                        or not fmt.startswith('http') and '/' in fmt):
                    # output format value as dcat:mediaType instead of dct:format
                    mimetype = fmt
                    fmt = None
                else:
                    # Use dct:format
                    mimetype = None

            if mimetype:
                g.add((distribution, DCAT.mediaType,
                       URIRefOrLiteral(mimetype)))

            if fmt:
                g.add((distribution, DCT['format'],
                       URIRefOrLiteral(fmt)))

            
            # URL fallback and old behavior
            url = resource_dict.get('url')
            download_url = resource_dict.get('download_url')
            access_url = resource_dict.get('access_url')
            # Use url as fallback for access_url if access_url is not set and download_url is not equal
            if url and not access_url:
                if (not download_url) or (download_url and url != download_url):
                  self._add_triple_from_dict(resource_dict, distribution, DCAT.accessURL, 'url', _type=URIRef)

            # Dates
            items = [
                ('issued', DCT.issued, ['created'], Literal),
                ('modified', DCT.modified, ['metadata_modified'], Literal),
            ]

            self._add_date_triples_from_dict(resource_dict, distribution, items)

            # Numbers
            if resource_dict.get('size'):
                try:
                    g.add((distribution, DCAT.byteSize,
                           Literal(float(resource_dict['size']),
                                   datatype=XSD.decimal)))
                except (ValueError, TypeError):
                    g.add((distribution, DCAT.byteSize,
                           Literal(resource_dict['size'])))
            # Checksum
            if resource_dict.get('hash'):
                checksum = BNode()
                g.add((checksum, RDF.type, SPDX.Checksum))
                g.add((checksum, SPDX.checksumValue,
                       Literal(resource_dict['hash'],
                               datatype=XSD.hexBinary)))

                if resource_dict.get('hash_algorithm'):
                    g.add((checksum, SPDX.algorithm,
                           URIRefOrLiteral(resource_dict['hash_algorithm'])))

                g.add((distribution, SPDX.checksum, checksum))