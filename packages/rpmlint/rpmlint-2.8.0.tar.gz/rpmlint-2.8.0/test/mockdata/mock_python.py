from Testing import get_tested_mock_package


########################
# Python mock packages #
########################

# Not valid doc folder in python packages
PythonDocFolderPackage = get_tested_mock_package(
    lazyload=True,
    files=[
        '/usr/lib/python2.7/site-packages/python-mypackage/doc',
        '/usr/lib/python2.7/site-packages/python-mypackage/docs',
        '/usr/lib/python3.10/site-packages/python-mypackage/doc',
        '/usr/lib/python3.10/site-packages/python-mypackage/docs',
        '/usr/lib64/python2.7/site-packages/python-mypackage/doc',
        '/usr/lib64/python2.7/site-packages/python-mypackage/docs',
        '/usr/lib64/python3.10/site-packages/python-mypackage/doc',
        '/usr/lib64/python3.10/site-packages/python-mypackage/docs',
    ]
)


# Valid doc folder in python package if it's a python module
PythonDocModulePackage = get_tested_mock_package(
    lazyload=True,
    files={
        '/usr/lib/python2.7/site-packages/python-mypackage/doc/__init__.py': {'create_dirs': True, 'include_dirs': 2},
        '/usr/lib/python2.7/site-packages/python-mypackage/docs/__init__.py': {'create_dirs': True, 'include_dirs': 1},
        '/usr/lib64/python2.7/site-packages/python-mypackage/doc/__init__.py': {'create_dirs': True, 'include_dirs': 2},
        '/usr/lib64/python2.7/site-packages/python-mypackage/docs/__init__.py': {'create_dirs': True, 'include_dirs': 1},
        '/usr/lib/python3.10/site-packages/python-mypackage/doc/__init__.py': {'create_dirs': True, 'include_dirs': 2},
        '/usr/lib/python3.10/site-packages/python-mypackage/docs/__init__.py': {'create_dirs': True, 'include_dirs': 1},
        '/usr/lib64/python3.10/site-packages/python-mypackage/doc/__init__.py': {'create_dirs': True, 'include_dirs': 2},
        '/usr/lib64/python3.10/site-packages/python-mypackage/docs/__init__.py': {'create_dirs': True, 'include_dirs': 1},
    }
)


# Python package with old egginfo file, not folder
PythonEggInfoFileackage = get_tested_mock_package(
    lazyload=True,
    files={
        '/usr/lib/python2.7/site-packages/mydistutilspackage.egg-info': {'content': 'Metadata-Version: 2.1\nName: pythoncheck'},
        '/usr/lib/python3.10/site-packages/mydistutilspackage.egg-info': {'content': 'Metadata-Version: 2.1\nName: pythoncheck'},
        '/usr/lib64/python2.7/site-packages/mydistutilspackage.egg-info': {'content': 'Metadata-Version: 2.1\nName: pythoncheck'},
        '/usr/lib64/python3.10/site-packages/mydistutilspackage.egg-info': {'content': 'Metadata-Version: 2.1\nName: pythoncheck'},
    }
)


PythonFlitMockPackage = get_tested_mock_package(
    lazyload=True,
    files={
        '/usr/lib/python3.10/site-packages/flit-3.8.0.dist-info/METADATA': {
            'content-path': 'files/python-flit-metadata.txt',
            'create_dirs': True,
        },
    },
    header={
        'requires': [
            'python-flit_core',
            'python-requests',
            'python-tomli-w',
            'python310-docutils',
        ],
    },
)


# Python package with missing require
PythonFlitMissingRequirePackage = PythonFlitMockPackage.clone(
    header={
        'requires': [
            'python3-flit-core',
            'python3-requests',
            'python3-tomli-w',
        ],
    },
)


# Python package with missing require
PythonFlitLeftoverRequirePackage = PythonFlitMockPackage.clone(
    header={
        'requires': [
            'python3-docutils',
            'python3-flit-core',
            'python3-poetry',
            'python3-requests',
            'python3-tomli-w',
        ],
    },
)


PythonJupyterServerFileidMockPackage = get_tested_mock_package(
    lazyload=True,
    files={
        '/usr/lib/python3.10/site-packages/jupyter_server_fileid-0.9.0.dist-info/METADATA': {
            'content-path': 'files/python-jupyter_server_fileid-metadata.txt',
            'create_dirs': True,
        },
    },
    header={
        'requires': [
            'python-jupyter-events',
            'python-click',
            'python-jupyter-server',
        ],
    },
)


