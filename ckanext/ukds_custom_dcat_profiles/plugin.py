import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class UkdsCustomDcatProfilesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    

    # IConfigurer

    def update_config(self, config_):
        
        config_['ckanext.dcat.rdf.profiles'] = 'ukds_dcat_ap'
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_resource('assets', 'ukds_custom_dcat_profiles')
