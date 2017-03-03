# -*- coding: utf-8 -*-
import os

from pytest import raises
from smif.data_layer.sos_model_config import SosModelReader
from smif.data_layer.validate import ValidationError


class TestSosModelReader():

    def _get_model_config(self, folder):
        return os.path.join(str(folder), "config", "model.yaml")

    def _get_reader(self, folder):
        return SosModelReader(self._get_model_config(folder))

    def test_read_sos_model(self, setup_project_folder):

        reader = self._get_reader(setup_project_folder)
        reader.load()

        # check timesteps filename
        expected = 'timesteps.yaml'
        assert reader._config['timesteps'] == expected

        # check planning filename list
        expected = ['../data/water_supply/pre-specified.yaml']
        assert reader._config['planning']['pre_specified']['files'] == expected

    def test_model_list(self, setup_project_folder):

        reader = self._get_reader(setup_project_folder)
        reader.load()

        expected = [
            {
                "name": "water_supply",
                "path": "../models/water_supply/__init__.py",
                "classname": "WaterSupplySectorModel",
                "config_dir": "../data/water_supply",
                "initial_conditions": [
                    "../data/water_supply/initial_conditions/assets_1.yaml"
                ],
                "interventions": [
                    "../data/water_supply/interventions/water_asset_abc.yaml"
                ]
            }
        ]

        assert reader.sector_model_data == expected
        assert reader.data["sector_model_config"] == expected

    def test_timesteps(self, setup_project_folder):

        reader = self._get_reader(setup_project_folder)
        reader.load()

        expected = [2010, 2011, 2012]

        assert reader.timesteps == expected
        assert reader.data["timesteps"] == expected

    def test_abs_path_for_timesteps(self, setup_project_folder, setup_abs_path_to_timesteps):
        """Expect absolute paths to work fine
        """
        reader = self._get_reader(setup_project_folder)
        reader.load()

        expected = [2010, 2011, 2012]

        assert reader.timesteps == expected
        assert reader.data["timesteps"] == expected

    def test_timesteps_alternate_file(self, setup_project_folder,
                                      setup_config_file_timesteps_two,
                                      setup_timesteps_file_two):

        reader = self._get_reader(setup_project_folder)
        reader.load()

        expected = [2015, 2020, 2025]
        actual = reader.timesteps
        assert actual == expected

    def test_timesteps_invalid(self, setup_project_folder, setup_timesteps_file_invalid):
        """Expect an error on trying to load an invalid file
        """
        reader = self._get_reader(setup_project_folder)

        with raises(ValidationError):
            reader.load()

    def test_load_scenario_data(self, setup_project_folder, setup_scenario_data):
        """Load a population parameter from scenario config files
        """
        reader = self._get_reader(setup_project_folder)
        reader.load()
        data = reader.data["scenario_data"]
        assert "population" in data
        assert len(data["population"]) == 3
        assert data["population"][0] == {
            'value': 100,
            'units': 'people',
            'region': 'GB',
            'year': 2015
        }

    def test_no_planning(self, setup_project_folder, setup_no_planning):
        """Expect an empty list if planning is not to be used
        """
        reader = self._get_reader(setup_project_folder)
        reader.load()
        data = reader.data["planning"]
        assert len(data) == 0