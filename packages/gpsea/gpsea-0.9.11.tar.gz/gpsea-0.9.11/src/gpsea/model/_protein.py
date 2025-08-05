import abc
import enum
import io
import json
import typing
import warnings

import pandas as pd

from gpsea.util import open_text_io_handle_for_reading

from .genome import Region


class FeatureInfo:
    """
    `FeatureInfo` represents a protein feature
    (e.g. a repeated sequence given the name "ANK 1" in protein "Ankyrin repeat domain-containing protein 11")
    """

    def __init__(self, name: str, region: Region):
        assert isinstance(name, str)
        self._name = name
        assert isinstance(region, Region)
        self._region = region

    @property
    def name(self) -> str:
        """
        Returns:
            string: the name of the protein feature
        """
        return self._name

    @property
    def start(self) -> int:
        """
        Returns:
            integer: A 0-based (excluded) start coordinate of the protein feature.
        """
        return self._region.start

    @property
    def end(self) -> int:
        """
        Returns:
            integer: A 0-based (included) end coordinate of the protein feature.
        """
        return self._region.end

    @property
    def region(self) -> Region:
        """
        Returns:
            Region: a protein region spanned by the feature.
        """
        return self._region

    def overlaps_with(self, region: Region) -> bool:
        """
        Covenience function to check whether a region overlaps with a protein feature.
        """
        return self._region.overlaps_with(region)

    def __len__(self):
        return len(self._region)

    def __eq__(self, other) -> bool:
        return isinstance(other, FeatureInfo) and self.name == other.name and self.region == other.region

    def __hash__(self):
        return hash((self._name, self._region))

    def __str__(self) -> str:
        return f"FeatureInfo(name={self.name}, start={self.start}, end={self.end})"

    def __repr__(self) -> str:
        return str(self)


def _deprecation_warning():
    warnings.warn(
        "`FeatureType` was deprecated and will be removed prior `v1.0.0`. Use a `str` instead!",
        DeprecationWarning,
    )


class FeatureType(enum.Enum):
    """
    An enum representing the protein feature types supported in GPSEA.

    Use :func:`~gpsea.model.FeatureType.from_string` to parse a feature from Uniprot:

    >>> from gpsea.model import FeatureType
    >>> val = "Dna Binding"
    >>> feature_type = FeatureType.from_string(val)
    >>> feature_type.name
    'DNA_BINDING'
    """

    REPEAT = enum.auto()
    """
    A repeated sequence motif or repeated domain within the protein.
    """

    MOTIF = enum.auto()
    """
    A short (usually not more than 20 amino acids) conserved sequence motif of biological significance.
    """

    DOMAIN = enum.auto()
    """
    A specific combination of secondary structures organized into a characteristic three-dimensional structure or fold.
    """

    COILED_COIL = enum.auto()
    """
    a structural motif in proteins, characterized by two or more α-helices wrapped around each other in a supercoil.
    This structure is often involved in protein-protein interactions
    """

    COMPOSITIONAL_BIAS = enum.auto()
    """
    Compositional bias refers to a  region in a protein where certain amino acids are overrepresented compared to
    the rest of the protein or compared to typical protein composition. These regions tend to have a non-random
    distribution of amino acids, often leading to specific structural or functional properties.
    """

    REGION = enum.auto()
    """
    A region of interest that cannot be described in other subsections.
    """

    ZINC_FINGER = enum.auto()
    """
    A zinc finger is a small, functional, independently folded domain that coordinates one or more zinc ions to stabilize its structure through cysteine and/or histidine residues.
    """

    TOPOLOGICAL_DOMAIN = enum.auto()
    """
    non-membrane region of a membrane-spanning protein
    """

    TRANSMEMBRANE = enum.auto()
    """
    Section of a protein that goes through the membrane of the cell or an organelle
    """

    DNA_BINDING = enum.auto()
    """
    A region with a known DNA binding activity.
    """

    def __init__(self, _value):
        _deprecation_warning()

    @staticmethod
    def from_string(category: str) -> "FeatureType":
        cat_lower = category.lower()
        if cat_lower == "repeat":
            return FeatureType.REGION
        elif cat_lower == "motif":
            return FeatureType.MOTIF
        elif cat_lower == "domain":
            return FeatureType.DOMAIN
        elif cat_lower == "region":
            return FeatureType.REGION
        elif cat_lower == "coiled coil":
            return FeatureType.REGION
        elif cat_lower == "compositional bias":
            return FeatureType.COMPOSITIONAL_BIAS
        elif cat_lower == "zinc finger":
            return FeatureType.ZINC_FINGER
        elif cat_lower == "topological domain":
            return FeatureType.TOPOLOGICAL_DOMAIN
        elif cat_lower == "transmembrane":
            return FeatureType.TRANSMEMBRANE
        elif cat_lower == "dna binding":
            return FeatureType.DNA_BINDING
        else:
            raise ValueError(f'Unrecognized protein feature type: "{category}"')

    @staticmethod
    def deprecation_warning():
        _deprecation_warning()


