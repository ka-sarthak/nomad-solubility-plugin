"""NOMAD schema definitions for solubility and equilibrium solution data."""

import numpy as np
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    QuantityDisplayAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    BaseSection,
    PubChemPureSubstanceSection,
    PublicationReference,
)
from nomad.metainfo import MEnum, Quantity, SchemaPackage, Section, SubSection

m_package = SchemaPackage()


class Amount(ArchiveSection):
    m_def = Section(
        description=(
            'Named solubility and composition quantities for one component, normalized '
            'to the declared storage units. For a header 10^n q, divide the tabulated '
            'value by 10^n before unit conversion. Several measures may coexist; '
            'omitted measures are not derived.'
        ),
    )

    mole_fraction = Quantity(
        type=np.float64,
        description=(
            'Component amount divided by total amount in its phase: x in liquids, '
            'y in gases, or x(s) in solids; dimensionless.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    mass_fraction = Quantity(
        type=np.float64,
        description=(
            'Component mass divided by solution mass; dimensionless. Divide printed '
            '100 w or g per 100 g solution by 100, g/kg solution by 1000, '
            'and mg/kg solution by 1000000.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    molality = Quantity(
        type=np.float64,
        unit='mole / kilogram',
        description='Solute amount per unit mass of solvent, in mol/kg solvent.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    molar_concentration = Quantity(
        type=np.float64,
        unit='mole / meter ** 3',
        description=(
            'Component amount per solution volume, in mol/m^3. Multiply mol/dm^3 '
            'or mol/L values by 1000 for storage.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        a_display=QuantityDisplayAnnotation(unit='mole / decimeter ** 3'),
    )
    mass_concentration = Quantity(
        type=np.float64,
        unit='kilogram / meter ** 3',
        description=(
            'Component mass per solution volume, in kg/m^3; g/dm^3 and g/L have '
            'the same numerical value. Mass-per-mass forms use mass_fraction or '
            'solute_solvent_mass_ratio according to the stated denominator.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        a_display=QuantityDisplayAnnotation(unit='gram / decimeter ** 3'),
    )
    solute_solvent_mass_ratio = Quantity(
        type=np.float64,
        description=(
            'Solute mass divided by solvent mass; dimensionless. Divide g per '
            '100 g solvent by 100, g/kg solvent by 1000, and mg/kg solvent by '
            '1000000. The source must identify the solvent denominator.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    bunsen_coefficient = Quantity(
        type=np.float64,
        description=(
            "Bunsen coefficient alpha: gas volume at the source's stated reference "
            'conditions (usually 273.15 K and 1 atm) divided by solvent volume '
            'at measurement conditions; dimensionless. Use '
            'bunsen_coefficient_per_pressure for a pressure-normalized result.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    bunsen_coefficient_per_pressure = Quantity(
        type=np.float64,
        unit='1 / pascal',
        description=(
            'Bunsen reference-condition gas-volume/solvent-volume ratio divided '
            'by gas partial pressure, in Pa^-1. The source must specify the '
            'gas-volume reference conditions; convert inverse-atmosphere '
            'values to inverse pascals.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    ostwald_coefficient = Quantity(
        type=np.float64,
        description=(
            'Ostwald coefficient L: gas volume at measurement temperature and '
            'pressure divided by solvent volume at measurement conditions; '
            'dimensionless. No value is derived from the Bunsen coefficient.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    kuenen_coefficient = Quantity(
        type=np.float64,
        unit='meter ** 3 / kilogram',
        description=(
            "Kuenen coefficient S: gas volume at the source's stated reference "
            'conditions (usually 273.15 K and 1 atm) per solvent mass, in m^3/kg. '
            'Use kuenen_coefficient_per_pressure for a pressure-normalized result.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    kuenen_coefficient_per_pressure = Quantity(
        type=np.float64,
        unit='meter ** 3 / (kilogram * pascal)',
        description=(
            'Kuenen reference-condition gas volume per solvent mass divided by '
            'gas partial pressure, in m^3/(kg Pa). The source must specify the '
            'gas-volume reference conditions; convert cm^3/(g atm) to the '
            'storage units.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    henry_constant_p_over_x = Quantity(
        type=np.float64,
        unit='pascal',
        description=(
            'Henry constant defined as gas partial pressure divided by '
            'liquid-phase mole fraction, p/x, in pascals. Select this convention '
            'from the source definition, not the symbol H alone.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    henry_constant_p_over_c = Quantity(
        type=np.float64,
        unit='pascal * meter ** 3 / mole',
        description=(
            'Henry constant defined as gas partial pressure divided by '
            'liquid-phase molar concentration, p/c, in Pa m^3/mol. Convert '
            'reported atm m^3/mol or dm^3 mmHg/mol to these storage units.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    henry_constant_c_gas_over_c_liquid = Quantity(
        type=np.float64,
        description=(
            'Henry constant defined as gas-phase molar concentration divided by '
            'liquid-phase molar concentration using matching concentration units; '
            'dimensionless. Select this convention from the source definition, '
            'not the symbol H alone.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    partial_pressure = Quantity(
        type=np.float64,
        unit='pascal',
        description=(
            'Component partial pressure associated with the reported '
            'gas-solubility measurements, in pascals. No pressure is assumed '
            'when omitted.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        a_display=QuantityDisplayAnnotation(unit='kilopascal'),
    )
    estimated_error_solubility = Quantity(
        type=str,
        description=(
            'Reported estimated error in solubility, preserved as source text '
            'with its expression, units, symbols, and line breaks.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )


class PhaseComponent(ArchiveSection):
    name = Quantity(
        type=str,
        description='Short descriptive name identifying this component within the phase.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )
    density = Quantity(
        type=np.float64,
        unit='kilogram / meter ** 3',
        description=(
            'Mass density of this component at the stated measurement '
            'conditions, in kg/m^3.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    source_purity = Quantity(
        type=str,
        description=(
            'Reported source, preparation, and purity of this material, '
            'preserved as text including units, symbols, percentages, and line breaks.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )

    substance = SubSection(
        section_def=PubChemPureSubstanceSection,
        description=(
            'Chemical identity and PubChem details of the substance forming '
            'this component.'
        ),
    )
    amount = SubSection(
        section_def=Amount,
        description=(
            'Reported solubility and composition quantities for this component, '
            'normalized to the declared storage units.'
        ),
    )


class Phase(ArchiveSection):
    name = Quantity(
        type=str,
        description=(
            'Short descriptive name identifying this phase within the '
            'equilibrium solution.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )
    state_of_matter = Quantity(
        type=MEnum('solid', 'liquid', 'gas'),
        description='Physical state of the phase, such as solid, liquid, or gas.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
    )
    density = Quantity(
        type=np.float64,
        unit='kilogram / meter ** 3',
        description=(
            'Bulk mass density of this phase at the stated measurement '
            'conditions, in kg/m^3.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    salinity = Quantity(
        type=np.float64,
        unit='dimensionless',
        description=(
            'Mass of dissolved salts divided by solution mass in this phase; '
            'dimensionless. Divide reported g/kg solution by 1000 for storage.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    ph = Quantity(
        type=np.float64,
        description='pH of this phase at the stated measurement conditions; dimensionless.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )

    substance = SubSection(
        section_def=PubChemPureSubstanceSection,
        description=(
            'Chemical identity and PubChem details of the substance forming this phase.'
        ),
    )
    components = SubSection(
        section_def=PhaseComponent,
        repeats=True,
        description=(
            'Components forming this phase, with their substance details and '
            'solubility quantities.'
        ),
    )


# BaseSection must precede EntryData so its normalizer can call EntryData
# without re-entering BaseSection.normalize.
class EquilibriumSolution(BaseSection, EntryData):
    temperature = Quantity(
        type=np.float64,
        unit='kelvin',
        description='Isothermal temperature of the solution.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        a_display=QuantityDisplayAnnotation(unit='celsius'),
    )
    temperature_initial = Quantity(
        type=np.float64,
        unit='kelvin',
        description=(
            'Initial temperature T_in of a dynamic measurement interval, in kelvin.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    temperature_final = Quantity(
        type=np.float64,
        unit='kelvin',
        description=(
            'Final temperature T_fin of a dynamic measurement interval, in kelvin.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    estimated_error_temperature = Quantity(
        type=str,
        description=(
            'Reported estimated error in temperature, preserved as source text '
            'with its expression, units, symbols, and line breaks.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )
    pressure = Quantity(
        type=np.float64,
        unit='pascal',
        description=(
            'Total gas pressure over the solution, in pascals; component '
            'partial pressures are stored in PhaseComponent.amount.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        a_display=QuantityDisplayAnnotation(unit='pascal'),
    )
    measurement_methods = Quantity(
        type=str,
        shape=['*'],
        description=(
            'Methods used to measure the equilibrium properties of the solution.'
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )
    mixing_methods = Quantity(
        type=str,
        shape=['*'],
        description='Methods used to mix the components when preparing the solution.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )

    phases = SubSection(section_def=Phase, repeats=True)
    publication_references = SubSection(section_def=PublicationReference, repeats=True)


m_package.__init_metainfo__()