PythonJupyterEventsMockPackage = get_tested_mock_package(
    lazyload=True,
    files={
        '/usr/lib/python3.10/site-packages/jupyter_events-0.6.3.dist-info/METADATA': {
            'content-path': 'files/python-jupyter-events-metadata.txt',
            'create_dirs': True,
        },
    },
    header={
        'requires': [
            'python-jsonschema',
            'python-python-json-logger',
            'python-pyyaml',
            'python-rfc3339-validator',
            'python-rfc3986-validator',
            'python-traitlets',
            'python-click',
            'python-rich',
            'python-jupyterlite-sphinx',
            'python-myst-parser',
            'python-pydata-sphinx-theme',
            'python-sphinxcontrib-spelling',
            'python-click',
            'python-coverage',
            'python-pre-commit',
            'python-pytest-asyncio',
            'python-pytest-console-scripts',
            'python-pytest-cov',
            'python-pytest',
            'python-rich',
        ],
    },
)


PythonScikitBuildMockPackage = get_tested_mock_package(
    lazyload=True,
    files={
        '/usr/lib/python3.10/site-packages/scikit_build-0.17.2.dist-info/METADATA': {
            'content-path': 'files/python-scikit_build-metadata.txt',
            'create_dirs': True,
        },
    },
    header={
        'requires': [
            'python-distro',
            'python-packaging',
            'python-setuptools',
            'python-wheel',
            'python-tomli',
        ],
    },
)


# Python flit package with python3.12dist(foo) requirements (used in Fedora see #1171)
PythonFlitFedoraMockPackage = get_tested_mock_package(
    lazyload=True,
    files={
        '/usr/lib/python3.10/site-packages/flit-3.8.0.dist-info/METADATA': {
            'content-path': 'files/python-flit-metadata.txt',
            'create_dirs': True,
        },
    },
    header={
        'requires': [
            'python3.12dist(docutils)',
            'python3.12dist(flit-core) >= 3.8',
            'python3.12dist(requests)',
            'python3.12dist(tomli-w)',
        ],
    },
)


# Python package with old setuptools metadata format, egg-info folder
PythonIcecreamPackage = get_tested_mock_package(
    lazyload=True,
    files={
        '/usr/lib/python3.10/site-packages/icecream-2.1.3-py3.10.egg-info/requires.txt': {
            'content': """
asttokens>=2.0.1
colorama>=0.3.9
executing>=0.3.1
pygments>=2.2.0
""",
            'create_dirs': True
        },
    },
    header={
        'requires': [
            'asttokens>=2.0.1',
            'colorama>=0.3.9',
            'executing>=0.3.1',
            'pygments>=2.2.0',
        ],
    },
)


# Python package with missing require
PythonIcecreamMissingRequirePackage = PythonIcecreamPackage.clone(
    header={
        'requires': [
            'asttokens>=2.0.1',
            'executing>=0.3.1',
            'pygments>=2.2.0',
        ],
    },
)


# Python package with leftover require
PythonIcecreamLeftoverRequirePackage = PythonIcecreamPackage.clone(
    header={
        'requires': [
            'python3-asttokens >= 2.0.1',
            'python3-colorama >= 0.3.9',
            'python3-executing >= 0.3.1',
            'python3-poetry',
            'python3-pygments >= 2.2.0',
        ],
    },
)


# Python package with multiple pyc for different python versions in the same
# sitelib
PythonMultiplePYCMockPackage = get_tested_mock_package(
    lazyload=True,
    files=[
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/base.cpython-310.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/base.cpython-39.opt-1.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/base.cpython-39.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/__init__.cpython-310.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/__init__.cpython-39.opt-1.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/__init__.cpython-39.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_saferef.cpython-310.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_saferef.cpython-39.opt-1.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_saferef.cpython-39.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_utilities.cpython-310.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_utilities.cpython-39.opt-1.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_utilities.cpython-39.pyc',
    ]
)


# Python package with pyc files but just the correct version
PythonSinglePYCMockPackage = get_tested_mock_package(
    lazyload=True,
    files=[
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/base.cpython-39.opt-1.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/base.cpython-39.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/__init__.cpython-39.opt-1.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/__init__.cpython-39.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_saferef.cpython-39.opt-1.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_saferef.cpython-39.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_utilities.cpython-39.opt-1.pyc',
        '/usr/lib/python3.9/site-packages/blinker/__pycache__/_utilities.cpython-39.pyc',
    ]
)


IPythonMissingRequirePackage = get_tested_mock_package(
    lazyload=True,
    files={
        '/usr/lib/python3.12/site-packages/ipython-8.14.0-py3.12.egg-info/requires.txt': {
            'content-path': 'files/ipython-requires.txt',
        },
    },
    header={'requires': [
        'python-leftover',
        'python-no-leftover',
    ]},
)
