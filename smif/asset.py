"""Asset is the general term for any component of an infrastructure system

The set of assets defines the state of the infrastructure system.

Notes
-----

This module needs to support:

- initialisation of set of assets from model config (e.g. set of text files;
  database)
    - hold generic list of key/values
- creation of new assets by decision logic (rule-based/optimisation solver)
    - maintain or derive set of possible assets
        - hence distinction between known-ahead values and build-time values.
          At least location and date are specified at build time,
          possibly also cost, capacity as functions of time and location.
- serialisation for passing to models
    - ease of access to full generic data structure
- output list of assets for reporting
    - write out with legible or traceable keys and units for verification
      and understanding

Terminology
~~~~~~~~~~~
asset_type:
    A category of infrastructure intervention (e.g. power station, policy)
    which holds default attribute/value pairs. These asset_types can be
    inherited by asset/intervention definitions to reduce the degree of
    duplicate data entry.
asset:
    An instance of an intervention, which represents a single investment
    decisions which will take place, or has taken place.
    Historical interventions are defined as initial conditions, while
    future interventions are listed as pre-specified planning.
    Both historical and future interventions can make use of asset_types to
    ease data entry.  Assets must have ``location``, ``build_date``
    and ``asset_type`` attributes defined.
intervention:
    A potential asset or investment.
    Interventions are defined in the same way as for assets,
    cannot have a ``build_date`` defined.

"""
import hashlib
import json


class InterventionContainer(object):
    """An container for asset types, interventions and assets.

    An asset's data is set up to be a flexible, plain data structure.

    Parameters
    ----------
    asset_type : str, default=""
        The type of asset, which should be unique across all sectors
    data : dict, default=None
        The dictionary of asset attributes
    sector : str, default=""
        The sector associated with the asset
    """
    def __init__(self, asset_type="", data=None, sector=""):

        assert isinstance(asset_type, str)

        if data is None:
            data = {}

        if asset_type == "" and "asset_type" in data:
            # allow data to set asset_type if none given
            asset_type = data["asset_type"]
        else:
            # otherwise rely on asset_type arg
            data["asset_type"] = asset_type

        self.asset_type = asset_type
        self.data = data

        if sector == "" and "sector" in data:
            # sector is required, may be None
            sector = data["sector"]
        else:
            data["sector"] = sector

        self.sector = sector

        (required, omitted) = self.get_attributes()
        self.validate(required, omitted)

    def get_attributes(self):
        """Override to return two lists, one containing required attributes,
        the other containing omitted attributes

        Returns
        tuple
            Tuple of lists, one contained required attributes, the other which
            must be omitted
        """
        raise NotImplementedError

    def validate(self, required_attributes, omitted_attributes):
        """Ensures location is present and no build date is specified

        """
        keys = self.data.keys()
        for expected in required_attributes:
            if expected not in keys:
                msg = "Validation failed due to missing attribute: '{}' in {}"
                raise ValueError(msg.format(expected, str(self)))

        for omitted in omitted_attributes:
            if omitted in keys:
                msg = "Validation failed due to extra attribute: '{}' in {}"
                raise ValueError(msg.format(omitted, str(self)))

    def sha1sum(self):
        """Compute the SHA1 hash of this asset's data
        """
        str_to_hash = str(self).encode('utf-8')
        return hashlib.sha1(str_to_hash).hexdigest()

    def __repr__(self):
        data_str = Asset.deterministic_dict_to_str(self.data)
        return "Asset(\"{}\", {})".format(self.asset_type, data_str)

    def __str__(self):
        return Asset.deterministic_dict_to_str(self.data)

    @staticmethod
    def deterministic_dict_to_str(data):
        """Return a reproducible string representation of any dict
        """
        return json.dumps(data, sort_keys=True)

    @property
    def sector(self):
        """The name of the sector model this asset is used in.
        """
        return self.data["sector"]

    @sector.setter
    def sector(self, value):
        self.data["sector"] = value


class Intervention(InterventionContainer):
    """An potential investment to send to the logic-layer

    Has a name (or asset_type), other attributes
    (such as capital cost and economic lifetime), and location,
    but no build date.

    """
    def get_attributes(self):
        """Ensures location is present and no build date is specified

        """
        return (['asset_type', 'location'], ['build_date'])

    @property
    def location(self):
        """The location of this asset instance (if specified - asset types
        may not have explicit locations)
        """
        return self.data["location"]

    @location.setter
    def location(self, value):
        self.data["location"] = value


class Asset(Intervention):
    """An instance of an intervention with a build date.

    Used to represent pre-specified planning and existing infrastructure assets
    and interventions

    """
    def get_attributes(self):
        """Ensures location is present and no build date is specified

        """
        return (['asset_type', 'location', 'build_date'], [])

    @property
    def build_date(self):
        """The build date of this asset instance (if specified - asset types
        will not have build dates)
        """
        if "build_date" not in self.data:
            return None
        return self.data["build_date"]

    @build_date.setter
    def build_date(self, value):
        self.data["build_date"] = value


