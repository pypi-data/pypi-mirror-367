import typing

import hpotk

from gpsea.model import VariantClass, VariantEffect, ProteinMetadata, FeatureType
from gpsea.model.genome import Region
from ._api import VariantPredicate, AllVariantPredicate, AnyVariantPredicate
from ._predicates import (
    AlwaysTrueVariantPredicate,
    ChangeLengthPredicate,
    IsLargeImpreciseStructuralVariantPredicate,
    ProteinFeaturePredicate,
    ProteinFeatureTypePredicate,
    ProteinRegionPredicate,
    RefAlleleLengthPredicate,
    StructuralTypePredicate,
    VariantClassPredicate,
    VariantEffectPredicate,
    VariantExonPredicate,
    VariantGenePredicate,
    VariantKeyPredicate,
    VariantTranscriptPredicate,
)


# We do not need more than just one instance of these predicates.
IS_TRANSLOCATION = VariantClassPredicate(VariantClass.TRANSLOCATION)
IS_LARGE_IMPRECISE_SV = IsLargeImpreciseStructuralVariantPredicate()


def true() -> VariantPredicate:
    """
    The most inclusive variant predicate - returns `True` for any variant whatsoever.
    """
    return AlwaysTrueVariantPredicate.get_instance()


def allof(predicates: typing.Iterable[VariantPredicate]) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` that returns `True` if ALL `predicates` evaluate to `True`.

    This is useful for building compound predicates programmatically.

    **Example**

    Build a predicate to test if variant has a functional annotation to genes *SURF1* and *SURF2*:

    >>> from gpsea.analysis.predicate import allof, gene

    >>> genes = ('SURF1', 'SURF2',)
    >>> predicate = allof(gene(g) for g in genes)
    >>> predicate.description
    '(affects SURF1 AND affects SURF2)'

    Args:
        predicates: an iterable of predicates to test
    """
    predicates = tuple(predicates)
    if len(predicates) == 1:
        # No need to wrap one predicate into a logical predicate.
        return predicates[0]
    else:
        return AllVariantPredicate(*predicates)


def anyof(predicates: typing.Iterable[VariantPredicate]) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` that returns `True` if ANY of the `predicates` evaluates to `True`.

    This can be useful for building compound predicates programmatically.

    **Example**

    Build a predicate to test if variant leads to a missense
    or nonsense change on a fictional transcript `NM_123456.7`:

    >>> from gpsea.model import VariantEffect
    >>> from gpsea.analysis.predicate import anyof, variant_effect

    >>> tx_id = 'NM_123456.7'
    >>> effects = (VariantEffect.MISSENSE_VARIANT, VariantEffect.STOP_GAINED,)
    >>> predicate = anyof(variant_effect(e, tx_id) for e in effects)
    >>> predicate.description
    '(MISSENSE_VARIANT on NM_123456.7 OR STOP_GAINED on NM_123456.7)'

    Args:
        predicates: an iterable of predicates to test
    """
    predicates = tuple(predicates)
    if len(predicates) == 1:
        # No need to wrap one predicate into a logical predicate.
        return predicates[0]
    else:
        return AnyVariantPredicate(*predicates)


def variant_effect(
    effect: VariantEffect,
    tx_id: str,
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` to test if the functional annotation predicts the variant to lead to
    a certain variant effect.

    **Example**

    Make a predicate for testing if the variant leads to a missense change on transcript `NM_123.4`:

    >>> from gpsea.model import VariantEffect
    >>> from gpsea.analysis.predicate import variant_effect
    >>> predicate = variant_effect(VariantEffect.MISSENSE_VARIANT, tx_id='NM_123.4')
    >>> predicate.description
    'MISSENSE_VARIANT on NM_123.4'

    Args:
        effect: the target :class:`~gpsea.model.VariantEffect`
        tx_id: a `str` with the accession ID of the target transcript (e.g. `NM_123.4`)
    """
    return VariantEffectPredicate(effect, tx_id)


def variant_key(key: str) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` that tests if the variant matches the provided `key`.

    Args:
        key: a `str` with the variant key (e.g. `X_12345_12345_C_G` or `22_10001_20000_INV`)
    """
    return VariantKeyPredicate(key)


def gene(symbol: str) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` that tests if the variant affects a given gene.

    We recommend to consult the `HUGO Gene Name Nomenclature Committee <https://www.genenames.org/>`_
    website to obtain the approved symbol for the gene of interest.

    Args:
        symbol: a `str` with the approved gene symbol (e.g. ``FBN1``).
    """
    return VariantGenePredicate(symbol)


def transcript(tx_id: str) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` that tests if the variant affects a transcript.

    Args:
        tx_id: a `str` with the accession ID of the target transcript (e.g. `NM_123.4`)
    """
    return VariantTranscriptPredicate(tx_id)


