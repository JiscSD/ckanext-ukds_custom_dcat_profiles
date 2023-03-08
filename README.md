[![Tests](https://github.com/JiscSD/ckanext-ukds_custom_dcat_profiles/workflows/Tests/badge.svg?branch=main)](https://github.com/JiscSD/ckanext-ukds_custom_dcat_profiles/actions)

# ckanext-ukds_custom_dcat_profiles

This extension provides a custom profile based on the dataset properties (Following the writing custom profiles documentation ) for the UKDS CKAN platform.

It also provides an easy access to the API JSON format of the dataset and the DCAT RDF serialization format endpoints through the dataset page, having one list item per serialization format.
There is a popover implementation for information about Machine-readable data section links.

The profile will support future non-object fields that could be created in any of the structures of the dataset (dataset, organization, resources etc). For RDF serialization of future new objects and list, an enhancement of the current profile is required.

## Requirements

This is a custom profile to be used for the ckanext-dcat extension, so this extension needs to be installed.

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.6 and earlier | not tested    |
| 2.7             | not tested    |
| 2.8             | not tested    |
| 2.9             | yes           |

## Installation

To install ckanext-ukds_custom_dcat_profiles:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/JiscSD/ckanext-ukds_custom_dcat_profiles.git
    cd ckanext-ukds_custom_dcat_profiles
    pip install -e .
	pip install -r requirements.txt

3. Add `ukds_custom_dcat_profiles` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Developer installation

To install ckanext-ukds_custom_dcat_profiles for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/JiscSD/ckanext-ukds_custom_dcat_profiles.git
    cd ckanext-ukds_custom_dcat_profiles
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## Releasing a new version of ckanext-ukds_custom_dcat_profiles

If ckanext-ukds_custom_dcat_profiles should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `setup.py` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

2. Make sure you have the latest version of necessary packages:

    pip install --upgrade setuptools wheel twine

3. Create a source and binary distributions of the new version:

       python setup.py sdist bdist_wheel && twine check dist/*

   Fix any errors you get.

4. Upload the source distribution to PyPI:

       twine upload dist/*

5. Commit any outstanding changes:

       git commit -a
       git push

6. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:

       git tag 0.0.1
       git push --tags

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