class ProteinFeature(metaclass=abc.ABCMeta):
    @staticmethod
    def create(
        info: FeatureInfo,
        feature_type: str,
    ) -> "ProteinFeature":
        return SimpleProteinFeature(info, feature_type)

    @property
    @abc.abstractmethod
    def info(self) -> FeatureInfo:
        pass

    @property
    @abc.abstractmethod
    def feature_type(self) -> str:
        pass

    def to_string(self) -> str:
        return f"{self.feature_type}-{self.info.name}-{self.info.region}"


class SimpleProteinFeature(ProteinFeature):
    """
    An implementation of a `ProteinFeature`.
    """

    # Not part of the public API.

    def __init__(
        self,
        info: FeatureInfo,
        feature_type: str,
    ):
        """Constructs all necessary attributes for a SimpleProteinFeature

        Args:
            info (FeatureInfo): A FeatureInfo object, describing name and location of the feature
            feature_type (FeatureType): A FeatureType object, limited to specific feature types
        """
        assert isinstance(info, FeatureInfo)
        self._info = info
        assert isinstance(feature_type, str)
        self._type = feature_type

    @property
    def info(self) -> FeatureInfo:
        """
        Returns:
            FeatureInfo: A FeatureInfo object, describing name and location of the feature
        """
        return self._info

    @property
    def feature_type(self) -> str:
        """
        Get a `str` with the feature type (e.g. `Region`, `Zinc finger`, ...).
        """
        return self._type

    def __str__(self) -> str:
        return f"SimpleProteinFeature(type={self._type}, info={self._info})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, SimpleProteinFeature) and self._type == other._type and self._info == other._info

    def __hash__(self) -> int:
        return hash((self._type, self._info))