def exon(
    exon: int,
    tx_id: str,
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` that tests if the variant overlaps with an exon of a specific transcript.

    .. warning::

        We use 1-based numbering to number the exons,
        not the usual 0-based numbering of the computer science.
        Therefore, the first exon of the transcript
        has ``exon_number==1``, the second exon is ``2``, and so on ...

    .. warning::

        We do not check if the `exon_number` spans
        beyond the number of exons of the given `transcript_id`!
        Therefore, ``exon_number==10,000`` will effectively return `False`
        for *all* variants!!! 😱
        Well, at least the genome variants of the *Homo sapiens sapiens* taxon...

    Args:
        exon: a positive `int` with the index of the target exon
            (e.g. `1` for the 1st exon, `2` for the 2nd, ...)
        tx_id: a `str` with the accession ID of the target transcript (e.g. `NM_123.4`)
    """
    return VariantExonPredicate(exon, tx_id)


def protein_region(
    region: typing.Union[typing.Tuple[int, int], Region],
    tx_id: str,
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` that tests if the variant
    overlaps with a region on a protein of a specific transcript.


    Example
    -------

    Create a predicate to test if the variant overlaps with the 5th aminoacid
    of the protein encoded by a fictional transcript `NM_1234.5`:

    >>> from gpsea.analysis.predicate import protein_region
    >>> overlaps_with_fifth_aa = protein_region(region=(5, 5), tx_id="NM_1234.5")
    >>> overlaps_with_fifth_aa.description
    'overlaps with [5,5] region of the protein encoded by NM_1234.5'

    Create a predicate to test if the variant overlaps with the first 20 aminoacid residues of the same transcript:

    >>> overlaps_with_first_20 = protein_region(region=(1, 20), tx_id="NM_1234.5")
    >>> overlaps_with_first_20.description
    'overlaps with [1,20] region of the protein encoded by NM_1234.5'

    Args:
        region: a :class:`~gpsea.model.genome.Region` that gives the start and end coordinate
            of the region of interest on a protein strand or a tuple with 1-based coordinates.
    """
    if isinstance(region, Region):
        pass
    elif isinstance(region, tuple) and len(region) == 2 and all(isinstance(r, int) and r > 0 for r in region):
        start = region[0] - 1  # Convert to 0-based
        end = region[1]
        region = Region(start=start, end=end)
    else:
        raise ValueError(f"region must be a `Region` or a tuple with two positive `int`s, but got {region}")

    return ProteinRegionPredicate(region, tx_id)


def is_large_imprecise_sv() -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` for testing if the variant is a large structural variant (SV)
    without exact breakpoint coordinates.
    """
    return IS_LARGE_IMPRECISE_SV


def is_structural_variant(
    threshold: int = 50,
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` for testing if the variant is a structural variant (SV).

    SVs are usually defined as variant affecting more than a certain number of base pairs.
    The thresholds vary in the literature, but here we use 50bp as a default.

    Any variant that affects at least `threshold` base pairs is considered an SV.
    Large SVs with unknown breakpoint coordinates or translocations
    (:class:`~gpsea.model.VariantClass.TRANSLOCATION`) are always considered as an SV.

    Args:
        threshold: a non-negative `int` with the number of base pairs that must be affected
    """
    assert threshold >= 0, "`threshold` must be non-negative!"
    return change_length("<=", -threshold) | change_length(">=", threshold) | is_large_imprecise_sv() | IS_TRANSLOCATION


def structural_type(
    curie: typing.Union[str, hpotk.TermId],
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` for testing if the variant has a certain structural type.

    We recommend using a descendant of `structural_variant`
    (`SO:0001537 <https://purl.obolibrary.org/obo/SO_0001537>`_)
    as the structural type.

    **Example**

    Make a predicate for testing if the variant is a chromosomal deletion (`SO:1000029`):

    >>> from gpsea.analysis.predicate import structural_type
    >>> predicate = structural_type('SO:1000029')
    >>> predicate.description
    'structural type is SO:1000029'

    Args:
        curie: compact uniform resource identifier (CURIE) with the structural type to test.
    """
    return StructuralTypePredicate.from_curie(curie)


def variant_class(
    variant_class: VariantClass,
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` for testing if the variant
    is of a certain :class:`~gpsea.model.VariantClass`.

    **Example**

    Make a predicate to test if the variant is a deletion:

    >>> from gpsea.model import VariantClass
    >>> from gpsea.analysis.predicate import variant_class
    >>> predicate = variant_class(VariantClass.DEL)
    >>> predicate.description
    'variant class is DEL'

    Args:
        variant_class: the variant class to test.
    """
    return VariantClassPredicate(
        query=variant_class,
    )


def ref_length(
    operator: typing.Literal["<", "<=", "==", "!=", ">=", ">"],
    length: int,
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` for testing if the reference (REF) allele
    of variant is above, below, or (not) equal to certain `length`.

    .. seealso::

        See :ref:`length-of-the-reference-allele` for more info.

    **Example**

    Prepare a predicate that tests that the REF allele includes more than 5 base pairs:

    >>> from gpsea.analysis.predicate import ref_length
    >>> predicate = ref_length('>', 5)
    >>> predicate.description
    'reference allele length > 5'

    Args:
        operator: a `str` with the desired test. Must be one of ``{ '<', '<=', '==', '!=', '>=', '>' }``.
        length: a non-negative `int` with the length threshold.
    """
    return RefAlleleLengthPredicate(operator, length)


def change_length(
    operator: typing.Literal["<", "<=", "==", "!=", ">=", ">"],
    threshold: int,
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` for testing if the variant's change length
    is above, below, or (not) equal to certain `threshold`.

    .. seealso::

        See :ref:`change-length-of-an-allele` for more info.

    **Example**

    Make a predicate for testing if the change length is less than or equal to `-10`,
    e.g. to test if a variant is a *deletion* leading to removal of at least 10 base pairs:

    >>> from gpsea.analysis.predicate import change_length
    >>> predicate = change_length('<=', -10)
    >>> predicate.description
    'change length <= -10'

    Args:
        operator: a `str` with the desired test. Must be one of ``{ '<', '<=', '==', '!=', '>=', '>' }``.
        threshold: an `int` with the threshold. Can be negative, zero, or positive.
    """
    return ChangeLengthPredicate(operator, threshold)


def is_structural_deletion(
    threshold: int = -50,
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` for testing if the variant
    is a `chromosomal deletion <https://purl.obolibrary.org/obo/SO_1000029>`_ or a structural variant deletion
    that leads to removal of at least *n* base pairs (50bp by default).

    .. note::

        The predicate uses :meth:`~gpsea.model.VariantCoordinates.change_length`
        to determine if the length of the variant is above or below `threshold`.

        **IMPORTANT**: the change lengths of deletions are *negative*, since the alternate allele
        is shorter than the reference allele. See :ref:`change-length-of-an-allele` for more info.

    **Example**

    Prepare a predicate for testing if the variant is a chromosomal deletion that removes at least 20 base pairs:

    >>> from gpsea.analysis.predicate import is_structural_deletion
    >>> predicate = is_structural_deletion(-20)
    >>> predicate.description
    '(structural type is SO:1000029 OR (variant class is DEL AND change length <= -20))'

    Args:
        threshold: an `int` with the change length threshold to determine if a variant is "structural"
            (-50 bp by default).
    """
    chromosomal_deletion = "SO:1000029"
    return structural_type(chromosomal_deletion) | (variant_class(VariantClass.DEL) & change_length("<=", threshold))


def protein_feature_type(
    feature_type: typing.Union[FeatureType, str],
    protein_metadata: ProteinMetadata,
) -> VariantPredicate:
    """
    Prepare a :class:`~gpsea.analysis.predicate.VariantPredicate`
    to test if the variant affects a `feature_type` of a protein.

    Args:
        feature_type: the target protein :class:`~gpsea.model.FeatureType`
            (e.g. :class:`~gpsea.model.FeatureType.DOMAIN`).
        protein_metadata: the information about the protein.
    """
    if isinstance(feature_type, FeatureType):
        FeatureType.deprecation_warning()
        feature_type = feature_type.name
    return ProteinFeatureTypePredicate(
        feature_type=feature_type,
        protein_metadata=protein_metadata,
    )


def protein_feature(
    feature_id: str,
    protein_metadata: ProteinMetadata,
) -> VariantPredicate:
    """
    Prepare a :class:`VariantPredicate` to test if the variant affects a protein feature
    labeled with the provided `feature_id`.

    Args:
        feature_id: the id of the target protein feature (e.g. `ANK 1`)
        protein_metadata: the information about the protein.
    """
    return ProteinFeaturePredicate(
        feature_id=feature_id,
        protein_metadata=protein_metadata,
    )
