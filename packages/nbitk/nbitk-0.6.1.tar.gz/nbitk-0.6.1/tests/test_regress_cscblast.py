import json
import pytest
import os
from nbitk.config import Config
from nbitk.Services.BOLD.TaxonValidator import TaxonValidator

# Location of the JSON file containing records, provided by @luuk.nolden
CSC_RECORDS_JSON = os.path.join(os.path.dirname(__file__), 'data', 'records.json')

@pytest.fixture
def galaxy_config():
    """
    Fixture to create a Galaxy configuration object.
    :return: A Config object with Galaxy settings.
    """
    config = Config()
    config.config_data = {
        'log_level': 'DEBUG',
    }
    config.initialized = True
    return config

@pytest.fixture
def records_dict():
    """
    Fixture to load records from a JSON file.
    :return: A dictionary containing records.
    """
    with open(CSC_RECORDS_JSON, 'r') as handle:
        records = json.load(handle)
    return records

def test_taxon_validator(galaxy_config, records_dict):
    """
    Test the TaxonValidator service client.
    """
    config = galaxy_config

    # Now we instantiate the service client:
    tv = TaxonValidator(config)
    result = tv.validate_records(records_dict[0:100])
    assert result is not None, "Validation result should not be None"
