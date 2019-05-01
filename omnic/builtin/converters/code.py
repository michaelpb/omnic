from omnic.conversion import converter


class HighlightSyntaxHighlighter(converter.ExecConverter):
    inputs = [
        # ABAP/4
        'ABAP4',
        'ABP',

        # ABC
        'ABC',

        # Advanced Backus-Naur Form
        'ABNF',

        # Action Script
        'ACTIONSCRIPT',
        'AS',

        # ADA95
        'ADA',
        'A',
        'ADB',
        'ADS',
        'GNAD',

        # Agda
        'AGDA',

        # ALGOL 68
        'ALGOL',
        'ALG',

        # AMPL
        'AMPL',
        'DAT',
        'RUN',

        # AMTrix
        'AMTRIX',
        'HND',
        'S4',
        'S4H',
        'S4T',
        'T4',

        # AppleScript
        'APPLESCRIPT',

        # Arc
        'ARC',

        # ARM
        'ARM',

        # AS/400 CL
        'AS400CL',

        # ASCEND
        'ASCEND',
        'A4C',

        # ASP
        'ASP',
        'ASA',

        # Abstract
        'ASPECT',
        'WAS',
        'WUD',

        # Assembler
        'ASSEMBLER',
        'ASM',

        # Applied Type System
        'ATS',
        'DATS',

        # AutoHotKey
        'AUTOHOTKEY',
        'AHK',

        # AutoIt
        'AUTOIT',
        'AU3',

        # Avenue
        'AVENUE',

        # (G)AWK
        'AWK',

        # DOS Batch
        'BAT',
        'CMD',

        # BBcode
        # 'BBCODE',

        # BCPL
        'BCPL',

        # BibTeX
        # 'BIBTEX',
        # 'BIB',

        # Biferno
        'BIFERNO',
        'BFR',

        # Bison
        'BISON',
        'Y',

        # Blitz Basic
        'BLITZBASIC',
        'BB',

        # BM Script
        'BMS',

        # Backus-Naur Form
        'BNF',

        # Boo
        'BOO',

        # C and C++
        'C',
        'C++',
        'CC',
        'CPP',
        'CU',
        'CXX',
        'H',
        'HH',
        'HPP',
        'HXX',

        # Ceylon
        'CEYLON',

        # Charmm
        'CHARMM',
        'INP',

        # CHILL
        'CHILL',
        'CHL',

        # Clean
        'CLEAN',
        'ICL',

        # ClearBasic
        'CLEARBASIC',
        'CB',

        # Clipper
        'CLIPPER',

        # Clojure
        'CLOJURE',

        # Clips
        'CLP',

        # COBOL
        'COBOL',
        'CBL',
        'COB',

        # ColdFusion MX
        'COLDFUSION',
        'CFC',
        'CFM',

        # Crack
        'CRK',

        # C#
        'CSHARP',
        'CS',

        # CSS
        'CSS',

        # D
        'D',

        # Dart
        'DART',

        # Diff
        'DIFF',
        'PATCH',

        # Dylan
        'DYLAN',

        # Extended Backus-Naur Form
        'EBNF',

        # Eiffel
        'EIFFEL',
        'E',
        'SE',

        # Erlang
        'ERLANG',
        'ERL',
        'HRL',

        # Euphoria
        'EUPHORIA',
        'EU',
        'EW',
        'EX',
        'EXW',
        'WXU',

        # Express
        'EXPRESS',
        'EXP',

        # FAME
        'FAME',
        'FAME',

        # Felix
        'FELIX',
        'FLX',

        # Fortran 77
        'FORTRAN77',
        'F',
        'FOR',
        'FTN',

        # Fortran 90
        'FORTRAN90',
        'F90',
        'F95',

        # Frink
        'FRINK',

        # F#
        'FSHARP',
        'FS',
        'FSX',

        # Java FX
        'FX',

        # Gambas
        'GAMBAS',
        'CLASS',

        # gdb
        'GDB',

        # Go
        'GO',

        # Graphviz
        'GRAPHVIZ',
        'DOT',

        # Haskell
        'HASKELL',
        'HS',

        # haXe
        'HAXE',
        'HX',

        # Hecl
        'HCL',

        # HTML
        # 'HTML',
        # 'HTM',
        # 'XHTML',

        # Apache Config
        'HTTPD',

        # Icon
        # 'ICON',
        # 'ICN',

        # IDL
        'IDL',

        # Interactive Data Language
        'IDLANG',

        # Lua (for LuaTeX)
        'INC_LUATEX',

        # Informix
        'INFORMIX',
        '4GL',

        # INI
        'INI',
        'DOXYFILE',

        # Inno Setup
        'INNOSETUP',
        'ISS',

        # INTERLIS
        'INTERLIS',
        'ILI',

        # IO
        'IO',

        # Jasmin
        'JASMIN',
        'J',

        # Java
        'JAVA',
        'GROOVY',
        'GRV',

        # Javascript
        'JS',

        # JSP
        'JSP',

        # LDAP
        'LDIF',

        # Haskell LHS
        # 'LHS',

        # Lilypond
        # 'LILYPOND',
        # 'LY',

        # Limbo
        'LIMBO',
        'B',

        # Linden Script
        'LINDENSCRIPT',
        'LSL',

        # Lisp
        'LISP',
        'CL',
        'CLISP',
        'EL',
        'LSP',
        'SBCL',
        'SCOM',

        # Logtalk
        'LOGTALK',
        'LGT',

        # Lotos
        'LOTOS',

        # Lotus
        'LOTUS',
        'LS',

        # Lua
        'LUA',

        # Luban
        'LUBAN',
        'LBN',

        # Make
        'MAKE',
        'MAK',
        'MAKEFILE',
        'MK',

        # Maple
        'MAPLE',
        'MPL',

        # Matlab
        'MATLAB',
        'M',

        # Maya
        'MAYA',
        'MEL',

        # Mercury
        'MERCURY',

        # Miranda
        'MIRANDA',

        # Modula2
        'MOD2',
        'DEF',
        'MOD',

        # Modula3
        'MOD3',
        'I3',
        'M3',

        # Modelica
        'MODELICA',
        'MO',

        # MoonScript
        'MOON',

        # MaxScript
        'MS',

        # MSSQL
        'MSSQL',

        # Magic eXtensible Markup Language
        'MXML',

        # Notation3 (N3), N-Triples, Turtle, SPARQL
        'N3',
        'NT',
        'TTL',

        # Nasal
        'NASAL',
        'NAS',

        # NeXT Byte Codes
        'NBC',

        # Nemerle
        'NEMERLE',
        'N',

        # NetRexx
        'NETREXX',
        'NRX',

        # Nice
        'NICE',

        # NSIS
        'NSIS',
        'NSI',

        # Not eXactly C
        'NXC',

        # Oberon
        'OBERON',
        'OOC',

        # Objective C
        'OBJC',

        # Objective Caml
        'OCAML',
        'ML',
        'MLI',

        # Octave
        'OCTAVE',

        # OpenObjectRexx
        'OOREXX',

        # Object Script
        'OS',

        # Oz
        'OZ',

        # Paradox
        'PARADOX',
        'SC',

        # Pascal
        'PAS',

        # Highlighting definitions for the Portable Document Format (PDF)
        # 'PDF',

        # Perl
        'PERL',
        'CGI',
        'PERL',
        'PL',
        'PLEX',
        'PLX',
        'PM',

        # PHP
        'PHP',
        'PHP3',
        'PHP4',
        'PHP5',
        'PHP6',

        # Pike
        'PIKE',
        'PMOD',

        # PL/1
        'PL1',
        'BDY',
        'FF',
        'FP',
        'FPP',
        'RPP',
        'SF',
        'SP',
        'SPB',
        'SPE',
        'SPP',
        'SPS',
        'WF',
        'WP',
        'WPB',
        'WPP',
        'WPS',

        # PL/Perl
        'PLPERL',

        # PL/Python
        'PLPYTHON',

        # PL/Tcl
        'PLTCL',

        # POV-Ray
        # 'POV',

        # Prolog
        'PRO',

        # Progress
        'PROGRESS',
        'I',
        'P',
        'W',

        # PostScript
        # 'PS',

        # Microsoft PowerShell
        'PS1',

        # PATROL
        'PSL',

        # Pure
        'PURE',

        # Pyrex
        'PYREX',
        'PYX',

        # Python
        'PYTHON',
        'PY',

        # Qore
        'Q',

        # QMake Project
        'QMAKE',

        # Qu
        'QU',

        # R
        'R',

        # Rebol
        'REBOL',

        # Rexx
        'REXX',
        'REX',
        'RX',
        'THE',

        # Relax NG
        'RNC',

        # RPG
        'RPG',

        # RPL Programming Language
        'RPL',

        # Ruby
        'RUBY',
        'GEMFILE',
        'PP',
        'RAKEFILE',
        'RB',
        'RJS',
        'RUBY',

        # PowerPC Assembler
        'S',

        # SAS
        'SAS',

        # Scala
        'SCALA',

        # Scilab
        'SCILAB',
        'SCE',
        'SCI',

        # Bash
        'SH',
        'BASH',
        'EBUILD',
        'ECLASS',

        # SMALL
        'SMALL',
        'SMA',

        # Smalltalk
        'SMALLTALK',
        'GST',
        'SQ',
        'ST',

        # Standard ML
        'SML',

        # SNMP
        'SNMP',
        'MIB',
        'SMI',

        # SNOBOL
        'SNOBOL',
        'SNO',

        # RPM Spec
        'SPEC',

        # SPIN SQL
        'SPN',

        # PL/SQL
        'SQL',

        # Squirrel
        'SQUIRREL',
        'NUT',

        # Sybase SQL
        'SYBASE',

        # Tcl/Tk
        'TCL',
        'ITCL',
        'WISH',

        # TCSH
        'TCSH',

        # TeX and LaTeX
        # 'TEX',
        # 'CLS',
        # 'STY',

        # TypeScript
        'TS',

        # Transact-SQL
        'TSQL',

        # TTCN3
        'TTCN3',

        # Plain text
        'TXT',
        'TEXT',

        # UPC (and C, technically)
        'UPC',

        # Vala
        'VALA',

        # Visual Basic
        'VB',
        'BAS',
        'BASIC',
        'BI',
        'VBS',

        # Verilog
        'VERILOG',
        'V',

        # VHDL
        'VHD',

        # XML
        # 'SVG',
        # 'SGM',
        # 'SGML',
        # 'WML',
        'XML',
        'DTD',
        'ECF',
        'ENT',
        'HDR',
        'HUB',
        'JNLP',
        'NRM',
        'RESX',
        'TLD',
        'VXML',
        'XSD',
        'XSL',

        # SuperX++
        'XPP',

        # Yaiff
        'YAIFF',

        # Yang
        'YANG',

        # Zonnon
        'ZNN',


        # Mimetypes of above:
        'text/x-boo',
        'text/x-c++hdr',
        'text/x-c++src',
        'text/x-chdr',
        # 'text/x-component',  # Not sure
        'text/x-crontab',
        'text/x-csh',
        'text/x-csrc',
        'text/x-dsrc',
        'text/x-diff',
        'text/x-haskell',
        'text/x-java',
        # 'text/x-lilypond',  # Should be handled by a music related one
        # 'text/x-literate-haskell',  # Handled by PanDoc
        'text/x-makefile',
        'text/x-moc',
        'text/x-pascal',
        'text/x-pcs-gcd',
        'text/x-perl',
        'text/x-python',
        'text/x-scala',
        # 'text/x-server-parsed-html',  # Not sure
        'text/x-setext',
        'text/x-sfv',
        'text/x-sh',
        'text/x-tcl',
        # 'text/x-tex',  # Hndled by PanDoc
        # 'text/x-vcalendar',  # ditto
    ]

    outputs = [
        'HTML',
    ]

    command = [
        'highlight',
        '--fragment',
        '--line-numbers',
        '--force',
        '--anchors',
        '--anchor-prefix=num',
        '--class-name=omnic-highlight--',
        '--enclose-pre',
        '--inline-css',
        '--replace-tabs=8',
        '$IN',
        '-o',
        '$OUT',
    ]
