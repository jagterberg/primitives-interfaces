#!/usr/bin/env python

# nonpar.py
# Copyright (c) 2017. All rights reserved.

from rpy2 import robjects
from typing import Sequence, TypeVar, Union, Dict
import os

from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase
import numpy as np


from d3m import container
from d3m import utils
from d3m.metadata import hyperparams, base as metadata_module, params
from d3m.primitive_interfaces import base
from d3m.primitive_interfaces.base import CallResult

Inputs = container.ndarray
Outputs = container.ndarray

class Params(params.Params):
    pass

class Hyperparams(hyperparams.Hyperparams):
    sigma = hyperparams.Hyperparameter[float](default=0.5, semantic_types=[
        'https://metadata.datadrivendiscovery.org/types/TuningParameter'
    ])

class NonParametricClustering(TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    # This should contain only metadata which cannot be automatically determined from the code.
    metadata = metadata_module.PrimitiveMetadata({
        # Simply an UUID generated once and fixed forever. Generated using "uuid.uuid4()".
        'id': '2e3cda2b-ce4a-39ae-ae02-22dc33affd17',
        'version': "0.1.0",
        'name': "jhu.nonpar",
        # The same path the primitive is registered with entry points in setup.py.
        'python_path': 'd3m.primitives.jhu_primitives.NonParametricClustering',
        # Keywords do not have a controlled vocabulary. Authors can put here whatever they find suitable.
        'keywords': ['nonparametric'],
        'source': {
            'name': "JHU",
            'uris': [
                # Unstructured URIs. Link to file and link to repo in this case.
                'https://github.com/neurodata/primitives-interfaces/jhu_primitives/nonpar/nonpar.py',
#                'https://github.com/youngser/primitives-interfaces/blob/jp-devM1/jhu_primitives/ase/ase.py',
                'https://github.com/neurodata/primitives-interfaces.git',
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
        Non-parametric clustering

        **Positional Arguments:**

        xhat1:
            - A numpy.ndarray type "matrix"
        xhat2:
            - A numpy.ndarray type "matrix"

        **Optional Arguments:**

        sigma:
            - a sigma for the Gaussian kernel
        """

        #xhat1 = inputs[0,:,:]
        #xhat2 = inputs[1,:,:]

        xhat1 = inputs[0]
        xhat2 = inputs[1]

        sigma = self.hyperparams['sigma']

        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                "nonpar.interface.R")

        cmd = """
        source("%s")
        fn <- function(xhat1, xhat2, sigma) {
            nonpar.interface(xhat1, xhat2, sigma)
        }
        """ % path

        result =  np.array(robjects.r(cmd)(xhat1, xhat2, sigma))

        outputs = container.ndarray(result)

        return base.CallResult(outputs)
