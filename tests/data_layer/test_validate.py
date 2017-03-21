"""Test config validation
"""
from pytest import fixture
from smif.data_layer.validate import (VALIDATION_ERRORS,
                                      validate_dependency,
                                      validate_input_spec,
                                      validate_interventions,
                                      validate_output,
                                      validate_output_spec,
                                      validate_planning_config,
                                      validate_sector_model_initial_config,
                                      validate_sos_model_config,
                                      validate_timesteps)


@fixture(scope='function')
def get_sos_model_config():
    """Return sample sos_model config
    """
    return {
        "sector_models": [
            {
                "name": "water_supply",
                "path": "../models/water_supply.py",
                "classname": "WaterSupplySectorModel",
                "config_dir": "../data/water_supply",
                "initial_conditions": [
                    "../data/water_supply/initial_conditions/initial_2015_oxford.yaml"
                ],
                "interventions": [
                    "../data/water_supply/interventions/types.yaml"
                ]
            }
        ],
        "timesteps": "timesteps.yaml",
        "scenario_data": [
            {
                "parameter": "population",
                "file": "../data/scenario/population.yaml",
                'spatial_resolution': 'national',
                'temporal_resolution': 'annual'
            },
            {
                "parameter": "raininess",
                "file": "../data/scenario/raininess.yaml",
                'spatial_resolution': 'national',
                'temporal_resolution': 'annual'
            }
        ],
        "region_sets": [{'name': 'national',
                         'file': '../data/national.shp'}],
        "interval_sets": [{'name': 'annual',
                           'file': '../data/annual_intervals.yaml'}],
        "planning": {
            "pre_specified": {
                "use": True,
                "files": [
                    "../planning/expected_to_2020.yaml",
                    "../planning/national_infrastructure_pipeline.yaml"
                ]
            },
            "rule_based": {
                "use": False
            },
            "optimisation": {
                "use": False
            }
        }
    }


@fixture(scope='function')
def get_sector_model_initial_config():
    """Return sample sector_model initial config
    """
    return {
        'name': 'test_model',
        'config_dir': '/path/to/config',
        'path': '/path/to/model/run.py',
        'classname': 'SectorModelImplementation'
    }


@fixture(scope='function')
def get_intervention():
    """Return sample intervention
    """
    return {
        'name': 'asset',
        'capacity': {
            'value': 3,
            'units': 'MW'
        },
        'location': 'galloway',
        'operational_lifetime': {
            'value': 150,
            'units': "years"
        },
        'economic_lifetime': {
            'value': 50,
            'units': "years"
        },
        'capital_cost': {
            'value': 50,
            'units': "million £/km"
        }
    }


@fixture(scope='function')
def get_input_spec():
    """Return sample input specification
    """
    return {
        'dependencies': [
            {
                'name': 'gas_demand',
                'spatial_resolution': 'national',
                'temporal_resolution': 'annual',
                'from_model': 'scenario'
            }
        ]
    }


@fixture(scope='function')
def get_dependency():
    """Return sample dependency
    """
    return {
        'name': 'gas_demand',
        'spatial_resolution': 'national',
        'temporal_resolution': 'annual',
        'from_model': 'scenario'
    }


@fixture(scope='function')
def get_output_spec():
    """Return sample output specification
    """
    return {
        'metrics': [
            {
                'name': 'total_cost',
                'spatial_resolution': 'national',
                'temporal_resolution': 'annual'
            }
        ]
    }


def test_modelrun_config_invalid():
    """Expect an error if not a dict
    """
    invalid_possibilities = [
        0,
        [],
        "just a string",
        3.1415
    ]

    for invalid_data in invalid_possibilities:
        validate_sos_model_config(invalid_data)
        ex = VALIDATION_ERRORS.pop()
        msg = "Main config file should contain setup data"
        assert msg in str(ex)