class ProteinMetadata:
    """
    An info regarding a protein sequence, including an ID, a label,
    and location of protein features, such as motifs, domains, or other regions.

    The information is usually retrieved from a resource such as :class:`~gpsea.preprocessing.UniprotProteinMetadataService`,
    but it can also be created manually using :meth:`~gpsea.model.ProteinMetadata.from_feature_frame` function.

    Example
    -------

    Let's create a protein info with a domain and a region. We must provide protein accession ID,
    a label, a data frame with protein features, and the number of aminoacids of the protein sequence:

    >>> protein_id = 'NP_000129.3'
    >>> label = 'fibrillin-1 isoform a preproprotein'
    >>> protein_length = 1000

    Now let's prepare a data frame with the protein features. We will prepare a domain and a region:

    >>> import pandas as pd
    >>> features = [
    ...     {
    ...         "region": "Suppresor domain",
    ...         "category": "domain",
    ...         "start": 1,
    ...         "end": 223,
    ...     },
    ...     {
    ...         "region": "IP3 binding",
    ...         "category": "region",
    ...         "start": 224,
    ...         "end": 578,
    ...     },
    ... ]
    >>> df = pd.DataFrame(features)

    last, we can put the protein info together:

    >>> from gpsea.model import ProteinMetadata
    >>> protein_meta = ProteinMetadata.from_feature_frame(
    ...     protein_id=protein_id,
    ...     label=label,
    ...     features=df,
    ...     protein_length=protein_length,
    ... )

    and get the expected protein info:

    >>> protein_meta.protein_id
    'NP_000129.3'
    >>> protein_meta.label
    'fibrillin-1 isoform a preproprotein'
    >>> len(protein_meta.protein_features)
    2
    """

    @staticmethod
    def from_feature_frame(
        protein_id: str,
        label: str,
        features: pd.DataFrame,
        protein_length: int,
    ) -> "ProteinMetadata":
        """
        Create `ProteinMetadata` from a user-supplied pandas DataFrame.
        We expect to obtain the gene symbol, protein identifier, and regions

        The DataFrame should include the following columns:

        +------------------+----------+----------------+
        | region           | category | start  | end   |
        +------------------+----------+--------+-------+
        | Suppresor domain | domain   | 1      | 223   |
        +------------------+----------+--------+-------+
        | IP3 binding      | region   | 224    | 578   |
        +------------------+----------+--------+-------+

        The `region` column includes the protein feature name.
        The category is a `str` representing region's feature type. Use `'region'` if no better type fits.
        Last, `start` and `end` denote 1-based start and end coordinates
        of the aminoacid sequence region described by the feature.
        For instance, `[1, 10]` for the first ten aminoacids of the protein.

        :param protein_id: the accession id of the protein, e.g. `'NP_000129.3'`.
        :param label: human-readable label, e.g. `'fibrillin-1 isoform a preproprotein'`.
        :param features: a dataframe with of the protein features.
        :param protein_length: a positive `int` representing the number of aminoacids included in the protein sequence.
        :raises ValueError: if case of issues during parsing the provided data.
        """
        expected_headers = ("region", "start", "end", "category")
        if any(col_name not in features.columns for col_name in expected_headers):
            missing_cols = ", ".join(set(expected_headers).difference(features.columns))
            raise ValueError(
                f"The column(s) {{{missing_cols}}} are missing from the `features` DataFrame: {tuple(features.columns)}"
            )
        region_list = list()
        for _, row in features.iterrows():
            region_name = row["region"]
            region_start = row["start"] - 1  # convert to 0-based coordinates
            region_end = row["end"]
            feature_type = row["category"]
            finfo = FeatureInfo(name=region_name, region=Region(start=region_start, end=region_end))
            pfeature = ProteinFeature.create(info=finfo, feature_type=feature_type)
            region_list.append(pfeature)

        return ProteinMetadata(
            protein_id=protein_id,
            label=label,
            protein_features=region_list,
            protein_length=protein_length,
        )

    @staticmethod
    def from_uniprot_json(
        protein_id: str,
        label: str,
        uniprot_json: typing.Union[io.IOBase, str],
        protein_length: int,
    ) -> "ProteinMetadata":
        """
        Create `ProteinMetadata` from a json file that has been downloaded from UniProt.

        Go to the UniProt page for the protein of interest, then go to the section "Family & Domains", and the
        subsection "Features". Click on the *Download* symbol. You will be presented with a JSON file for download.
        From this, we extract information about the gene symbol, protein identifier, and regions.
        This method is intended to be a backup if the API call to UniProt fails; the same information should be
        retrieved.
        See the test file "test_uniprot_json.py" for details about the JSON parsing etc.

        :param protein_id: the accession id of the protein, e.g. `'NP_000129.3'`.
        :param label: human-readable label, e.g. `'fibrillin-1 isoform a preproprotein'`.
        :param uniprot_json: a `str` with the path or an IO object with the Uniprot JSON data.
        :param protein_length: a positive `int` representing the number of aminoacids included in the protein sequence.
        :raises ValueError: if case of issues during parsing the provided data.
        """
        with open_text_io_handle_for_reading(uniprot_json) as fh:
            data = json.load(fh)

        regions = list()
        for feature in data["features"]:
            region_name = feature["description"]
            locus = feature["location"]
            region_start = int(locus["start"]["value"]) - 1  # convert to 0-based coordinates
            region_end = int(locus["end"]["value"])
            feature_type = feature["type"]
            finfo = FeatureInfo(name=region_name, region=Region(start=region_start, end=region_end))
            pfeature = ProteinFeature.create(info=finfo, feature_type=feature_type)
            regions.append(pfeature)

        return ProteinMetadata(
            protein_id=protein_id,
            label=label,
            protein_features=regions,
            protein_length=protein_length,
        )

    def __init__(
        self,
        protein_id: str,
        label: str,
        protein_features: typing.Iterable[ProteinFeature],
        protein_length: int,
    ):
        assert isinstance(protein_id, str)
        self._id = protein_id
        assert isinstance(label, str)
        self._label = label

        assert all(isinstance(x, ProteinFeature) for x in protein_features)
        self._features = tuple(protein_features)
        assert isinstance(protein_length, int) and protein_length > 0
        self._protein_length = protein_length

    @property
    def protein_id(self) -> str:
        """
        Get the protein's accession ID, e.g. `NP_000129.3`.
        """
        return self._id

    @property
    def label(self) -> str:
        """
        Get the protein label, e.g. `fibrillin-1 isoform a preproprotein`.
        """
        return self._label

    @property
    def protein_features(self) -> typing.Sequence[ProteinFeature]:
        """
        Get a sequence of protein features.
        """
        return self._features

    @property
    def protein_length(self) -> int:
        """
        Get the number of aminoacids of the protein sequence.
        """
        return self._protein_length

    def domains(self) -> typing.Iterable[ProteinFeature]:
        """
        Returns:
            Iterable[ProteinFeature]: A subgroup of the protein features that correspond to protein domains.
        """
        return filter(lambda f: f.feature_type.upper() == "DOMAIN", self.protein_features)

    def repeats(self) -> typing.Iterable[ProteinFeature]:
        """
        Returns:
            Iterable[ProteinFeature]: A subgroup of the protein features that correspond to repeat regions.
        """
        return filter(lambda f: f.feature_type.upper() == "REPEAT", self.protein_features)

    def regions(self) -> typing.Iterable[ProteinFeature]:
        """
        Returns:
            Iterable[ProteinFeature]: A subgroup of the protein features that correspond to generic regions.
        """
        return filter(lambda f: f.feature_type.upper() == "REGION", self.protein_features)

    def motifs(self) -> typing.Iterable[ProteinFeature]:
        """
        Returns:
            Iterable[ProteinFeature]: A subgroup of the protein features that correspond to motifs.
        """
        return filter(lambda f: f.feature_type.upper() == "MOTIF", self.protein_features)

    def get_features_variant_overlaps(
        self,
        region: Region,
    ) -> typing.Collection[ProteinFeature]:
        """
        Get a collection of protein features that overlap with the `region`.
        Args:
            region: the query region.

        Returns:
            Collection[ProteinFeature]: a collection of overlapping protein features.
        """
        return tuple(feature for feature in self._features if feature.info.region.overlaps_with(region))

    def __str__(self) -> str:
        return f"ProteinMetadata(id={self.protein_id}, label={self.label}, features={str(self.protein_features)})"

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ProteinMetadata)
            and self.label == other.label
            and self.protein_features == other.protein_features
            and self.protein_id == other.protein_id
        )

    def __hash__(self) -> int:
        return hash((self.protein_id, self.label, self._features))

    def __repr__(self) -> str:
        return str(self)
