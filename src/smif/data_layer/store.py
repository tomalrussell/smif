"""The store provides a common data interface to smif configuration, data and metadata.

Raises
------
SmifDataNotFoundError
    If data cannot be found in the store when try to read from the store
SmifDataExistsError
    If data already exists in the store when trying to write to the store
    (use an update method instead)
SmifDataMismatchError
    Data presented to read, write and update methods is in the
    incorrect format or of wrong dimensions to that expected
SmifDataReadError
    When unable to read data e.g. unable to handle file type or connect
    to database
"""
from copy import deepcopy
from logging import getLogger


class Store():
    """Common interface to data store, composed of config, metadata and data store implementations.

    Parameters
    ----------
    config_store: ~smif.data_layer.abstract_config_store.ConfigStore
    metadata_store: ~smif.data_layer.abstract_metadata_store.MetadataStore
    data_store: ~smif.data_layer.abstract_data_store.DataStore
    """
    def __init__(self, config_store, metadata_store, data_store):
        self.logger = getLogger(__name__)
        self.config_store = config_store
        self.metadata_store = metadata_store
        self.data_store = data_store

    #
    # CONFIG
    #

    # region Model runs
    def read_model_runs(self):
        """Read all system-of-system model runs

        Returns
        -------
        list[~smif.controller.modelrun.ModelRun]
        """
        return self.config_store.read_model_runs()

    def read_model_run(self, model_run_name):
        """Read a system-of-system model run

        Parameters
        ----------
        model_run_name : str

        Returns
        -------
        ~smif.controller.modelrun.ModelRun
        """
        return self.config_store.read_model_run(model_run_name)

    def write_model_run(self, model_run):
        """Write system-of-system model run

        Parameters
        ----------
        model_run : ~smif.controller.modelrun.ModelRun
        """
        self.config_store.write_model_run(model_run)

    def update_model_run(self, model_run_name, model_run):
        """Update system-of-system model run

        Parameters
        ----------
        model_run_name : str
        model_run : ~smif.controller.modelrun.ModelRun
        """
        self.config_store.update_model_run(model_run_name, model_run)

    def delete_model_run(self, model_run_name):
        """Delete a system-of-system model run

        Parameters
        ----------
        model_run_name : str
        """
        self.config_store.delete_model_run(model_run_name)
    # endregion

    # region System-of-systems models
    def read_sos_models(self):
        """Read all system-of-system models

        Returns
        -------
        list[~smif.model.sos_model.SosModel]
        """
        return self.config_store.read_sos_models()

    def read_sos_model(self, sos_model_name):
        """Read a specific system-of-system model

        Parameters
        ----------
        sos_model_name : str

        Returns
        -------
        ~smif.model.sos_model.SosModel
        """
        return self.config_store.read_sos_model(sos_model_name)

    def write_sos_model(self, sos_model):
        """Write system-of-system model

        Parameters
        ----------
        sos_model : ~smif.model.sos_model.SosModel
        """
        self.config_store.write_sos_model(sos_model)

    def update_sos_model(self, sos_model_name, sos_model):
        """Update system-of-system model

        Parameters
        ----------
        sos_model_name : str
        sos_model : ~smif.model.sos_model.SosModel
        """
        self.config_store.update_sos_model(sos_model_name, sos_model)

    def delete_sos_model(self, sos_model_name):
        """Delete a system-of-system model

        Parameters
        ----------
        sos_model_name : str
        """
        self.config_store.delete_sos_model(sos_model_name)
    # endregion

    # region Models
    def read_models(self, skip_coords=False):
        """Read all models

        Returns
        -------
        list[~smif.model.model.Model]
        """
        models = self.config_store.read_models()
        if not skip_coords:
            models = [
                self._add_coords(model, ('inputs', 'outputs', 'parameters'))
                for model in models
            ]
        return models

    def read_model(self, model_name, skip_coords=False):
        """Read a model

        Parameters
        ----------
        model_name : str

        Returns
        -------
        ~smif.model.model.Model
        """
        model = self.config_store.read_model(model_name)
        if not skip_coords:
            model = self._add_coords(model, ('inputs', 'outputs', 'parameters'))
        return model

    def write_model(self, model):
        """Write a model

        Parameters
        ----------
        model : ~smif.model.model.Model
        """
        self.config_store.write_model(model)

    def update_model(self, model_name, model):
        """Update a model

        Parameters
        ----------
        model_name : str
        model : ~smif.model.model.Model
        """
        self.config_store.update_model(model_name, model)

    def delete_model(self, model_name):
        """Delete a model

        Parameters
        ----------
        model_name : str
        """
        self.config_store.delete_model(model_name)
    # endregion

    # region Scenarios
    def read_scenarios(self, skip_coords=False):
        """Read scenarios

        Returns
        -------
        list[~smif.model.ScenarioModel]
        """
        scenarios = self.config_store.read_scenarios()
        if not skip_coords:
            scenarios = [
                self._add_coords(scenario, ['provides'])
                for scenario in scenarios
            ]
        return scenarios

    def read_scenario(self, scenario_name, skip_coords=False):
        """Read a scenario

        Parameters
        ----------
        scenario_name : str

        Returns
        -------
        ~smif.model.ScenarioModel
        """
        scenario = self.config_store.read_scenario(scenario_name)
        if not skip_coords:
            scenario = self._add_coords(scenario, ['provides'])
        return scenario

    def write_scenario(self, scenario):
        """Write scenario

        Parameters
        ----------
        scenario : ~smif.model.ScenarioModel
        """
        self.config_store.write_scenario(scenario)

    def update_scenario(self, scenario_name, scenario):
        """Update scenario

        Parameters
        ----------
        scenario_name : str
        scenario : ~smif.model.ScenarioModel
        """
        self.config_store.update_scenario(scenario_name, scenario)

    def delete_scenario(self, scenario_name):
        """Delete scenario from project configuration

        Parameters
        ----------
        scenario_name : str
        """
        self.config_store.delete_scenario(scenario_name)
    # endregion

    # region Scenario Variants
    def read_scenario_variants(self, scenario_name):
        """Read variants of a given scenario

        Parameters
        ----------
        scenario_name : str

        Returns
        -------
        list[dict]
        """
        return self.config_store.read_scenario_variants(scenario_name)

    def read_scenario_variant(self, scenario_name, variant_name):
        """Read a scenario variant

        Parameters
        ----------
        scenario_name : str
        variant_name : str

        Returns
        -------
        dict
        """
        return self.config_store.read_scenario_variant(scenario_name, variant_name)

    def write_scenario_variant(self, scenario_name, variant):
        """Write scenario to project configuration

        Parameters
        ----------
        scenario_name : str
        variant : dict
        """
        self.config_store.write_scenario_variant(scenario_name, variant)

    def update_scenario_variant(self, scenario_name, variant_name, variant):
        """Update scenario to project configuration

        Parameters
        ----------
        scenario_name : str
        variant_name : str
        variant : dict
        """
        self.config_store.update_scenario_variant(scenario_name, variant_name, variant)

    def delete_scenario_variant(self, scenario_name, variant_name):
        """Delete scenario from project configuration

        Parameters
        ----------
        scenario_name : str
        variant_name : str
        """
        self.config_store.delete_scenario_variant(scenario_name, variant_name)
    # endregion

    # region Narratives
    def read_narrative(self, sos_model_name, narrative_name):
        """Read narrative from sos_model

        Parameters
        ----------
        sos_model_name : str
        narrative_name : str
        """
        return self.config_store.read_narrative(sos_model_name, narrative_name)
    # endregion

    # region Strategies
    def read_strategies(self, model_run_name):
        """Read strategies for a given model run

        Parameters
        ----------
        model_run_name : str

        Returns
        -------
        list[dict]
        """
        return self.config_store.read_strategies(model_run_name)

    def write_strategies(self, model_run_name, strategies):
        """Write strategies for a given model_run

        Parameters
        ----------
        model_run_name : str
        strategies : list[dict]
        """
        self.config_store.write_strategies(model_run_name, strategies)
    # endregion

    #
    # METADATA
    #

    # region Units
    def read_unit_definitions(self):
        """Reads custom unit definitions

        Returns
        -------
        list[str]
            Pint-compatible unit definitions
        """
        return self.metadata_store.read_unit_definitions()

    def write_unit_definitions(self, definitions):
        """Reads custom unit definitions

        Parameters
        ----------
        list[str]
            Pint-compatible unit definitions
        """
        self.metadata_store.write_unit_definitions(definitions)
    # endregion

    # region Dimensions
    def read_dimensions(self):
        """Read dimensions

        Returns
        -------
        list[~smif.metadata.coords.Coords]
        """
        return self.metadata_store.read_dimensions()

    def read_dimension(self, dimension_name):
        """Return dimension

        Parameters
        ----------
        dimension_name : str

        Returns
        -------
        ~smif.metadata.coords.Coords
            A dimension definition (including elements)
        """
        return self.metadata_store.read_dimension(dimension_name)

    def write_dimension(self, dimension):
        """Write dimension to project configuration

        Parameters
        ----------
        dimension : ~smif.metadata.coords.Coords
        """
        self.metadata_store.write_dimension(dimension)

    def update_dimension(self, dimension_name, dimension):
        """Update dimension

        Parameters
        ----------
        dimension_name : str
        dimension : ~smif.metadata.coords.Coords
        """
        self.metadata_store.update_dimension(dimension_name, dimension)

    def delete_dimension(self, dimension_name):
        """Delete dimension

        Parameters
        ----------
        dimension_name : str
        """
        self.metadata_store.delete_dimension(dimension_name)

    def _add_coords(self, item, keys):
        """Add coordinates to spec definitions on an object
        """
        item = deepcopy(item)
        for key in keys:
            spec_list = item[key]
            for spec in spec_list:
                if 'dims' in spec and spec['dims']:
                    spec['coords'] = {
                        dim: self.read_dimension(dim)['elements']
                        for dim in spec['dims']
                    }
        return item
    # endregion

    #
    # DATA
    #

    # region Scenario Variant Data
    def read_scenario_variant_data(self, scenario_name, variant_name, variable, timestep=None):
        """Read scenario data file

        Parameters
        ----------
        scenario_name : str
        variant_name : str
        variable : str
        timestep : int (optional)
            If None, read data for all timesteps

        Returns
        -------
        data : ~smif.data_layer.data_array.DataArray
        """
        variant = self.read_scenario_variant(scenario_name, variant_name)
        return self.data_store.read_scenario_variant_data(
            scenario_name, variant, variable, timestep)

    def write_scenario_variant_data(self, scenario_name, variant_name, data, timestep=None):
        """Write scenario data file

        Parameters
        ----------
        scenario_name : str
        variant_name : str
        data : ~smif.data_layer.data_array.DataArray
        timestep : int (optional)
            If None, write data for all timesteps
        """
        variant = self.read_scenario_variant(scenario_name, variant_name)
        self.data_store.write_scenario_variant_data(scenario_name, variant, data, timestep)
    # endregion

    # region Narrative Data
    def read_narrative_variant_data(self, sos_model_name, narrative_name, variant_name,
                                    parameter_name, timestep=None):
        """Read narrative data file

        Parameters
        ----------
        sos_model_name : str
        narrative_name : str
        variant_name : str
        parameter_name : str
        timestep : int (optional)
            If None, read data for all timesteps

        Returns
        -------
        ~smif.data_layer.data_array.DataArray
        """
        return self.data_store.read_narrative_variant_data(
            sos_model_name, narrative_name, variant_name, parameter_name, timestep)

    def write_narrative_variant_data(self, sos_model_name, narrative_name, variant_name,
                                     data, timestep=None):
        """Read narrative data file

        Parameters
        ----------
        sos_model_name : str
        narrative_name : str
        variant_name : str
        data : ~smif.data_layer.data_array.DataArray
        timestep : int (optional)
            If None, write data for all timesteps
        """
        self.data_store.write_narrative_variant_data(
            sos_model_name, narrative_name, variant_name, data, timestep)

    def read_model_parameter(self, model_name, parameter_name):
        """Read a model parameter

        Parameters
        ----------
        model_name : str
        parameter_name : str

        Returns
        -------
        ~smif.metadata.spec.Spec
        """
        raise NotImplementedError()

    def read_model_parameter_default(self, model_name, parameter_name):
        """Read default data for a sector model parameter

        Parameters
        ----------
        model_name : str
        parameter_name : str

        Returns
        -------
        ~smif.data_layer.data_array.DataArray
        """
        return self.data_store.read_model_parameter_default(model_name, parameter_name)

    def write_model_parameter_default(self, model_name, parameter_name, data):
        """Write default data for a sector model parameter

        Parameters
        ----------
        model_name : str
        parameter_name : str
        data : ~smif.data_layer.data_array.DataArray
        """
        self.data_store.write_model_parameter_default(model_name, parameter_name, data)
    # endregion

    # region Interventions
    def read_interventions(self, model_name):
        """Read interventions data for `model_name`

        Returns
        -------
        dict[str, dict]
            A dict of intervention dictionaries containing intervention
            attributes keyed by intervention name
        """
        return self.data_store.read_interventions(model_name)

    def write_interventions(self, model_name, interventions):
        """Write interventions data for a model

        Parameters
        ----------
        dict[str, dict]
            A dict of intervention dictionaries containing intervention
            attributes keyed by intervention name
        """
        self.data_store.write_interventions(model_name, interventions)

    def read_initial_conditions(self, model_name):
        """Read historical interventions for `model_name`

        Returns
        -------
        list[dict]
            A list of historical interventions, with keys 'name' and 'build_year'
        """
        return self.data_store.read_initial_conditions(model_name)

    def write_initial_conditions(self, model_name, initial_conditions):
        """Write historical interventions for a model

        Parameters
        ----------
        list[dict]
            A list of historical interventions, with keys 'name' and 'build_year'
        """
        self.data_store.write_initial_conditions(model_name, initial_conditions)

    def read_all_initial_conditions(self, model_run_name):
        """A list of all historical interventions

        Returns
        -------
        list[dict]
        """
        historical_interventions = []
        model_run = self.read_model_run(model_run_name)
        sos_model_name = model_run['sos_model']
        sos_model = self.read_sos_model(sos_model_name)
        sector_model_names = sos_model['sector_models']
        for sector_model_name in sector_model_names:
            historical_interventions.extend(
                self.read_initial_conditions(sector_model_name)
            )
        return historical_interventions
    # endregion

    # region State
    def read_state(self, model_run_name, timestep, decision_iteration=None):
        """Read list of (name, build_year) for a given model_run, timestep,
        decision

        Parameters
        ----------
        model_run_name : str
        timestep : int
        decision_iteration : int, optional

        Returns
        -------
        list[dict]
        """
        return self.data_store.read_state(model_run_name, timestep, decision_iteration)

    def write_state(self, state, model_run_name, timestep, decision_iteration=None):
        """State is a list of decisions with name and build_year.

        State is output from the DecisionManager

        Parameters
        ----------
        state : list[dict]
        model_run_name : str
        timestep : int
        decision_iteration : int, optional
        """
        self.data_store.write_state(state, model_run_name, timestep, decision_iteration)
    # endregion

    # region Conversion coefficients
    def read_coefficients(self, source_spec, destination_spec):
        """Reads coefficients from the store

        Coefficients are uniquely identified by their source/destination specs.
        This method and `write_coefficients` implement caching of conversion
        coefficients between dimensions.

        Parameters
        ----------
        source_spec : ~smif.metadata.spec.Spec
        destination_spec : ~smif.metadata.spec.Spec

        Returns
        -------
        numpy.ndarray

        Notes
        -----
        To be called from :class:`~smif.convert.adaptor.Adaptor` implementations.
        """
        return self.data_store.read_coefficients(source_spec, destination_spec)

    def write_coefficients(self, source_spec, destination_spec, data):
        """Writes coefficients to the store

        Coefficients are uniquely identified by their source/destination specs.
        This method and `read_coefficients` implement caching of conversion
        coefficients between dimensions.

        Parameters
        ----------
        source_spec : ~smif.metadata.spec.Spec
        destination_spec : ~smif.metadata.spec.Spec
        data : numpy.ndarray

        Notes
        -----
        To be called from :class:`~smif.convert.adaptor.Adaptor` implementations.
        """
        self.data_store.write_coefficients(source_spec, destination_spec, data)
    # endregion

    # region Results
    def read_results(self, model_run_name, model_name, output_spec, timestep=None,
                     decision_iteration=None):
        """Return results of a `model_name` in `model_run_name` for a given `output_name`

        Parameters
        ----------
        model_run_id : str
        model_name : str
        output_spec : smif.metadata.Spec
        timestep : int, default=None
        decision_iteration : int, default=None

        Returns
        -------
        ~smif.data_layer.data_array.DataArray
        """
        return self.data_store.read_results(
            model_run_name, model_name, output_spec, timestep, decision_iteration)

    def write_results(self, data_array, model_run_name, model_name, timestep=None,
                      decision_iteration=None):
        """Write results of a `model_name` in `model_run_name` for a given `output_name`

        Parameters
        ----------
        data_array : ~smif.data_layer.data_array.DataArray
        model_run_id : str
        model_name : str
        timestep : int, optional
        decision_iteration : int, optional
        """
        self.data_store.write_results(
            data_array, model_run_name, model_name, timestep, decision_iteration)

    def available_results(self, model_run_name):
        """List available results from a model run

        Returns
        -------
        list[tuple]
             Each tuple is (timestep, decision_iteration, model_name, output_name)
        """
        return self.data_store.available_results(model_run_name)

    def prepare_warm_start(self, model_run_name):
        """Copy the results from the previous model_run if available

        The method allows a previous unsuccessful model_run to 'warm start' a new model run
        from a later timestep. Model results are recovered from the timestep that the previous
        model_run was run until, and the new model run runs from the returned timestep

        Parameters
        ----------
        model_run_name : str

        Returns
        -------
        int The timestep to which the data store was recovered

        Notes
        -----
        Called from smif.controller.execute
        """
        available_results = self.data_store.available_results(model_run_name)
        if available_results:
            max_timestep = max(
                timestep for
                timestep, decision_iteration, model_name, output_name in available_results
            )
            # could explicitly clear results for max timestep
        else:
            max_timestep = None
        return max_timestep
    # endregion
