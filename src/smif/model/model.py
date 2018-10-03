"""Model abstract class
"""
from abc import ABCMeta, abstractmethod
from enum import Enum
from logging import getLogger

from smif.metadata import RelativeTimestep, Spec
from smif.model.dependency import Dependency


class ModelOperation(Enum):
    """ Enumerate that describes the possible operations on Models
    """
    BEFORE_MODEL_RUN = 'before_model_run'
    SIMULATE = 'simulate'


class Model(metaclass=ABCMeta):
    """Abstract class represents the interface used to implement the composite
    `SosModel` and leaf classes `SectorModel` and `Scenario`.

    Arguments
    ---------
    name : str
    """

    def __init__(self, name):
        self.name = name
        self.description = ''
        self._inputs = {}
        self._parameters = {}
        self._outputs = {}
        self._deps = {}

        self.logger = getLogger(__name__)

    @property
    def inputs(self):
        """All model inputs defined at this layer

        Returns
        -------
        dict of {input_name: smif.metadata.Spec}
        """
        return self._inputs

    @property
    def parameters(self):
        """Model parameters

        Returns
        -------
        dict of {parameter_name: smif.metadata.Spec}
        """
        return self._parameters

    @property
    def outputs(self):
        """All model outputs defined at this layer

        Returns
        -------
        dict of {output_name: smif.metadata.Spec}
        """
        return self._outputs

    @property
    def deps(self):
        """All model dependencies defined at this layer

        Returns
        -------
        dict of {input_name: smif.model.Dependency}
        """
        return self._deps

    @property
    def free_inputs(self):
        """Returns the free inputs not linked to a dependency at this layer

        Free inputs are passed up to higher layers for deferred linkages to
        dependencies.

        Returns
        -------
        smif.metadata.MetadataSet
        """
        all_input_names = set(self.inputs.keys())
        dep_input_names = set(dep.sink.name for dep in self.deps.values())
        free_input_names = all_input_names - dep_input_names

        return {name: self.inputs[name] for name in free_input_names}

    def add_input(self, spec):
        """Add an input

        Arguments
        ---------
        spec: smif.metadata.Spec
        """
        self.inputs[spec.name] = spec

    def add_parameter(self, spec):
        """Add a parameter

        Arguments
        ---------
        spec: smif.metadata.Spec
        """
        self.parameters[spec.name] = spec

    def add_output(self, spec):
        """Add an output

        Arguments
        ---------
        spec: smif.metadata.Spec
        """
        self.outputs[spec.name] = spec

    def add_dependency(self, source_model, source_output_name, sink_input_name,
                       timestep=RelativeTimestep.CURRENT):
        """Adds a dependency to the current `Model` object

        Arguments
        ---------
        source_model : `smif.composite.Model`
            A reference to the source `~smif.composite.Model` object
        source_output_name : string
            The name of the model_output defined in the `source_model`
        sink_name : string
            The name of a model_input defined in this object
        timestep : smif.metadata.RelativeTimestep, optional
            The relative timestep of the dependency, defaults to CURRENT, may be PREVIOUS.
        """
        if source_output_name not in source_model.outputs:
            msg = "Output '{}' is not defined in '{}' model"
            raise ValueError(msg.format(source_output_name, source_model.name))

        if sink_input_name not in self.inputs:
            msg = "Input '{}' is not defined in '{}' model"
            raise ValueError(msg.format(sink_input_name, self.name))

        if not self._allow_adding_dependency(source_model, sink_input_name, timestep):
            msg = "Inputs: '%s'. Free inputs: '%s'."
            self.logger.debug(msg, self.inputs, self.free_inputs)
            msg = "Input '{}' dependency already defined as {} in {}"
            raise ValueError(
                msg.format(sink_input_name, self.deps[sink_input_name], self.name))

        source_spec = source_model.outputs[source_output_name]
        sink_spec = self.inputs[sink_input_name]
        self.deps[sink_input_name] = Dependency(
            source_model, source_spec, self, sink_spec, timestep=timestep)

        msg = "Added dependency from '%s:%s' to '%s:%s'"
        self.logger.debug(
            msg, source_model.name, source_output_name, self.name, sink_input_name)

    def _allow_adding_dependency(self, source_model, sink_input_name, timestep):
        if sink_input_name not in self.free_inputs:
            other_dep = self.deps[sink_input_name]
            other_model = other_dep.source_model
            other_timestep = other_dep.timestep

            other_is_previous = other_timestep == RelativeTimestep.PREVIOUS
            other_is_scenario = isinstance(other_model, ScenarioModel)

            new_is_previous = timestep == RelativeTimestep.PREVIOUS
            new_is_scenario = isinstance(source_model, ScenarioModel)

            allowable = (new_is_previous and other_is_scenario) or \
                (other_is_previous and new_is_scenario)
        else:
            allowable = True

        return allowable

    @abstractmethod
    def simulate(self, data):
        """Override to implement the generation of model results

        Generate ``results`` for ``timestep`` using ``data``

        Arguments
        ---------
        data: smif.data_layer.DataHandle
            Access state, parameter values, dependency inputs.
        """


