import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class UkdsCustomDcatProfilesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        
        # config_['ckanext.dcat.rdf.profiles'] = 'euro_dcat_ap ukds_dcat_ap'
        config_['ckanext.dcat.rdf.profiles'] = 'ukds_dcat_ap'