class Register(object):
    """Holds interventions, pre-spec'd planning instructions & existing assets

    Controls asset serialisation to/from numeric representation

    - register each asset type/intervention name
    - translate a set of assets representing an initial system into numeric
      representation

    Internal data structures
    ------------------------

    `asset_types` is a 2D array of integers: each entry is an array
    representing an asset type, each integer indexes attribute_possible_values

    `attribute_keys` is a 1D array of strings

    `attribute_possible_values` is a 2D array of simple values, possibly
    (boolean, integer, float, string, tuple). Each entry is a list of possible
    values for the attribute at that index.

    Invariants
    ----------

    - there must be one name and one list of possible values per attribute
    - each asset type must list one value for each attribute, and that
      value must be a valid index into the possible_values array
    - each possible_values array should be all of a single type

    """
    def __init__(self):
        self.assets = {}
        self._asset_types = []
        self._attribute_keys = []
        self._attribute_possible_values = []

    def register(self, asset):
        """Adds a new asset to the collection
        """
        asset_type = asset.data['asset_type']
        self.assets[asset_type] = asset
        self._asset_types.append(asset.data['asset_type'])

        for key in asset.data.keys():
            self._attribute_keys.append(key)

    def __iter__(self):
        for asset in self.assets:
            yield asset


class AssetRegister(Register):
    """Register each asset type

    """
    def __len__(self):
        return len(self._asset_types)


class InterventionRegister(Register):
    """The collection of Intervention objects

    An InterventionRegister contains an immutable collection of sector specific
    assets and decision points which can be decided on by the Logic Layer

    An Intervention, is basically an investment which has a name (or asset_type),
    other attributes (such as capital cost and economic lifetime), and location,
    but no build date.

    An Intervention is a possible investment, normally an infrastructure asset,
    the timing of which can be decided by the logic-layer.

    * Reads in a collection of interventions defined in each sector model
    * Builds an ordered and immutable collection of interventions
    * Provides interfaces to
        * optimisation/rule-based planning logic
        * SectorModel class model wrappers

    Key functions:
    - outputs a complete list of asset build possibilities (asset type at
      location) which are (potentially) constrained by the pre-specified
      planning instructions and existing infrastructure.
    - translate a binary vector of build instructions
      (e.g. from optimisation routine) into Asset objects with human-readable
      key-value pairs
    - translates an immutable collection of Asset objects into a binary vector
      to pass to the logic-layer.
    """
    def _check_new_asset(self, intervention):
        """Checks that the asset doesn't exist in the register

        """
        hash_list = []
        for existing_asset in self._asset_types:
            hash_list.append(self.numeric_to_asset(existing_asset).sha1sum())
        if intervention.sha1sum() in hash_list:
            return False
        else:
            return True

    def register(self, intervention):
        """Add a new asset to the register
        """
        if self._check_new_asset(intervention):

            for key, value in intervention.data.items():
                self._register_attribute(key, value)

            numeric_asset = [0] * len(self._attribute_keys)

            for key, value in intervention.data.items():
                attr_idx = self.attribute_index(key)
                value_idx = self.attribute_value_index(attr_idx, value)
                numeric_asset[attr_idx] = value_idx

            self._asset_types.append(numeric_asset)

    def _register_attribute(self, key, value):
        """Add a new attribute and its possible value to the register (or, if
        the attribute has been seen before, add a new possible value)
        """
        if key not in self._attribute_keys:
            self._attribute_keys.append(key)
            self._attribute_possible_values.append([None])

        attr_idx = self.attribute_index(key)

        if value not in self._attribute_possible_values[attr_idx]:
            self._attribute_possible_values[attr_idx].append(value)

    def attribute_index(self, key):
        """Get the index of an attribute name
        """
        return list(self._attribute_keys).index(key)

    def attribute_value_index(self, attr_idx, value):
        """Get the index of a possible value for a given attribute index
        """
        return self._attribute_possible_values[attr_idx].index(value)

    def numeric_to_asset(self, numeric_asset):
        """Convert the numeric representation of an asset back to Asset (with
        legible key/value data)

        Given a (very minimal) possible state of a register:

        >>> register = AssetRegister()
        >>> register._asset_types = [[1,1,1]]
        >>> register._attribute_keys = ["asset_type", "capacity", "sector"]
        >>> register._attribute_possible_values = [
        ...     [None, "water_treatment_plant"],
        ...     [None, {"value": 5, "units": "ML/day"}],
        ...     [None, "water_supply"]
        ... ]

        Calling this function would piece together the asset:

        >>> asset = register.numeric_to_asset([1,1,1])
        >>> print(asset)
        Asset("water_treatment_plant", {"asset_type": "water_treatment_plant",
        "capacity": {"units": "ML/day", "value": 5}, "sector": "water_supply"})

        """
        data = {}
        for attr_idx, value_idx in enumerate(numeric_asset):
            key = list(self._attribute_keys)[attr_idx]
            value = self._attribute_possible_values[attr_idx][value_idx]

            data[key] = value

        intervention = Intervention(data=data)

        return intervention

    def __iter__(self):
        """Iterate over the list of Asset types held in the register
        """
        for asset in self._asset_types:
            yield self.numeric_to_asset(asset)

    def __len__(self):
        """Returns the number of asset types stored in the register
        """
        return len(self._asset_types)
