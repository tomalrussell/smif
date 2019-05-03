"""Test the Results interface
"""

import os

import numpy as np
import pandas as pd
from pytest import fixture, raises
from smif.data_layer import DataArray, Results
from smif.exception import SmifDataNotFoundError
from smif.metadata import Spec


@fixture
def results(empty_store):
    """Results fixture
    """
    return Results(store=empty_store)


@fixture
def results_with_results(empty_store):
    """Results fixture with a model run and fictional results
    """
    empty_store.write_dimension({
        'name': 'sample_dim',
        'elements': [ {'name': 'a'}, {'name': 'b'} ]
    })
    sample_output = {
        'name': 'sample_output',
        'dtype': 'float',
        'dims': ['sample_dim'],
        'coords': { 'sample_dim': [ {'name': 'a'}, {'name': 'b'} ] },
        'unit': 'm'
    }
    empty_store.write_model({
        'name': 'a_model',
        'description': "Sample model",
        'classname': 'DoesNotExist',
        'path': '/dev/null',
        'inputs': [],
        'outputs': [sample_output],
        'parameters': [],
        'interventions': [],
        'initial_conditions': []
    })
    empty_store.write_model({
        'name': 'b_model',
        'description': "Second sample model",
        'classname': 'DoesNotExist',
        'path': '/dev/null',
        'inputs': [],
        'outputs': [sample_output],
        'parameters': [],
        'interventions': [],
        'initial_conditions': []
    })
    empty_store.write_sos_model({
        'name': 'a_sos_model',
        'description': 'Sample SoS',
        'sector_models': ['a_model', 'b_model'],
        'scenarios': [],
        'scenario_dependencies': [],
        'model_dependencies': [],
        'narratives': []
    })
    empty_store.write_model_run({
        'name': 'model_run_1',
        'description': 'Sample model run',
        'timesteps': [2010, 2015, 2020, 2025, 2030],
        'sos_model': 'a_sos_model',
        'scenarios': {},
        'strategies': [],
        'narratives': {}
    })
    empty_store.write_model_run({
        'name': 'model_run_2',
        'description': 'Sample model run',
        'timesteps': [2010, 2015, 2020, 2025, 2030],
        'sos_model': 'a_sos_model',
        'scenarios': {},
        'strategies': [],
        'narratives': {}
    })

    spec = Spec.from_dict(sample_output)
    data = np.zeros((2,), dtype=float)
    sample_results = DataArray(spec, data)

    empty_store.write_results(sample_results, 'model_run_1', 'a_model', 2010, 0)
    empty_store.write_results(sample_results, 'model_run_1', 'a_model', 2015, 0)
    empty_store.write_results(sample_results, 'model_run_1', 'a_model', 2020, 0)
    empty_store.write_results(sample_results, 'model_run_1', 'a_model', 2015, 1)
    empty_store.write_results(sample_results, 'model_run_1', 'a_model', 2020, 1)
    empty_store.write_results(sample_results, 'model_run_1', 'a_model', 2015, 2)
    empty_store.write_results(sample_results, 'model_run_1', 'a_model', 2020, 2)

    empty_store.write_results(sample_results, 'model_run_1', 'b_model', 2010, 0)
    empty_store.write_results(sample_results, 'model_run_1', 'b_model', 2015, 0)
    empty_store.write_results(sample_results, 'model_run_1', 'b_model', 2020, 0)
    empty_store.write_results(sample_results, 'model_run_1', 'b_model', 2025, 0)
    empty_store.write_results(sample_results, 'model_run_1', 'b_model', 2030, 0)

    return Results(store=empty_store)