def test_invalid_timesteps_file(get_sos_model_config):

    """Expect an error if timesteps is not a path to a file
    """
    data = get_sos_model_config
    data['timesteps'] = 3

    validate_sos_model_config(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected 'timesteps' in main config to specify a timesteps file, instead got 3"
    assert msg in str(ex)


def test_invalid_timesteps():
    """Expect a list of timesteps, else error
    """
    data = 2010
    validate_timesteps(data, "timestep.yaml")
    ex = VALIDATION_ERRORS.pop()
    msg = "expected a list of timesteps"
    assert msg in str(ex)


def test_invalid_single_timestep():
    """Expect an error for non-integer timesteps
    """
    data = [2010, "January 2015"]
    validate_timesteps(data, "timestep.yaml")
    ex = VALIDATION_ERRORS.pop()
    msg = "timesteps should be integer years"
    assert msg in str(ex)


def test_missing_sector_models(get_sos_model_config):
    """Expect an error if missing sector_models
    """
    data = get_sos_model_config
    del data['sector_models']

    validate_sos_model_config(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "No 'sector_models' specified in main config"
    assert msg in str(ex)


def test_sector_models_not_list(get_sos_model_config):
    """Expect an error if sector_models is not a list
    """
    data = get_sos_model_config
    data['sector_models'] = 42

    validate_sos_model_config(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected 'sector_models' in main config to specify a list of sector " + \
          "models to run, instead got 42."
    assert msg in str(ex)


def test_sector_models_empty_list(get_sos_model_config):
    """Expect an error if sector_models is an empty list
    """
    data = get_sos_model_config
    data['sector_models'] = []

    validate_sos_model_config(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "No 'sector_models' specified in main config"
    assert msg in str(ex)


def test_sector_model_type(get_sos_model_config):
    """Expect an error if sector_model config is not a dict
    """
    data = get_sos_model_config
    data['sector_models'] = [None]

    validate_sos_model_config(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected a sector model config block"
    assert msg in str(ex)


def test_sector_model_required(get_sector_model_initial_config):
    """Expect an error if a sector_model is missing a required key
    """
    required_keys = ['name', 'config_dir', 'path', 'classname']
    for key in required_keys:
        data = get_sector_model_initial_config
        del data[key]

        validate_sector_model_initial_config(data)
        ex = VALIDATION_ERRORS.pop()
        msg = "Expected a value for '{}'".format(key)
        assert msg in str(ex)


def test_input_spec_type():
    """Expect an error if input_spec is not a dict
    """
    data = None
    validate_input_spec(data, 'energy_demand')
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected a list of dependencies in 'energy_demand' model input " + \
          "specification, instead got None"
    assert msg in str(ex)


def test_input_spec_deps():
    """Expect an error if input_spec is missing dependencies
    """
    data = {}
    validate_input_spec(data, 'energy_demand')
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected a list of dependencies in 'energy_demand' model input " + \
          "specification, instead got {}"
    assert msg in str(ex)


def test_input_spec_deps_list():
    """Expect an error if input_spec dependencies is not a list
    """
    data = {'dependencies': 1.618}
    validate_input_spec(data, 'energy_demand')
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected a list of dependencies in 'energy_demand' model input " + \
          "specification, instead got 1.618"
    assert msg in str(ex)


def test_input_spec_deps_list_empty():
    """Expect no errors for an empty list
    """
    data = {'dependencies': []}
    # empty is ok
    n_errors_before = len(VALIDATION_ERRORS)
    validate_input_spec(data, 'energy_demand')
    assert len(VALIDATION_ERRORS) == n_errors_before


def test_input_spec_deps_list_ok(get_input_spec):
    """Expect no errors for a list of valid dependencies
    """
    data = get_input_spec
    n_errors_before = len(VALIDATION_ERRORS)
    validate_input_spec(data, 'energy_demand')
    assert len(VALIDATION_ERRORS) == n_errors_before


def test_dependency_type(get_input_spec):
    """Expect an error if dependency is not a dict
    """
    data = 'single_string'
    validate_dependency(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected a dependency specification, " + \
          "instead got single_string"
    assert msg in str(ex)


def test_dependency_ok(get_dependency):
    """Expect no errors for a valid dependency
    """
    data = get_dependency
    n_errors_before = len(VALIDATION_ERRORS)
    validate_dependency(data)
    assert len(VALIDATION_ERRORS) == n_errors_before


def test_dependency_required(get_dependency):
    """Expect an error if dependency is missing required fields
    """
    required_keys = ['name', 'spatial_resolution', 'temporal_resolution', 'from_model']
    for key in required_keys:
        data = get_dependency
        del data[key]
        validate_dependency(data)
        ex = VALIDATION_ERRORS.pop()
        msg = "Expected a value for '{}' in each model dependency, " + \
            "only received {}"
        assert msg.format(key, data) in str(ex)


def test_output_spec_type():
    """Expect an error if output_spec is not a dict
    """
    data = None
    validate_output_spec(data, 'energy_demand')
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected a list of metrics in 'energy_demand' model output " + \
          "specification, instead got None"
    assert msg in str(ex)


def test_output_spec_deps():
    """Expect an error if output_spec is missing metrics
    """
    data = {}
    validate_output_spec(data, 'energy_demand')
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected a list of metrics in 'energy_demand' model output " + \
          "specification, instead got {}"
    assert msg in str(ex)


def test_output_spec_deps_list():
    """Expect an error if output_spec metrics is not a list
    """
    data = {'metrics': 1.618}
    validate_output_spec(data, 'energy_demand')
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected a list of metrics in 'energy_demand' model output " + \
          "specification, instead got 1.618"
    assert msg in str(ex)


def test_output_spec_deps_list_empty():
    """Expect no errors for an empty list
    """
    data = {'metrics': []}
    # empty is ok
    n_errors_before = len(VALIDATION_ERRORS)
    validate_output_spec(data, 'energy_demand')
    assert len(VALIDATION_ERRORS) == n_errors_before


def test_output_spec_list_str():
    data = {
        'metrics': ['these', 'outputs', 'should', 'not', 'be', 'a', 'list']
    }
    n_errors_before = len(VALIDATION_ERRORS)

    validate_output_spec(data, 'energy_demand')
    # should add one error per output spec:
    assert len(VALIDATION_ERRORS) == n_errors_before + len(data['metrics'])

    # last error, e.g.
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected an output specification, " + \
          "instead got list"
    assert msg in str(ex)


def test_output_spec_deps_list_ok(get_output_spec):
    """Expect no errors for a list of valid dependencies
    """
    data = get_output_spec
    n_errors_before = len(VALIDATION_ERRORS)
    validate_output_spec(data, 'energy_demand')
    assert len(VALIDATION_ERRORS) == n_errors_before


def test_output_type():
    """Expect an error if output is not a dict
    """
    data = 'single_string'
    validate_output(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "Expected an output specification, " + \
          "instead got single_string"
    assert msg in str(ex)


def test_output_ok(get_dependency):
    """Expect no errors for a valid output
    """
    data = get_dependency
    n_errors_before = len(VALIDATION_ERRORS)
    validate_output(data)
    assert len(VALIDATION_ERRORS) == n_errors_before


def test_output_required(get_dependency):
    """Expect an error if output is not a dict
    """
    required_keys = ['name', 'spatial_resolution', 'temporal_resolution']
    for key in required_keys:
        data = get_dependency
        del data[key]
        validate_output(data)
        ex = VALIDATION_ERRORS.pop()
        msg = "Expected a value for '{}' in each model output, " + \
            "only received {}"
        assert msg.format(key, data) in str(ex)


def test_missing_planning(get_sos_model_config):
    """Expect an error if missing planning
    """
    data = get_sos_model_config
    del data['planning']

    validate_sos_model_config(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "No 'planning' mode specified in main config"
    assert msg in str(ex)


def test_used_planning_needs_files(get_sos_model_config):
    """Expect an error if a planning mode is to be used, but has no files
    """
    data = get_sos_model_config
    del data["planning"]["pre_specified"]["files"]

    validate_sos_model_config(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "No 'files' provided for the 'pre_specified' planning type in main config"
    assert msg in str(ex)


def test_planning_missing_required(get_sos_model_config):
    """Expect an error if missing a planning mode
    """
    required_keys = ["pre_specified", "rule_based", "optimisation"]
    for key in required_keys:
        data = get_sos_model_config["planning"]
        del data[key]

        validate_planning_config(data)
        ex = VALIDATION_ERRORS.pop()
        msg = "No '{}' settings specified under 'planning'".format(key)
        assert msg in str(ex)


def test_planning_missing_use(get_sos_model_config):
    """Expect an error if a planning mode is missing "use""
    """
    data = get_sos_model_config["planning"]
    del data["rule_based"]["use"]

    validate_planning_config(data)
    ex = VALIDATION_ERRORS.pop()
    msg = "No 'use' settings specified for 'rule_based' 'planning'"
    assert msg in str(ex)


def test_interventions_missing_required(get_intervention):
    """Expect an error if an intervention is missing required key
    """
    required_keys = ["name", "location", "capital_cost",
                     "operational_lifetime",
                     "economic_lifetime"]

    for key in required_keys:
        intervention = get_intervention
        del intervention[key]

        data = [intervention]

        msg = "required a value for '{}' in each intervention".format(key)

        validate_interventions(data, "/path/to/data.yaml")
        ex = VALIDATION_ERRORS.pop()
        assert msg in str(ex)


def test_interventions_checks_for_units(get_intervention):
    """Expect an error if an intervention's "capacity" has no units
    """
    intervention = get_intervention
    intervention["capacity"] = 3

    data = [intervention]

    msg = "Loading interventions from /path/to/data.yaml, asset.capacity " + \
          "was 3 but should have specified units, e.g. " + \
          "{'value': 3, 'units': 'm'}"

    validate_interventions(data, "/path/to/data.yaml")
    ex = VALIDATION_ERRORS.pop()
    assert msg in str(ex)


class TestValidateMissingConfigSections:
    """Check that validation raises validation errors when whole sections of
    the configuration data are missing

    """
    def test_modelrun_config_validate(self, get_sos_model_config):
        """Expect no errors from a complete, valid config
        """
        validate_sos_model_config(get_sos_model_config)

    def test_missing_timestep(self, get_sos_model_config):
        """Expect an error if missing timesteps
        """
        data = get_sos_model_config
        del data['timesteps']

        validate_sos_model_config(data)
        ex = VALIDATION_ERRORS.pop()
        msg = "No 'timesteps' file specified in main config"
        assert msg in str(ex)

    def test_region_sets_missing(self, get_sos_model_config):
        """Expect an error if no region sets are specified
        """
        data = get_sos_model_config
        del data['region_sets']

        validate_sos_model_config(data)
        ex = VALIDATION_ERRORS.pop()
        msg = "No 'region_sets' specified in main config file."
        assert msg == str(ex)

    def test_interval_sets_missing(self, get_sos_model_config):
        """Expect an error if no time interval sets are specified
        """
        data = get_sos_model_config
        del data['interval_sets']

        validate_sos_model_config(data)
        ex = VALIDATION_ERRORS.pop()
        msg = "No 'interval_sets' specified in main config file."
        assert msg == str(ex)


class TestValidateMissingConfigurationReferences:
    """Check that validation raises validation errors when one part of the
    configuration assumes presence of a file or other configuration that is
    missing
    """

    def test_scenario_data_missing(self, get_sector_model_initial_config):
        """Expect an error if no scenario data is specified, but referenced in
        input file
        """
        pass
