from nomad.config.models.plugins import SchemaPackageEntryPoint


class SolubilitySchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_solubility_plugin.schema_packages.schema_package import m_package

        return m_package


schema_package_entry_point = SolubilitySchemaPackageEntryPoint(
    name='OSI Hackathon Schema',
    description='Schema package for solubility and equilibrium solution data.',
)
