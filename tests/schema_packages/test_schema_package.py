from pathlib import Path

import pytest
import yaml
from nomad.client import parse
from nomad.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.metainfo.basesections import (
    PubChemPureSubstanceSection,
    PublicationReference,
)
from nomad.units import ureg
from nomad.utils import get_logger

from nomad_solubility_plugin.schema_packages import schema_package_entry_point
from nomad_solubility_plugin.schema_packages.schema_package import (
    Amount,
    EquilibriumSolution,
    Phase,
    PhaseComponent,
    m_package,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_SECTIONS = (Amount, PhaseComponent, Phase, EquilibriumSolution)


@pytest.fixture(scope='module')
def yaml_sections():
    schema = yaml.safe_load((PACKAGE_ROOT / 'schema.archive.yaml').read_text())
    return schema['definitions']['sections']


def test_schema_package_entry_point(yaml_sections):
    assert schema_package_entry_point.load() is m_package
    assert {section.name for section in m_package.section_definitions} == set(
        yaml_sections
    )


@pytest.mark.parametrize('section_class', SCHEMA_SECTIONS)
def test_sections_match_yaml(section_class, yaml_sections):
    definition = section_class.m_def
    expected = yaml_sections[definition.name]

    assert definition.description == expected.get('description')
    assert {base.name for base in definition.base_sections} == {
        base.rsplit('.', 1)[-1] for base in expected['base_sections']
    }
    assert {quantity.name for quantity in definition.quantities} == set(
        expected['quantities']
    )
    assert {subsection.name for subsection in definition.sub_sections} == set(
        expected.get('sub_sections', {})
    )


@pytest.mark.parametrize('section_class', SCHEMA_SECTIONS)
def test_quantities_match_yaml(section_class, yaml_sections):
    expected_quantities = yaml_sections[section_class.__name__]['quantities']
    for name, expected in expected_quantities.items():
        quantity = section_class.m_def.all_quantities[name]
        serialized = quantity.m_to_dict()
        assert quantity.description == expected['description']
        assert quantity.shape == expected.get('shape', [])
        assert quantity.unit == (
            ureg.Unit(expected['unit']) if 'unit' in expected else None
        )

        expected_type = expected['type']
        if expected_type == 'np.float64':
            assert serialized['type'] == {
                'type_kind': 'numpy',
                'type_data': 'float64',
            }
        elif expected_type == 'str':
            assert serialized['type'] == {'type_kind': 'python', 'type_data': 'str'}
        else:
            assert serialized['type']['type_kind'].lower() == 'enum'
            assert set(serialized['type']['type_data']) == set(
                expected_type['type_data']
            )

        for annotation, value in expected['m_annotations'].items():
            assert serialized['m_annotations'][annotation] == [value]


@pytest.mark.parametrize('section_class', SCHEMA_SECTIONS)
def test_subsections_match_yaml(section_class, yaml_sections):
    expected_subsections = yaml_sections[section_class.__name__].get('sub_sections', {})
    for name, expected in expected_subsections.items():
        subsection = section_class.m_def.all_sub_sections[name]
        assert (
            subsection.sub_section.name
            == (expected['section'].rsplit('/', 1)[-1].rsplit('.', 1)[-1])
        )
        assert subsection.repeats == expected.get('repeats', False)
        assert subsection.description == expected.get('description')


def test_nested_archive_round_trip():
    archive = parse(str(PACKAGE_ROOT / 'tests' / 'data' / 'test.archive.yaml'))[0]
    serialized = archive.m_to_dict()
    restored = EntryArchive.m_from_dict(serialized)
    assert restored.m_to_dict() == serialized

    solution = restored.data
    assert isinstance(solution, EquilibriumSolution)
    assert list(solution.measurement_methods) == ['static equilibrium', 'gravimetry']
    assert list(solution.mixing_methods) == ['stirring']
    assert solution.estimated_error_temperature == (
        '±0.05 K\nReported thermometer uncertainty.\n'
    )
    assert [phase.state_of_matter for phase in solution.phases] == ['liquid', 'gas']
    liquid, gas = solution.phases
    assert isinstance(liquid, Phase)
    assert isinstance(liquid.substance, PubChemPureSubstanceSection)
    assert [component.name for component in liquid.components] == [
        'carbon dioxide',
        'water',
    ]
    solute = liquid.components[0]
    assert isinstance(solute, PhaseComponent)
    assert isinstance(solute.substance, PubChemPureSubstanceSection)
    assert solute.source_purity == (
        'Synthetic source, purity ≥99.9 %.\nDried before use.\n'
    )
    assert isinstance(solute.amount, Amount)
    assert solute.amount.estimated_error_solubility == (
        '±2 %\nReported relative uncertainty.\n'
    )
    assert gas.components[0].amount.partial_pressure.to('pascal').magnitude == (
        pytest.approx(100000.0)
    )
    assert all(
        isinstance(reference, PublicationReference)
        for reference in solution.publication_references
    )
    assert [
        reference.publication_title for reference in solution.publication_references
    ] == [
        'Synthetic solubility study',
        'Synthetic measurement methods',
    ]


@pytest.mark.parametrize(
    ('section_class', 'quantity_name', 'measurement', 'expected'),
    [
        (Amount, 'molar_concentration', (0.25, 'mole / liter'), 250.0),
        (Amount, 'mass_concentration', (1.5, 'gram / liter'), 1.5),
        (Amount, 'partial_pressure', (1.0, 'atmosphere'), 101325.0),
        (
            Amount,
            'bunsen_coefficient_per_pressure',
            (1.0, '1 / atmosphere'),
            1 / 101325,
        ),
        (
            Amount,
            'kuenen_coefficient_per_pressure',
            (1.0, 'centimeter ** 3 / (gram * atmosphere)'),
            0.001 / 101325,
        ),
        (Phase, 'salinity', (35.0, 'gram / kilogram'), 0.035),
        (EquilibriumSolution, 'temperature', (25.0, 'degree_Celsius'), 298.15),
    ],
)
def test_storage_unit_conversion(section_class, quantity_name, measurement, expected):
    section = section_class(**{quantity_name: ureg.Quantity(*measurement)})
    quantity = getattr(section, quantity_name)
    assert quantity.magnitude == pytest.approx(expected)


@pytest.mark.parametrize('state', ['solid', 'liquid', 'gas'])
def test_state_of_matter(state):
    assert Phase(state_of_matter=state).state_of_matter == state


def test_invalid_state_of_matter():
    with pytest.raises(ValueError):
        Phase(state_of_matter='plasma')


def test_normalization_preserves_reported_amounts():
    amount = Amount(mole_fraction=0.001, mass_fraction=0.002, bunsen_coefficient=0.8)
    reported_amounts = amount.m_to_dict()
    solution = EquilibriumSolution(
        name='Incomplete solution',
        temperature_initial=293.15,
        temperature_final=303.15,
        phases=[
            Phase(
                state_of_matter='liquid',
                components=[PhaseComponent(name='solute', amount=amount)],
            )
        ],
    )
    archive = EntryArchive(
        metadata=EntryMetadata(entry_name='test.archive.yaml'),
        data=solution,
    )

    solution.normalize(archive, get_logger(__name__))

    assert archive.metadata.entry_type == 'EquilibriumSolution'
    assert archive.metadata.entry_name == solution.name
    assert solution.name in archive.results.eln.names
    assert solution.temperature is None
    assert solution.pressure is None
    assert amount.partial_pressure is None
    assert amount.ostwald_coefficient is None
    assert amount.m_to_dict() == reported_amounts
