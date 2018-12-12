"""File-backed data store
"""
import glob
import os
from logging import getLogger

import numpy as np
import pandas
from smif.data_layer.abstract_data_store import DataStore
from smif.data_layer.data_array import DataArray
from smif.exception import SmifDataMismatchError, SmifDataNotFoundError


class CSVDataStore(DataStore):
    """CSV text file data store
    """
    def __init__(self, base_folder):
        super().__init__()
        self.logger = getLogger(__name__)
        self.base_folder = str(base_folder)
        self.data_folder = str(os.path.join(self.base_folder, 'data'))
        self.data_folders = {}
        self.results_folder = str(os.path.join(self.base_folder, 'results'))
        data_folders = [
            'coefficients',
            'strategies',
            'initial_conditions',
            'initial_inputs',
            'interventions',
            'narratives',
            'scenarios',
            'strategies',
            'parameters'
        ]
        for folder in data_folders:
            dirname = os.path.join(self.data_folder, folder)
            # ensure each directory exists
            if not os.path.exists(dirname):
                msg = "Expected data folder at '{}' but it does does not exist"
                abs_path = os.path.abspath(dirname)
                raise SmifDataNotFoundError(msg.format(abs_path))
            self.data_folders[folder] = dirname

    # region Data Array
    def read_scenario_variant_data(self, key, spec, timestep=None):
        path = os.path.join(self.data_folders['scenarios'], key)
        data = self._read_data_array(path, spec, timestep)
        data.validate_as_full()
        return data

    def write_scenario_variant_data(self, key, data, timestep=None):
        path = os.path.join(self.data_folders['scenarios'], key)
        self._write_data_array(path, data, timestep)

    def read_narrative_variant_data(self, key, spec, timestep=None):
        path = os.path.join(self.data_folders['narratives'], key)
        return self._read_data_array(path, spec, timestep)

    def write_narrative_variant_data(self, key, data, timestep=None):
        path = os.path.join(self.data_folders['narratives'], key)
        self._write_data_array(path, data, timestep)

    def read_model_parameter_default(self, key, spec):
        path = os.path.join(self.data_folders['parameters'], key)
        data = self._read_data_array(path, spec)
        data.validate_as_full()
        return data

    def write_model_parameter_default(self, key, data):
        path = os.path.join(self.data_folders['parameters'], key)
        self._write_data_array(path, data)

    def _read_data_array(self, path, spec, timestep=None):
        try:
            dataframe = pandas.read_csv(path)
        except FileNotFoundError:
            raise SmifDataNotFoundError

        if timestep is not None:
            if 'timestep' not in dataframe.columns:
                msg = "Missing 'timestep' key, found {} in {}"
                raise SmifDataMismatchError(msg.format(list(dataframe.columns), path))
            dataframe = dataframe[dataframe.timestep == timestep]
            dataframe.drop('timestep', axis=1, inplace=True)

        if spec.dims:
            dataframe.set_index(spec.dims, inplace=True)
            data_array = DataArray.from_df(spec, dataframe)
        else:
            # zero-dimensional case (scalar)
            data = dataframe[spec.name]
            if data.shape != (1,):
                msg = "Expected single value, found {} in {}"
                raise SmifDataMismatchError(msg.format(list(data.shape), path))
            data_array = DataArray(spec, data[0])
        print(dataframe)
        print(data_array)
        return data_array

    def _write_data_array(self, path, data_array, timestep=None):
        dataframe = data_array.as_df()
        if timestep is not None:
            dataframe['timestep'] = timestep
        dataframe.reset_index().to_csv(path, index=False)
    # endregion

    # region Interventions
    def read_interventions(self, keys):
        all_interventions = []
        for key in keys:
            path = os.path.join(self.data_folders['interventions'], key)
            interventions = self._read_file(path)
            all_interventions.extend(interventions)

        seen = set()
        dups = set()

        for intervention in all_interventions:
            name = intervention['name']
            if name in seen:
                dups.add(name)
            else:
                seen.add(name)

        if dups:
            name = dups.pop()
            msg = "An entry for intervention {} already exists. Also found duplicates for {}"
            raise ValueError(msg.format(name, dups))

        return {
            intervention['name']: _nest_keys(intervention)
            for intervention in all_interventions
        }

    def write_interventions(self, key, interventions):
        # convert dict[str, dict] to list[dict]
        data = [
            _unnest_keys(intervention)
            for intervention in interventions.values()
        ]
        path = os.path.join(self.data_folders['interventions'], key)
        self._write_file(path, data)

    def read_strategy_interventions(self, strategy):
        path = os.path.join(self.data_folders['strategies'], strategy['filename'])
        return self._read_file(path)

    def read_initial_conditions(self, keys):
        conditions = []
        for key in keys:
            path = os.path.join(self.data_folder, 'initial_conditions', key)
            data = self._read_file(path)
            conditions.extend(data)
        return conditions

    def write_initial_conditions(self, key, initial_conditions):
        path = os.path.join(self.data_folders['initial_conditions'], key)
        self._write_file(path, initial_conditions)

    def _read_file(self, path):
        """Read file to list[dict]
        """
        return pandas.read_csv(path).to_dict('records')

    def _write_file(self, path, data):
        """Write list[dict] to file
        """
        pandas.DataFrame.from_records(data).to_csv(path, index=False)
    # endregion

    # region State
    def read_state(self, modelrun_name, timestep, decision_iteration=None):
        path = self._get_state_path(modelrun_name, timestep, decision_iteration)
        try:
            state = self._read_file(path)
        except FileNotFoundError:
            msg = "State file does not exist for timestep {} and iteration {}"
            raise SmifDataNotFoundError(msg.format(timestep, decision_iteration))
        return state

    def write_state(self, state, modelrun_name, timestep=None, decision_iteration=None):
        path = self._get_state_path(modelrun_name, timestep, decision_iteration)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._write_file(path, state)

    def _get_state_path(self, modelrun_name, timestep=None, decision_iteration=None):
        """Compose a unique filename for state file:
                state_{timestep|0000}[_decision_{iteration}].csv
        """
        if timestep is None:
            timestep = '0000'

        if decision_iteration is None:
            separator = ''
            decision_iteration = ''
        else:
            separator = '_decision_'

        filename = 'state_{}{}{}.csv'.format(timestep, separator, decision_iteration)
        path = os.path.join(self.results_folder, modelrun_name, filename)

        return path
    # endregion

    # region Conversion coefficients
    def read_coefficients(self, source_spec, destination_spec):
        results_path = self._get_coefficients_path(source_spec, destination_spec)
        try:
            return np.loadtxt(results_path)
        except OSError:
            msg = "Could not find the coefficients file for %s to %s"
            self.logger.warning(msg, source_spec, destination_spec)
            raise SmifDataNotFoundError(msg.format(source_spec, destination_spec))

    def write_coefficients(self, source_spec, destination_spec, data):
        results_path = self._get_coefficients_path(source_spec, destination_spec)
        header = "Conversion coefficients {}:{}"
        np.savetxt(
            results_path, data,
            header=header.format(source_spec.name, destination_spec.name)
        )

    def _get_coefficients_path(self, source_spec, destination_spec):
        path = os.path.join(
            self.data_folders['coefficients'],
            "{}_{}.{}_{}.txt.gz".format(
                source_spec.name, "-".join(source_spec.dims),
                destination_spec.name, "-".join(destination_spec.dims)
            )
        )
        return path
    # endregion

    # region Results
    def read_results(self, modelrun_id, model_name, output_spec, timestep,
                     decision_iteration=None):
        if timestep is None:
            raise ValueError("You must pass a timestep argument")

        results_path = self._get_results_path(
            modelrun_id, model_name, output_spec.name,
            timestep, decision_iteration
        )

        try:
            return self._read_data_array(results_path, output_spec)
        except FileNotFoundError:
            key = str([modelrun_id, model_name, output_spec.name, timestep,
                       decision_iteration])
            raise SmifDataNotFoundError("Could not find results for {}".format(key))

    def write_results(self, data_array, modelrun_id, model_name, timestep=None,
                      decision_iteration=None):
        if timestep is None:
            raise NotImplementedError()

        if timestep:
            assert isinstance(timestep, int), "Timestep must be an integer"
        if decision_iteration:
            assert isinstance(decision_iteration, int), "Decision iteration must be an integer"

        results_path = self._get_results_path(
            modelrun_id, model_name, data_array.name,
            timestep, decision_iteration
        )
        os.makedirs(os.path.dirname(results_path), exist_ok=True)
        self._write_data_array(results_path, data_array)

    def available_results(self, modelrun_name):
        """List available results for a given model run

        See _get_results_path for path construction.

        On the pattern of:
            results/<modelrun_name>/<model_name>/
            decision_<id>/
            output_<output_name>_timestep_<timestep>.csv
        """
        paths = glob.glob(os.path.join(self.results_folder, modelrun_name, "*", "*", "*.csv"))
        # (timestep, decision_iteration, model_name, output_name)
        results_keys = []
        for path in paths:
            timestep, decision_iteration, model_name, output_name = \
                self._parse_results_path(path)
            results_keys.append(
                (timestep, decision_iteration, model_name, output_name)
            )
        return results_keys

    def _get_results_path(self, modelrun_id, model_name, output_name, timestep,
                          decision_iteration=None):
        """Return path to filename for a given output without file extension

        On the pattern of:
            results/<modelrun_name>/<model_name>/
            decision_<id>/
            output_<output_name>_timestep_<timestep>.csv

        Parameters
        ----------
        modelrun_id : str
        model_name : str
        output_name : str
        timestep : str or int
        decision_iteration : int, optional

        Returns
        -------
        path : strs
        """
        if decision_iteration is None:
            decision_iteration = 'none'

        path = os.path.join(
            self.results_folder, modelrun_id, model_name,
            "decision_{}".format(decision_iteration),
            "output_{}_timestep_{}.{}".format(output_name, timestep, 'csv')
        )
        return path

    def _parse_results_path(self, path):
        """Return result metadata for a given result path

        On the pattern of:
            results/<modelrun_name>/<model_name>/
            decision_<id>/
            output_<output_name>_timestep_<timestep>.csv

        Parameters
        ----------
        path : str

        Returns
        -------
        tuple : (timestep, decision_iteration, model_name, output_name)
        """
        # split to last directories and filename
        model_name, decision_str, output_str = path.split(os.sep)[-3:]
        # trim "decision_"
        decision_iteration = int(decision_str[9:])
        # trim "output_" [...] ".csv"
        output_str_trimmed = output_str[7:-4]
        # pick (str) output and (integer) timestep
        output_name, timestep_str = output_str_trimmed.split("_timestep_")
        timestep = int(timestep_str)

        return (timestep, decision_iteration, model_name, output_name)
    # endregion


def _nest_keys(intervention):
    nested = {}
    for key, value in intervention.items():
        if key.endswith(('_value', '_unit')):
            new_key, sub_key = key.rsplit(sep="_", maxsplit=1)
            if new_key in nested:
                if not isinstance(nested[new_key], dict):
                    msg = "Duplicate heading in csv data: {}"
                    raise ValueError(msg.format(new_key))
                else:
                    nested[new_key].update({sub_key: value})
            else:
                nested[new_key] = {sub_key: value}
        else:
            if key in nested:
                msg = "Duplicate heading in csv data: {}"
                raise ValueError(msg.format(new_key))
            else:
                nested[key] = value
    return nested


def _unnest_keys(intervention):
    unnested = {}
    for key, value in intervention.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value:
                unnested["{}_{}".format(key, sub_key)] = sub_value
        else:
            unnested[key] = value
    return unnested
