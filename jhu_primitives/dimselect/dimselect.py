#!/usr/bin/env python

# dimselect.py
# Copyright (c) 2017. All rights reserved.


from rpy2 import robjects
from typing import Sequence, TypeVar, Union, Dict
import os
<<<<<<< HEAD
=======
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
>>>>>>> a8743767cceafd5ac6a68f0330100efb5d443e8c
from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase
import numpy as np
from d3m import utils
from d3m_metadata import hyperparams, base as metadata_module, params
from d3m.primitive_interfaces import base
from d3m.primitive_interfaces.base import CallResult

Inputs = container.ndarray
Outputs = container.ndarray

class Params(params.Params):
    pass

class Hyperparams(hyperparams.Hyperparams):
    n_elbows = hyperparams.Hyperparameter[int](default=3, semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'])

def file_path_conversion(abs_file_path, uri="file"):
    local_drive, file_path = abs_file_path.split(':')[0], abs_file_path.split(':')[1]
    path_sep = file_path[0]
    file_path = file_path[1:]  # Remove initial separator
    if len(file_path) == 0:
        print("Invalid file path: len(file_path) == 0")
        return

    s = ""
    if path_sep == "/":
        s = file_path
    elif path_sep == "\\":
        splits = file_path.split("\\")
        data_folder = splits[-1]
        for i in splits:
            if i != "":
                s += "/" + i
    else:
        print("Unsupported path separator!")
        return

    if uri == "file":
        return "file://localhost" + s
    else:
        return local_drive + ":" + s



class DimensionSelection(TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    # This should contain only metadata which cannot be automatically determined from the code.
    metadata = metadata_module.PrimitiveMetadata({
        # Simply an UUID generated once and fixed forever. Generated using "uuid.uuid4()".
        'id': '7b8ff08a-f887-3be5-86c8-9f0123bd4936',
        'version': "0.3.0",
        'name': "jhu.dimselect",
        # The same path the primitive is registered with entry points in setup.py.
        'python_path': 'd3m.primitives.jhu_primitives.DimensionSelection',
        # Keywords do not have a controlled vocabulary. Authors can put here whatever they find suitable.
        'keywords': ['dimselect primitive'],
        'source': {
            'name': "JHU",
            'uris': [
                # Unstructured URIs. Link to file and link to repo in this case.
                'https://github.com/neurodata/primitives-interfaces/jhu_primitives/dimselect/dimselect.py',
#                'https://github.com/youngser/primitives-interfaces/blob/jp-devM1/jhu_primitives/ase/ase.py',
                'https://github.com//neurodata/primitives-interfaces.git',
            ],
        },
        # A list of dependencies in order. These can be Python packages, system packages, or Docker images.
        # Of course Python packages can also have their own dependencies, but sometimes it is necessary to
        # install a Python package first to be even able to run setup.py of another package. Or you have
        # a dependency which is not on PyPi.
        'installation': [{
            'type': metadata_module.PrimitiveInstallationType.PIP,
            'package_uri': 'git+https://github.com/neurodata/primitives-interfaces.git@{git_commit}#egg=jhu_primitives'.format(
                git_commit=utils.current_git_commit(os.path.dirname(__file__)),
                ),
        }],
        # URIs at which one can obtain code for the primitive, if available.
        # 'location_uris': [
        #     'https://gitlab.com/datadrivendiscovery/tests-data/raw/{git_commit}/primitives/test_primitives/monomial.py'.format(
        #         git_commit=utils.current_git_commit(os.path.dirname(__file__)),
        #     ),
        # ],
        # Choose these from a controlled vocabulary in the schema. If anything is missing which would
        # best describe the primitive, make a merge request.
        'algorithm_types': [
            "HIGHER_ORDER_SINGULAR_VALUE_DECOMPOSITION"
        ],
        'primitive_family': "DATA_TRANSFORMATION"
    })

    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:
        """
        Select the right number of dimensions within which to embed given
        an adjacency matrix

        **Positional Arguments:**

        X:
            - Adjacency matrix
        """
        
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                "dimselect.interface.R")

        path = file_path_conversion(path, uri="")
        n_elbows = self.hyperparams['n_elbows']

        cmd = """
        source("%s")
        fn <- function(X, n_elbows) {
            dimselect.interface(X, n_elbows)
        }
        """ % path

        #print(cmd)

        result = np.array(robjects.r(cmd)(inputs, n_elbows))

        outputs = container.ndarray(result)

        return base.CallResult(outputs)