class CompositeModel(Model, metaclass=ABCMeta):
    """Override to implement models which contain models.

    Inherited by `smif.model.sos_model.SosModel` and
    `smif.model.model_set.ModelSet`
    """
    def __init__(self, name):
        super().__init__(name)
        self.models = {}

    def add_dependency(self, source_model, source_output_name, sink_input_name):
        raise NotImplementedError("Dependencies cannot be added to a CompositeModel")

    @property
    def free_inputs(self):
        """Returns the free inputs not linked to a dependency at this layer

        For this composite :class:`~smif.model.CompositeModel` this includes
        the free_inputs from all contained smif.model.Model objects

        Free inputs are passed up to higher layers for deferred linkages to
        dependencies.

        Returns
        -------
        dict of {input_name: smif.metadata.Spec}
        """
        # free inputs of current layer
        free_inputs = super().free_inputs

        # free inputs of all contained models
        for model in self.models.values():
            for input_name, input_spec in model.free_inputs.items():
                free_inputs[(model.name, input_name)] = input_spec

        return free_inputs

    @property
    def outputs(self):
        outputs = super().outputs
        for model in self.models.values():
            for output_name, output_spec in model.outputs.items():
                outputs[(model.name, output_name)] = output_spec

        return outputs

    @abstractmethod
    def simulate(self, data):
        """Override to implement the generation of model results within the composite

        Arguments
        ---------
        data: smif.data_layer.DataHandle
            Access state, parameter values, dependency inputs.
        """


class ScenarioModel(Model):
    """Represents exogenous scenario data

    Arguments
    ---------
    name : str
        The name of this scenario (scenario set/abstract
        scenario/scenario group) - like sector model name

    Attributes
    ----------
    name : str
        Name of this scenario
    scenario : str
        Instance of scenario (concrete instance)
    """
    def __init__(self, name):
        super().__init__(name)
        self.scenario = None

    @classmethod
    def from_dict(cls, data):
        """Create ScenarioModel from dict serialisation
        """
        scenario = cls(data['name'])
        scenario.scenario = data['scenario']
        if 'description' in data:
            scenario.description = data['description']
        for output in data['outputs']:
            spec = Spec.from_dict(output)
            scenario.add_output(spec)

        return scenario

    def as_dict(self):
        """Serialise ScenarioModel to dict
        """
        config = {
            'name': self.name,
            'description': self.description,
            'scenario': self.scenario,
            'outputs': [
                output.as_dict()
                for output in self.outputs.values()
            ]
        }
        return config

    def simulate(self, data):
        """No-op, as the data is assumed to be already available in the store
        """
        return data