class TestNoResults:

    def test_exceptions(self, empty_store):

        # No arguments is not allowed
        with raises(TypeError) as e:
            Results()
        assert "missing 1 required positional argument: 'store'" in str(e)

        # Check that constructing with just a store works fine
        Results(store=empty_store)

        # Check that valid configurations do work (but expect a SmifDataNotFoundError
        # because the store creation will fall over
        with raises(SmifDataNotFoundError) as e:
            Results(store={'interface': 'local_csv', 'dir': '.'})
        assert 'Expected data folder' in str(e)

        with raises(SmifDataNotFoundError) as e:
            Results(store={'interface': 'local_parquet', 'dir': '.'})
        assert 'Expected data folder' in str(e)

        # Interface left blank will default to local_csv
        with raises(SmifDataNotFoundError) as e:
            Results(store={'dir': '.'})
        assert 'Expected data folder' in str(e)

        # Dir left blank will default to '.'
        with raises(SmifDataNotFoundError) as e:
            Results(store={'interface': 'local_parquet'})
        assert 'Expected data folder' in str(e)

        # Invalid interface will raise a ValueError
        with raises(ValueError) as e:
            Results(store={'interface': 'invalid', 'dir': '.'})
        assert 'Unsupported interface "invalid"' in str(e)

        # Invalid directory will raise a ValueError
        with raises(ValueError) as e:
            invalid_dir = os.path.join(os.path.dirname(__file__), 'does', 'not', 'exist')
            Results(store={'interface': 'local_csv', 'dir': invalid_dir})
        assert 'to be a valid directory' in str(e)

    def test_list_model_runs(self, results_with_results):
        assert results_with_results.list_model_runs() == ['model_run_1', 'model_run_2']

    def test_list_no_model_runs(self, results):
        # Should be no model runs in an empty Results()
        assert results.list_model_runs() == []

    def test_available_results(self, results_with_results):
        available = results_with_results.available_results('model_run_1')

        assert available['model_run'] == 'model_run_1'
        assert available['sos_model'] == 'a_sos_model'
        assert available['sector_models'] == {
            'a_model': {
                'outputs': {
                    'sample_output': {
                        0: [2010, 2015, 2020],
                        1: [2015, 2020],
                        2: [2015, 2020]
                    }
                }
            },
            'b_model': {
                'outputs': {
                    'sample_output': {
                        0: [2010, 2015, 2020, 2025, 2030]
                    }
                }
            }
        }


class TestSomeResults:

    def test_available_results(self, results_with_results):

        available = results_with_results.available_results('model_run_1')

        assert available['model_run'] == 'model_run_1'
        assert available['sos_model'] == 'a_sos_model'

        sec_models = available['sector_models']
        assert sorted(sec_models.keys()) == ['a_model', 'b_model']

        # Check a_model outputs are correct
        outputs_a = sec_models['a_model']['outputs']
        assert sorted(outputs_a.keys()) == ['sample_output']

        output_answer_a = {0: [2010, 2015, 2020], 1: [2015, 2020], 2: [2015, 2020]}
        assert outputs_a['sample_output'] == output_answer_a

        # Check b_model outputs are correct
        outputs_b = sec_models['b_model']['outputs']
        assert sorted(outputs_b.keys()) == ['sample_output']

        output_answer_b = {0: [2010, 2015, 2020, 2025, 2030]}
        assert outputs_b['sample_output'] == output_answer_b

    def test_read_validate_names(self, results_with_results):

        # Passing anything other than one sector model or output is current not implemented
        with raises(NotImplementedError) as e:
            results_with_results.read(
                model_run_names=['model_run_1', 'model_run_2'],
                model_names=[],
                output_names=['sample_output']
            )
        assert 'requires exactly one sector model' in str(e.value)

        with raises(NotImplementedError) as e:
            results_with_results.read(
                model_run_names=['model_run_1', 'model_run_2'],
                model_names=['a_model', 'b_model'],
                output_names=['one']
            )
        assert 'requires exactly one sector model' in str(e.value)

        with raises(ValueError) as e:
            results_with_results.read(
                model_run_names=[],
                model_names=['a_model'],
                output_names=['sample_output']
            )
        assert 'requires at least one sector model name' in str(e.value)

        with raises(ValueError) as e:
            results_with_results.read(
                model_run_names=['model_run_1'],
                model_names=['a_model'],
                output_names=[]
            )
        assert 'requires at least one output name' in str(e.value)


    def test_read(self, results_with_results):
        # This is difficult to test without fixtures defining an entire canonical project.
        # See smif issue #304 (https://github.com/nismod/smif/issues/304).

        # should pass validation
        results_data = results_with_results.read(
            model_run_names=['model_run_1'],
            model_names=['a_model'],
            output_names=['sample_output']
        )
        print(results_data)
        expected = pd.DataFrame({
            'model_run': 'model_run_1',
            'timestep': [
                2010, 2015, 2015, 2015, 2020, 2020, 2020,
                2010, 2015, 2015, 2015, 2020, 2020, 2020],
            'decision': [
                0, 0, 1, 2, 0, 1, 2,
                0, 0, 1, 2, 0, 1, 2],
            'sample_dim': [
                'a', 'a', 'a', 'a', 'a', 'a', 'a',
                'b', 'b', 'b', 'b', 'b', 'b', 'b'],
            'sample_output': 0.0,
        })
        pd.testing.assert_frame_equal(results_data, expected)
