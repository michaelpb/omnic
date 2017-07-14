from omnic.conversion import converter


class NodeSdfToSvgRenderer(converter.ExecConverter):
    inputs = [
        'SD',
        'SDF',
        'chemical/x-mdl-sdfile',
    ]

    outputs = [
        'SVG',
        'image/svg+xml',
    ]

    command = [
        'sdftosvg',
        '$IN',
        '$OUT',
    ]


class OpenBabelConverter(converter.ExecConverter):
    # NOTE: All these input types are untested
    inputs = [
        'ABINIT',  # ABINIT Output Format
        'ACESOUT',  # ACES output format
        'ACR',  # ACR format
        'ADFOUT',  # ADF output format
        'ALC',  # Alchemy format
        'ARC',  # Accelrys/MSI Biosym/Insight II CAR format
        'AXSF',  # XCrySDen Structure Format
        'BGF',  # MSI BGF format
        'BOX',  # Dock 3.5 Box format
        'BS',  # Ball and Stick format
        'C09OUT',  # Crystal 09 output format
        'C3D1',  # Chem3D Cartesian 1 format
        'C3D2',  # Chem3D Cartesian 2 format
        'CACCRT',  # Cacao Cartesian format
        'CAN',  # Canonical SMILES format
        'CAR',  # Accelrys/MSI Biosym/Insight II CAR format
        'CASTEP',  # CASTEP format
        'CCC',  # CCC format
        'CDX',  # ChemDraw binary format
        'CDXML',  # ChemDraw CDXML format
        'CIF',  # Crystallographic Information File
        'CK',  # ChemKin format
        'CML',  # Chemical Markup Language
        'CMLR',  # CML Reaction format
        'config',  # DL-POLY CONFIG
        'contcar',  # VASP format
        'CRK2D',  # Chemical Resource Kit diagram(2D)
        'CRK3D',  # Chemical Resource Kit 3D format
        'CT',  # ChemDraw Connection Table format
        'CUB',  # Gaussian cube format
        'CUBE',  # Gaussian cube format
        'DAT',  # Generic Output file format
        'DMOL',  # DMol3 coordinates format
        'DX',  # OpenDX cube format for APBS
        'ENT',  # Protein Data Bank format
        'FA',  # FASTA format
        'FASTA',  # FASTA format
        'FCH',  # Gaussian formatted checkpoint file format
        'FCHK',  # Gaussian formatted checkpoint file format
        'FCK',  # Gaussian formatted checkpoint file format
        'FEAT',  # Feature format
        'FHIAIMS',  # FHIaims XYZ format
        'FRACT',  # Free Form Fractional format
        'FS',  # Fastsearch format
        'FSA',  # FASTA format
        'G03',  # Gaussian Output
        'G09',  # Gaussian Output
        'G92',  # Gaussian Output
        'G94',  # Gaussian Output
        'G98',  # Gaussian Output
        'GAL',  # Gaussian Output
        'GAM',  # GAMESS Output
        'GAMESS',  # GAMESS Output
        'GAMIN',  # GAMESS Input
        'GAMOUT',  # GAMESS Output
        'GOT',  # GULP format
        'GPR',  # Ghemical format
        'GRO',  # GRO format
        'GUKIN',  # GAMESS-UK Input
        'GUKOUT',  # GAMESS-UK Output
        'GZMAT',  # Gaussian Z-Matrix Input
        'HIN',  # HyperChem HIN format
        'history',  # DL-POLY HISTORY
        'INCHI',  # InChI format
        'INP',  # GAMESS Input
        'INS',  # ShelX format
        'JOUT',  # Jaguar output format
        'LOG',  # Generic Output file format
        'MCDL',  # MCDL format
        'MCIF',  # Macromolecular Crystallographic Info
        'MDL',  # MDL MOL format
        'ML2',  # Sybyl Mol2 format
        'MMCIF',  # Macromolecular Crystallographic Info
        'MMD',  # MacroModel format
        'MMOD',  # MacroModel format
        'MOL',  # MDL MOL format
        'MOL2',  # Sybyl Mol2 format
        'MOLD',  # Molden format
        'MOLDEN',  # Molden format
        'MOLF',  # Molden format
        'MOO',  # MOPAC Output format
        'MOP',  # MOPAC Cartesian format
        'MOPCRT',  # MOPAC Cartesian format
        'MOPIN',  # MOPAC Internal
        'MOPOUT',  # MOPAC Output format
        'MPC',  # MOPAC Cartesian format
        'MPO',  # Molpro output format
        'MPQC',  # MPQC output format
        'MRV',  # Chemical Markup Language
        'MSI',  # Accelrys/MSI Cerius II MSI format
        'NWO',  # NWChem output format
        'OUT',  # Generic Output file format
        'OUTMOL',  # DMol3 coordinates format
        'OUTPUT',  # Generic Output file format
        'PC',  # PubChem format
        'PCM',  # PCModel Format
        'PDB',  # Protein Data Bank format
        'PDBQT',  # AutoDock PDQBT format
        'POS',  # POS cartesian coordinates format
        'poscar',  # VASP format
        'PQR',  # PQR format
        'PQS',  # Parallel Quantum Solutions format
        'PREP',  # Amber Prep format
        'PWSCF',  # PWscf format
        'QCOUT',  # Q-Chem output format
        'RES',  # ShelX format
        'RSMI',  # Reaction SMILES format
        'RXN',  # MDL RXN format
        'SD',  # MDL MOL format
        'SDF',  # MDL MOL format
        'SMI',  # SMILES format
        'SMILES',  # SMILES format
        'SY2',  # Sybyl Mol2 format
        'T41',  # ADF TAPE41 format
        'TDD',  # Thermo format
        'TEXT',  # Read and write raw text
        'THERM',  # Thermo format
        'TMOL',  # TurboMole Coordinate format
        # 'TXT', # Title format
        'TXYZ',  # Tinker XYZ format
        'UNIXYZ',  # UniChem XYZ format
        'vasp',  # VASP format
        'VMOL',  # ViewMol format
        'XML',  # General XML format
        'XSF',  # XCrySDen Structure Format
        'XTC',  # XTC format
        'XYZ',  # XYZ cartesian coordinates format
        'YOB',  # YASARA.org YOB format

        # mimetypes of the above
        'chemical/x-alchemy',
        'chemical/x-cdx',
        'chemical/x-cerius',
        'chemical/x-chem3d',
        'chemical/x-chemdraw',
        'chemical/x-cif',
        'chemical/x-cml',
        'chemical/x-daylight-smiles',
        'chemical/x-gamess-input',
        'chemical/x-gaussian-checkpoint',
        'chemical/x-gaussian-cube',
        'chemical/x-gaussian-input',
        'chemical/x-gaussian-log',
        'chemical/x-hin',
        'chemical/x-jcamp-dx',
        'chemical/x-kinemage',
        'chemical/x-macmolecule',
        'chemical/x-macromodel-input',
        'chemical/x-mdl-molfile',
        'chemical/x-mdl-rdfile',
        'chemical/x-mdl-rxnfile',
        'chemical/x-mdl-sdfile',
        'chemical/x-mdl-tgf',
        'chemical/x-mmcif',
        'chemical/x-mol2',
        'chemical/x-mopac-graph',
        'chemical/x-mopac-input',
        'chemical/x-mopac-out',
        'chemical/x-pdb',
        'chemical/x-rosdal',
        'chemical/x-xyz',
    ]

    outputs = [
        'PNG',
        'SVG',
        'image/png',
        'image/svg+xml',
    ]

    command = [
        'obabel',
        '$IN',
        '$0',
    ]

    def get_arguments(self, out):
        return ['-O%s' % out.cache_path]
