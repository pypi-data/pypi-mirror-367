import ast
import ftplib
import multiprocessing
import zlib
import subprocess
import os
import sys
import time
import hashlib
import secrets

import json

from tqdm.notebook import tqdm
from pathlib import Path
from ftplib import FTP
import dimod
import numpy as np
from IPython.core.display_functions import clear_output
from tabulate import tabulate

from config import DynexConfig
from models import BQM
from api import DynexAPI


def _check_list_length(lst):
    """
    `Internal Function`

    :Returns:
    - TRUE if the sat problem is k-Sat, FALSE if the problem is 3-sat or 2-sat (`bool`)
    """

    for sublist in lst:
        if isinstance(sublist, list) and len(sublist) > 3:
            return True
    return False


################################################################################################################################
# utility functions
################################################################################################################################

def _calculate_sha3_256_hash(string):
    """
    `Internal Function`
    """
    sha3_256_hash = hashlib.sha3_256()
    sha3_256_hash.update(string.encode('utf-8'))
    return sha3_256_hash.hexdigest()


def _calculate_sha3_256_hash_bin(bin):
    """
    `Internal Function`
    """
    sha3_256_hash = hashlib.sha3_256()
    sha3_256_hash.update(bin)
    return sha3_256_hash.hexdigest()


def _Convert(a):
    """
    `Internal Function`
    """
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct


def _max_value(inputlist):
    """
    `Internal Function`
    """
    return max([sublist[-1] for sublist in inputlist])


def _getCoreCount():
    """
    `Internal Function`
    """
    if sys.platform == 'win32':
        return (int)(os.environ['NUMBER_OF_PROCESSORS'])
    else:
        return (int)(os.popen('grep -c cores /proc/cpuinfo').read())


################################################################################################################################
# save clauses to SAT cnf file
################################################################################################################################

def _save_cnf(clauses, filename, mainnet):
    """
    `Internal Function`

    Saves the model as an encrypted .bin file locally in /tmp as defined in dynex.ini
    """

    num_variables = max(max(abs(lit) for lit in clause) for clause in clauses)
    num_clauses = len(clauses)

    with open(filename, 'w') as f:
        line = "p cnf %d %d" % (num_variables, num_clauses)

        line_enc = line
        f.write(line_enc + "\n")

        for clause in clauses:
            line = ' '.join(str(int(lit)) for lit in clause) + ' 0'
            line_enc = line
            f.write(line_enc + "\n")


################################################################################################################################
# save wcnf file
################################################################################################################################


def to_wcnf_string(clauses, num_variables, num_clauses):
    """
    `Internal Function`

    Saves the model as an string
    """

    line = "p wcnf %d %d\n" % (num_variables, num_clauses)
    for clause in clauses:
        line += ' '.join(str(int(lit)) for lit in clause) + ' 0\n'
    return line


def _test_completed():
    """
    `Internal Function`

    :Returns:

    - Returns TRUE if dynex.test() has been successfully completed, FALSE if dynex.test() was not successfully completed (`bool`)
    """

    local_path = 'dynex.test'
    return os.path.isfile(local_path)


################################################################################################################################
# Dynex sampling functions
################################################################################################################################
def sample_qubo(Q, offset=0.0, logging=True, formula=2, mainnet=False, description='Dynex SDK Job', test=False,
                bnb=True, num_reads=32, annealing_time=10, clones=1, switchfraction=0.0, alpha=20, beta=20, gamma=1,
                delta=1, epsilon=1, zeta=1, minimum_stepsize=0.00000006, debugging=False, block_fee=0, is_cluster=False,
                cluster_type=1,
                shots=1, v2=False):
    """
    Samples a Qubo problem.

    :Parameters:

    - :Q: The Qubo problem

    - :offset: The offset value of the Qubo problem

    - :logging: Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (`bool`)

    - :mainnet: Defines if the mainnet (Dynex platform sampling) or the testnet (local sampling) is being used for sampling (`bool`)

    - :description: Defines the description for the sampling, which is shown in Dynex job dashboards as well as in the market place  (`string`)

    - :num_reads: Defines the number of parallel samples to be performed (`int` value in the range of [32, MAX_NUM_READS] as defined in your license)

    - :annealing_time: Defines the number of integration steps for the sampling. Models are being converted into neuromorphic circuits, which are then simulated with ODE integration by the participating workers (`int` value in the range of [1, MAX_ANNEALING_TIME] as defined in your license)

    - :clones: Defines the number of clones being used for sampling. Default value is 1 which means that no clones are being sampled. Especially when all requested num_reads will fit on one worker, it is desired to also retrieve the optimum ground states found from more than just one worker. The number of clones runs the sampler for n clones in parallel and aggregates the samples. This ensures a broader spectrum of retrieved samples. Please note, it the number of clones is set higher than the number of available threads on your local machine, then the number of clones processed in parallel is being processed in batches. Clone sampling is only available when sampling on the mainnet. (`integer` value in the range of [1,128])

    - :switchfraction: Defines the percentage of variables which are replaced by random values during warm start samplings (`double` in the range of [0.0, 1.0])

    - :alpha: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :beta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :gamma: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :delta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :epsilon: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :zeta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :minimum_stepsize: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is performig adaptive stepsizes for each ODE integration forward Euler step. This value defines the smallest step size for a single adaptive integration step (`double` value in the range of [0.0000000000000001, 1.0])

    - :debugging: Only applicable for test-net sampling. Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (TRUE) (`bool`)

    - :bnb: Use alternative branch-and-bound sampling when in mainnet=False (`bool`)

    - :block_fee: Computing jobs on the Dynex platform are being prioritised by the block fee which is being offered for computation. If this parameter is not specified, the current average block fee on the platform is being charged. To set an individual block fee for the sampling, specify this parameter, which is the amount of DNX in nanoDNX (1 DNX = 1,000,000,000 nanoDNX)

    - :shots: Sets the minimum number of solutions to retrieve from the network. Works both on mainnet=False and mainnet=True (Default: 1). Typically used for situations where not only the best global optimum (sampleset.first) is required, but multiple optima from different workers.

    :Returns:

    - Returns a dimod sampleset object class:`dimod.sampleset`

    :Example:

    .. code-block:: Python

        from pyqubo import Array
        N = 15
        K = 3
        numbers = [4.8097315016016315, 4.325157567810298, 2.9877429101815127,
                   3.199880179616316, 0.5787939511978596, 1.2520928214246918,
                   2.262867466401502, 1.2300003067401255, 2.1601079352817925,
                   3.63753899583021, 4.598232793833491, 2.6215815162575646,
                   3.4227134835783364, 0.28254151584552023, 4.2548151473817075]

        q = Array.create('q', N, 'BINARY')
        H = sum(numbers[i] * q[i] for i in range(N)) + 5.0 * (sum(q) - K)**2
        model = H.compile()
        Q, offset = model.to_qubo(index_label=True)
        sampleset = dynex.sample_qubo(Q, offset, formula=2, annealing_time=200, bnb=True)
        print(sampleset)
           0  1  2  3  4  5  6  7  8  9 10 11 12 13 14   energy num_oc.
        0  0  1  0  0  0  0  0  1  0  0  1  0  0  0  0 2.091336       1
        ['BINARY', 1 rows, 1 samples, 15 variables]

    """
    bqm = dimod.BinaryQuadraticModel.from_qubo(Q, offset)
    model = BQM(bqm, logging=logging, formula=formula)
    sampler = DynexSampler(model, mainnet=mainnet, logging=logging, description=description, bnb=bnb, v2=v2)
    sampleset = sampler.sample(num_reads=num_reads, annealing_time=annealing_time, clones=clones,
                               switchfraction=switchfraction, alpha=alpha, beta=beta, gamma=gamma, delta=delta,
                               epsilon=epsilon, zeta=zeta, minimum_stepsize=minimum_stepsize, debugging=debugging,
                               block_fee=block_fee, is_cluster=is_cluster, shots=shots, cluster_type=cluster_type)
    return sampleset


def sample_ising(h, j, logging=True, formula=2, mainnet=False, description='Dynex SDK Job', test=False, bnb=True,
                 num_reads=32, annealing_time=10, clones=1, switchfraction=0.0, alpha=20, beta=20, gamma=1, delta=1,
                 epsilon=1, zeta=1, minimum_stepsize=0.00000006, debugging=False, block_fee=0, is_cluster=False,
                 shots=1, cluster_type=1, v2=False):
    """
    Samples an Ising problem.

    :Parameters:

    - :h: Linear biases of the Ising problem

    - :j: Quadratic biases of the Ising problem

    - :logging: Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (`bool`)

    - :mainnet: Defines if the mainnet (Dynex platform sampling) or the testnet (local sampling) is being used for sampling (`bool`)

    - :description: Defines the description for the sampling, which is shown in Dynex job dashboards as well as in the market place  (`string`)

    - :num_reads: Defines the number of parallel samples to be performed (`int` value in the range of [32, MAX_NUM_READS] as defined in your license)

    - :annealing_time: Defines the number of integration steps for the sampling. Models are being converted into neuromorphic circuits, which are then simulated with ODE integration by the participating workers (`int` value in the range of [1, MAX_ANNEALING_TIME] as defined in your license)

    - :clones: Defines the number of clones being used for sampling. Default value is 1 which means that no clones are being sampled. Especially when all requested num_reads will fit on one worker, it is desired to also retrieve the optimum ground states found from more than just one worker. The number of clones runs the sampler for n clones in parallel and aggregates the samples. This ensures a broader spectrum of retrieved samples. Please note, it the number of clones is set higher than the number of available threads on your local machine, then the number of clones processed in parallel is being processed in batches. Clone sampling is only available when sampling on the mainnet. (`integer` value in the range of [1,128])

    - :switchfraction: Defines the percentage of variables which are replaced by random values during warm start samplings (`double` in the range of [0.0, 1.0])

    - :alpha: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :beta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :gamma: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :delta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :epsilon: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :zeta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :minimum_stepsize: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is performig adaptive stepsizes for each ODE integration forward Euler step. This value defines the smallest step size for a single adaptive integration step (`double` value in the range of [0.0000000000000001, 1.0])

    - :debugging: Only applicable for test-net sampling. Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (TRUE) (`bool`)

    - :bnb: Use alternative branch-and-bound sampling when in mainnet=False (`bool`)

    - :block_fee: Computing jobs on the Dynex platform are being prioritised by the block fee which is being offered for computation. If this parameter is not specified, the current average block fee on the platform is being charged. To set an individual block fee for the sampling, specify this parameter, which is the amount of DNX in nanoDNX (1 DNX = 1,000,000,000 nanoDNX)

    - :shots: Sets the minimum number of solutions to retrieve from the network. Works both on mainnet=False and mainnet=True (Default: 1). Typically used for situations where not only the best global optimum (sampleset.first) is required, but multiple optima from different workers.

    :Returns:

    - Returns a dimod sampleset object class:`dimod.sampleset`

    """
    bqm = dimod.BinaryQuadraticModel.from_ising(h, j)
    model = BQM(bqm, logging=logging, formula=formula)
    sampler = DynexSampler(model, mainnet=mainnet, logging=logging, description=description, bnb=bnb, v2=v2)
    sampleset = sampler.sample(num_reads=num_reads, annealing_time=annealing_time, clones=clones,
                               switchfraction=switchfraction, alpha=alpha, beta=beta, gamma=gamma, delta=delta,
                               epsilon=epsilon, zeta=zeta, minimum_stepsize=minimum_stepsize, debugging=debugging,
                               block_fee=block_fee, is_cluster=is_cluster, shots=shots, cluster_type=cluster_type)
    return sampleset


def sample(bqm, logging=True, formula=2, mainnet=False, description='Dynex SDK Job', test=False, bnb=True, num_reads=32,
           annealing_time=10, clones=1, switchfraction=0.0, alpha=20, beta=20, gamma=1, delta=1, epsilon=1, zeta=1,
           minimum_stepsize=0.00000006, debugging=False, block_fee=0, is_cluster=False, shots=1, cluster_type=1,
           v2=False):
    """
    Samples a Binary Quadratic Model (bqm).

    :Parameters:

    - :bqm: Binary quadratic model to sample

    - :logging: Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (`bool`)

    - :mainnet: Defines if the mainnet (Dynex platform sampling) or the testnet (local sampling) is being used for sampling (`bool`)

    - :description: Defines the description for the sampling, which is shown in Dynex job dashboards as well as in the market place  (`string`)

    - :num_reads: Defines the number of parallel samples to be performed (`int` value in the range of [32, MAX_NUM_READS] as defined in your license)

    - :annealing_time: Defines the number of integration steps for the sampling. Models are being converted into neuromorphic circuits, which are then simulated with ODE integration by the participating workers (`int` value in the range of [1, MAX_ANNEALING_TIME] as defined in your license)

    - :clones: Defines the number of clones being used for sampling. Default value is 1 which means that no clones are being sampled. Especially when all requested num_reads will fit on one worker, it is desired to also retrieve the optimum ground states found from more than just one worker. The number of clones runs the sampler for n clones in parallel and aggregates the samples. This ensures a broader spectrum of retrieved samples. Please note, it the number of clones is set higher than the number of available threads on your local machine, then the number of clones processed in parallel is being processed in batches. Clone sampling is only available when sampling on the mainnet. (`integer` value in the range of [1,128])

    - :switchfraction: Defines the percentage of variables which are replaced by random values during warm start samplings (`double` in the range of [0.0, 1.0])

    - :alpha: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :beta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :gamma: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :delta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :epsilon: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :zeta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

    - :minimum_stepsize: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is performig adaptive stepsizes for each ODE integration forward Euler step. This value defines the smallest step size for a single adaptive integration step (`double` value in the range of [0.0000000000000001, 1.0])

    - :debugging: Only applicable for test-net sampling. Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (TRUE) (`bool`)

    - :bnb: Use alternative branch-and-bound sampling when in mainnet=False (`bool`)

    - :block_fee: Computing jobs on the Dynex platform are being prioritised by the block fee which is being offered for computation. If this parameter is not specified, the current average block fee on the platform is being charged. To set an individual block fee for the sampling, specify this parameter, which is the amount of DNX in nanoDNX (1 DNX = 1,000,000,000 nanoDNX)

    - :shots: Sets the minimum number of solutions to retrieve from the network. Works both on mainnet=False and mainnet=True (Default: 1). Typically used for situations where not only the best global optimum (sampleset.first) is required, but multiple optima from different workers.

    :Returns:

    - Returns a dimod sampleset object class:`dimod.sampleset`

    :Example:

    .. code-block:: Python

        from pyqubo import Array
        N = 15
        K = 3
        numbers = [4.8097315016016315, 4.325157567810298, 2.9877429101815127,
                   3.199880179616316, 0.5787939511978596, 1.2520928214246918,
                   2.262867466401502, 1.2300003067401255, 2.1601079352817925,
                   3.63753899583021, 4.598232793833491, 2.6215815162575646,
                   3.4227134835783364, 0.28254151584552023, 4.2548151473817075]

        q = Array.create('q', N, 'BINARY')
        H = sum(numbers[i] * q[i] for i in range(N)) + 5.0 * (sum(q) - K)**2
        model = H.compile()
        Q, offset = model.to_qubo(index_label=True)
        bqm = dimod.BinaryQuadraticModel.from_qubo(Q, offset)
        sampleset = dynex.sample(bqm, offset, formula=2, annealing_time=200, bnb=True)
        print(sampleset)
           0  1  2  3  4  5  6  7  8  9 10 11 12 13 14   energy num_oc.
        0  0  1  0  0  0  0  0  1  0  0  1  0  0  0  0 2.091336       1
        ['BINARY', 1 rows, 1 samples, 15 variables]

    """
    model = BQM(bqm, logging=logging, formula=formula)
    sampler = DynexSampler(model, mainnet=mainnet, logging=logging, description=description, bnb=bnb, v2=v2)
    sampleset = sampler.sample(num_reads=num_reads, annealing_time=annealing_time, clones=clones,
                               switchfraction=switchfraction, alpha=alpha, beta=beta, gamma=gamma, delta=delta,
                               epsilon=epsilon, zeta=zeta, minimum_stepsize=minimum_stepsize, debugging=debugging,
                               block_fee=block_fee, is_cluster=is_cluster, shots=shots, cluster_type=cluster_type)
    return sampleset


################################################################################################################################
# Dynex Sampler (public class)
################################################################################################################################
class DynexSampler:
    """
    Initialises the sampler object given a model.

    :Parameters:

    - :logging: Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (`bool`)
    - :mainnet: Defines if the mainnet (Dynex platform sampling) or the testnet (local sampling) is being used for sampling (`bool`)
    - :description: Defines the description for the sampling, which is shown in Dynex job dashboards as well as in the market place  (`string`)

    :Returns:

    - class:`dynex.samper`

    :Example:

    .. code-block:: Python

        sampler = dynex.DynexSampler(model)

    """

    def __init__(self,
                 model,
                 logging=True,
                 description='Dynex SDK Job',
                 test=False,
                 bnb=True,
                 filename_override='',
                 config: DynexConfig = None):

        # multi-model parallel sampling

        if not config:
            config = DynexConfig()

        self.config = config
        self.logger = config.logger
        self.state = 'initialised'
        self.model = model
        self.logging = logging
        self.filename_override = filename_override
        self.description = description
        self.test = test
        self.dimod_assignments = {}
        self.bnb = bnb

    @staticmethod
    def _sample_thread(q, x, model, logging, logger, description, num_reads, annealing_time, switchfraction, alpha,
                       beta,
                       gamma, delta, epsilon, zeta, minimum_stepsize, block_fee, is_cluster, shots, cluster_type):
        """
        `Internal Function` which creates a thread for clone sampling
        """
        if logging:
            logger.info(f'[DYNEX] Clone {x} started...')
        _sampler = _DynexSampler(model, False, True, description, False)
        _sampleset = _sampler.sample(num_reads, annealing_time, switchfraction, alpha, beta, gamma, delta, epsilon,
                                     zeta,
                                     minimum_stepsize, False, block_fee, is_cluster, shots, cluster_type)
        if logging:
            logger.info(f'[DYNEX] Clone {x} finished')
        q.put(_sampleset)
        return

    def sample(self, num_reads=32, annealing_time=10, clones=1, switchfraction=0.0, alpha=20, beta=20, gamma=1, delta=1,
               epsilon=1, zeta=1, minimum_stepsize=0.00000006, debugging=False, block_fee=0, is_cluster=False, shots=1,
               cluster_type=1):
        """
        The main sampling function:

        :Parameters:

        - :num_reads: Defines the number of parallel samples to be performed (`int` value in the range of [32, MAX_NUM_READS] as defined in your license)

        - :annealing_time: Defines the number of integration steps for the sampling. Models are being converted into neuromorphic circuits, which are then simulated with ODE integration by the participating workers (`int` value in the range of [1, MAX_ANNEALING_TIME] as defined in your license)

        - :clones: Defines the number of clones being used for sampling. Default value is 1 which means that no clones are being sampled. Especially when all requested num_reads will fit on one worker, it is desired to also retrieve the optimum ground states found from more than just one worker. The number of clones runs the sampler for n clones in parallel and aggregates the samples. This ensures a broader spectrum of retrieved samples. Please note, it the number of clones is set higher than the number of available threads on your local machine, then the number of clones processed in parallel is being processed in batches. Clone sampling is only available when sampling on the mainnet. (`integer` value in the range of [1,128])

        - :switchfraction: Defines the percentage of variables which are replaced by random values during warm start samplings (`double` in the range of [0.0, 1.0])

        - :alpha: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :beta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :gamma: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :delta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :epsilon: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :zeta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :minimum_stepsize: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is performig adaptive stepsizes for each ODE integration forward Euler step. This value defines the smallest step size for a single adaptive integration step (`double` value in the range of [0.0000000000000001, 1.0])

        - :debugging: Only applicable for test-net sampling. Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (TRUE) (`bool`)

        - :bnb: Use alternative branch-and-bound sampling when in mainnet=False (`bool`)

        - :block_fee: Computing jobs on the Dynex platform are being prioritised by the block fee which is being offered for computation. If this parameter is not specified, the current average block fee on the platform is being charged. To set an individual block fee for the sampling, specify this parameter, which is the amount of DNX in nanoDNX (1 DNX = 1,000,000,000 nanoDNX)

        - :shots: Sets the minimum number of solutions to retrieve from the network. Works both on mainnet=False and mainnet=True (Default: 1). Typically used for situations where not only the best global optimum (sampleset.first) is required, but multiple optima from different workers.

        :Returns:

        - Returns a dimod sampleset object class:`dimod.sampleset`

        :Example:

        .. code-block::

            import dynex
            import dimod

            # Define the QUBU problem:
            bqmodel = dimod.BinaryQuadraticModel({0: -1, 1: -1}, {(0, 1): 2}, 0.0, dimod.BINARY)

            # Sample the problem:
            model = dynex.BQM(bqmodel)
            sampler = dynex.DynexSampler(model)
            sampleset = sampler.sample(num_reads=32, annealing_time = 100)

            # Output the result:
            print(sampleset)

        .. code-block::

            ╭────────────┬───────────┬───────────┬─────────┬─────┬─────────┬───────┬─────┬──────────┬──────────╮
            │   DYNEXJOB │   ELAPSED │   WORKERS │   CHIPS │   ✔ │   STEPS │   LOC │   ✔ │   ENERGY │        ✔ │
            ├────────────┼───────────┼───────────┼─────────┼─────┼─────────┼───────┼─────┼──────────┼──────────┤
            │       3617 │      0.07 │         1 │       0 │  32 │     100 │     0 │   1 │        0 │ 10000.00 │
            ╰────────────┴───────────┴───────────┴─────────┴─────┴─────────┴───────┴─────┴──────────┴──────────╯
            ╭─────────────────────────────┬───────────┬─────────┬───────┬──────────┬───────────┬───────────────┬──────────╮
            │                      WORKER │   VERSION │   CHIPS │   LOC │   ENERGY │   RUNTIME │   LAST UPDATE │   STATUS │
            ├─────────────────────────────┼───────────┼─────────┼───────┼──────────┼───────────┼───────────────┼──────────┤
            │ *** WAITING FOR WORKERS *** │           │         │       │          │           │               │          │
            ╰─────────────────────────────┴───────────┴─────────┴───────┴──────────┴───────────┴───────────────┴──────────╯
            [DYNEX] FINISHED READ AFTER 0.07 SECONDS
            [DYNEX] PARSING 1 VOLTAGE ASSIGNMENT FILES...
            progress: 100%
            1/1 [00:05<00:00, 5.14s/it]
            [DYNEX] SAMPLESET LOADED
            [DYNEX] MALLOB: JOB UPDATED: 3617 STATUS: 2
               0  1 energy num_oc.
            0  0  1   -1.0       1
            ['BINARY', 1 rows, 1 samples, 2 variables]
        """

        # assert parameters:
        if clones < 1:
            raise Exception("[DYNEX] ERROR: Value of clones must be in range [1,128]")
        if clones > 128:
            raise Exception("[DYNEX] ERROR: Value of clones must be in range [1,128]")
        if self.config.mainnet == False and clones > 1:
            raise Exception("[DYNEX] ERROR: Clone sampling is only supported on the mainnet")

        # sampling without clones: -------------------------------------------------------------------------------------------
        if clones == 1:
            _sampler = _DynexSampler(self.model, self.logging, self.config.mainnet, self.description, self.test,
                                     self.bnb,
                                     self.filename_override, self.config)
            _sampleset = _sampler.sample(num_reads, annealing_time, switchfraction, alpha, beta, gamma, delta, epsilon,
                                         zeta, minimum_stepsize, debugging, block_fee, is_cluster, shots, cluster_type)
            return _sampleset

        # sampling with clones: ----------------------------------------------------------------------------------------------
        else:
            supported_threads = multiprocessing.cpu_count()
            if clones > supported_threads:
                self.logger.info(
                    f'[DYNEX] WARNING: number of clones > CPU cores: clones: {clones} threads available: {supported_threads}')
            jobs = []
            results = []

            if self.logging:
                self.logger.info(f'[DYNEX] STARTING SAMPLING (, {clones}, CLONES )...')

            # define n samplers:
            for i in range(clones):
                q = multiprocessing.Queue()
                results.append(q)
                p = multiprocessing.Process(target=self._sample_thread, args=(
                    q, i, self.model, self.logging, self.logger, self.description, num_reads, annealing_time,
                    switchfraction, alpha, beta, gamma, delta, epsilon, zeta, minimum_stepsize, block_fee, is_cluster,
                    shots, cluster_type))
                jobs.append(p)
                p.start()

            # wait for samplers to finish:
            for job in jobs:
                job.join()

            # collect samples for each job:
            assignments_cum = []
            for result in results:
                assignments = result.get()
                assignments_cum.append(assignments)

            # accumulate and aggregate all results:
            r = None
            for assignment in assignments_cum:
                if len(assignment) > 0:
                    if r == None:
                        r = assignment
                    else:
                        r = dimod.concatenate((r, assignment))

            # aggregate samples:
            r = r.aggregate()

            self.dimod_assignments = r

            return r


################################################################################################################################
# Dynex Sampler class (private)
################################################################################################################################

class _DynexSampler:
    """
    `Internal Class` which is called by public class `DynexSampler`
    """
    num_retries = 10

    def __init__(self, model, logging=True, mainnet=True, description='Dynex SDK Job', test=False,
                 bnb=True, filename_override='', config: DynexConfig = None):

        if not test and not _test_completed():
            raise Exception("CONFIGURATION TEST NOT COMPLETED. PLEASE RUN 'dynex.test()'")

        if model.type not in ['cnf', 'wcnf', 'qasm']:
            raise Exception("INCORRECT MODEL TYPE:", model.type)

        self.description = description
        self.config = config if config is not None else DynexConfig(mainnet=mainnet)
        self.api = DynexAPI(config=self.config, logging=logging)
        self.logger = self.config.logger
        # FTP data where miners submit results:
        self.solutionurl = f'ftp://{self.config.ftp_hostname}/'
        self.solutionuser = f'{self.config.ftp_username}:{self.config.ftp_password}'

        # local path where tmp files are stored
        tmppath = Path("tmp/test.bin")
        tmppath.parent.mkdir(exist_ok=True)
        with open(tmppath, 'w') as f:
            f.write('0123456789ABCDEF')
        self.filepath = 'tmp/'
        self.filepath_full = os.getcwd() + '/tmp'

        # path to testnet
        self.solver_path = self.config.solver_path
        self.bnb = bnb

        # multi-model parallel sampling?
        multi_model_mode = False
        if isinstance(model, list):
            if mainnet == False:
                raise Exception("[ÐYNEX] ERROR: Multi model parallel sampling is only supported on mainnet")
            multi_model_mode = True

        self.multi_model_mode = multi_model_mode

        # single model sampling:
        if multi_model_mode == False:
            # auto generated temp filename:
            if len(filename_override) > 0:
                if filename_override.endswith(".dnx"):
                    self.filename = filename_override
                else:
                    self.filename = filename_override + ".dnx"
            else:
                self.filename = secrets.token_hex(16) + ".dnx"

            self.logging = logging
            self.type_str = model.type_str
            self.wcnf_offset = model.wcnf_offset
            self.precision = model.precision

            if model.type == 'cnf':
                # convert to 3sat?
                if (_check_list_length(model.clauses)):
                    # we need to convert to 3sat:
                    self.clauses = self.api.k_sat(model.clauses)
                else:
                    self.clauses = model.clauses
                _save_cnf(self.clauses, self.filepath + self.filename, mainnet)
                self.num_clauses = len(self.clauses)
                self.num_variables = max(max(abs(lit) for lit in clause) for clause in self.clauses)

            elif model.type == 'wcnf':
                if self.config.solver_version == 1:
                    self.clauses = model.clauses
                    self.num_variables = model.num_variables
                    self.num_clauses = model.num_clauses
                else:
                    self.num_variables = model.bqm.num_variables
                    self.num_clauses = len(model.bqm.to_qubo()[0])
                    self.clauses = model.bqm.to_qubo()
                self.var_mappings = model.var_mappings
                self.precision = model.precision
                self._save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses,
                                self.var_mappings)

            elif model.type == 'qasm':
                self.clauses = None
                self.num_variables = None
                self.num_clauses = None
                self.var_mappings = None
                self.precision = None

            self.type = model.type
            self.assignments = {}
            self.dimod_assignments = {}
            self.bqm = model.bqm
            self.model = model

        # multi model sampling:
        else:
            _filename = []
            _type_str = []
            _clauses = []
            _num_clauses = []
            _num_variables = []
            _var_mappings = []
            _precision = []
            _type = []
            _assignments = []
            _dimod_assignments = []
            _bqm = []
            _model = []
            for m in model:
                _filename.append(secrets.token_hex(16) + ".dnx")
                _type_str.append(m.type)
                if m.type == 'cnf':
                    raise Exception(
                        "[ÐYNEX] ERROR: Multi model parallel sampling is currently not implemented for SAT")
                if m.type == 'wcnf':
                    if self.config.solver_version == 1:
                        _num_clauses.append(m.num_clauses)
                        _num_variables.append(m.num_variables)
                        _clauses.append(m.clauses)
                    else:
                        _num_variables.append(m.bqm.num_variables)
                        _num_clauses.append(len(m.bqm.to_qubo()[0]))
                        _clauses.append(m.bqm.to_qubo())
                    _var_mappings.append(m.var_mappings)
                    _precision.append(m.precision)
                    self._save_wcnf(_clauses[-1], self.filepath + _filename[-1], _num_variables[-1], _num_clauses[-1],
                                    _var_mappings[-1])
                _type.append(m.type)
                _assignments.append({})
                _dimod_assignments.append({})
                _bqm.append(m.bqm)
                _model.append(m)
            self.filename = _filename
            self.type_str = _type_str
            self.clauses = _clauses
            self.num_clauses = _num_clauses
            self.num_variables = _num_variables
            self.var_mappings = _var_mappings
            self.precision = _precision
            self.type = _type
            self.assignments = _assignments
            self.dimod_assignments = _dimod_assignments
            self.bqm = _bqm
            self.model = _model
            self.wcnf_offset = _model.wcnf_offset
            self.precision = _model.precision
            self.logging = logging

        if self.logging:
            self.logger.info("[DYNEX] SAMPLER INITIALISED")

    def _save_wcnf(self, clauses, filename, num_variables, num_clauses, var_mappings):
        """
        `Internal Function`

        Saves the model as an encrypted .bin file locally in /tmp as defined in dynex.ini
        """

        if self.config.solver_version == 1:
            with open(filename, 'w') as f:
                line = "p wcnf %d %d" % (num_variables, num_clauses)

                line_enc = line
                f.write(line_enc + "\n")

                for clause in clauses:
                    line = ' '.join(str(int(lit)) for lit in clause) + ' 0'

                    line_enc = line
                    f.write(line_enc + "\n")
        else:
            with open(filename, 'w') as f:
                line = "p qubo %d %d %f" % (num_variables, num_clauses, clauses[1])
                f.write(line + "\n")
                for (i, j), value in clauses[0].items():
                    if var_mappings:
                        i = next((k for k, v in var_mappings.items() if v == i), i)  # i if not mapped
                        j = next((k for k, v in var_mappings.items() if v == j), j)  # j if not mapped
                    line = "%d %d %f" % (i, j, value)
                    f.write(line + "\n")

    # deletes all assignment files on FTP
    def cleanup_ftp(self, files):
        """
        `Internal Function`

        This function is called on __exit__ of the sampler class or by sampler.clear().
        It ensures that submitted sample-files, which have not been parsed and used from the sampler, will be deleted on the FTP server.
        """

        if len(files) > 0:
            try:
                host = self.solutionurl[6:-1]
                username = self.solutionuser.split(":")[0]
                password = self.solutionuser.split(":")[1]
                directory = ""
                ftp = FTP(host)
                ftp.login(username, password)
                ftp.cwd(directory)
                for file in files:
                    ftp.delete(file)
                if self.logging:
                    self.logger.info("[ÐYNEX] FTP DATA CLEANED")
            except Exception as e:
                self.logger.error(f"[DYNEX] An error occurred while deleting file: {str(e)}")
                raise Exception("ERROR: An error occurred while deleting file")
            finally:
                ftp.quit()
        return

    # delete file from FTP server
    def delete_file_on_ftp(self, hostname, username, password, local_file_path, remote_directory, logging=True):
        """
        `Internal Function`

        Deletes a file on the FTP server as specified in dynex,ini
        """

        ftp = FTP(hostname)
        ftp.login(username, password)
        # Change to the remote directory
        ftp.cwd(remote_directory)
        ftp.delete(local_file_path.split("/")[-1])
        if logging:
            self.logger.info(f'[DYNEX] COMPUTING FILE {local_file_path.split("/")[-1]} REMOVED')
        return

    # upload file to ftp server
    def upload_file_to_ftp(self, hostname, username, password, local_file_path, remote_directory, logging=True):
        """
        `Internal Function`

        Submits a computation file (xxx.bin) to the FTP server as defined in dynex.ini

        :Returns:

        - Status if successul or failed (`bool`)
        """

        retval = True
        try:
            ftp = FTP(hostname)
            ftp.login(username, password)
            # Change to the remote directory
            ftp.cwd(remote_directory)

            # Open the local file in binary mode for reading
            with open(local_file_path, 'rb') as file:
                total = os.path.getsize(local_file_path)  # file size
                # sanity check:
                if total > 104857600:
                    self.logger.error("[ERROR] PROBLEM FILE TOO LARGE (MAX 104,857,600 BYTES)")
                    raise Exception('PROBLEM FILE TOO LARGE (MAX 104,857,600 BYTES)')

                # upload:
                if logging:
                    with tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024,
                              desc='file upload progress') as pbar:
                        def cb(data):
                            pbar.update(len(data))

                        # Upload the file to the FTP server
                        ftp.storbinary(f'STOR {local_file_path.split("/")[-1]}', file, 1024, cb)
                else:
                    # Upload the file to the FTP server
                    ftp.storbinary(f'STOR {local_file_path.split("/")[-1]}', file)

            if logging:
                self.logger.info(
                    f"[DYNEX] File '{local_file_path}' sent successfully to '{hostname}/{remote_directory}'")

        except Exception as e:
            self.logger.error(f"[DYNEX] An error occurred while sending the file: {str(e)}")
            raise Exception("ERROR: An error occurred while sending the file")
            retval = False
        finally:
            ftp.quit()
        return retval

    # calculate ground state energy and numer of falsified softs from model ==========================================================
    def _energy(self, sample, mapping=True):
        """
        `Internal Function`

        Takes a model and dimod samples and calculates the energy and loc.

        Input:
        ======

        - dimod sample (dict) with mapping = True
          example: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0}

        or

        - assignments (list) with mapping = False (raw solution file)
          example: [1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1, -1]
        """
        # convert dimod sample to wcnf mapping:
        wcnf_vars = []
        if mapping:
            for v in sample:
                if v in self.model.var_mappings:
                    v_mapped = self.model.var_mappings[v]
                else:
                    v_mapped = v
                wcnf_vars.append(sample[v_mapped])
        # or convert solution file to 0/1:
        else:
            for v in sample:
                if v > 0:
                    wcnf_vars.append(1)
                else:
                    wcnf_vars.append(0)

        loc = 0
        energy = 0.0
        for clause in self.model.clauses:

            if len(clause) == 2:
                # 2-lit clause:
                w = clause[0]
                i = int(abs(clause[1]))
                i_dir = np.sign(clause[1])
                if i_dir == -1:
                    i_dir = 0
                i_assign = wcnf_vars[i - 1]
                if (i_dir != i_assign):
                    loc += 1
                    energy += w
            else:
                # 3-lit clause:
                w = clause[0]
                i = int(abs(clause[1]))
                i_dir = np.sign(clause[1])
                if i_dir == -1:
                    i_dir = 0
                i_assign = wcnf_vars[i - 1]
                j = int(abs(clause[2]))
                j_dir = np.sign(clause[2])
                if j_dir == -1:
                    j_dir = 0
                j_assign = wcnf_vars[j - 1]
                if (i_dir != i_assign) and (j_dir != j_assign):
                    loc += 1
                    energy += w

        return loc, energy

    def add_salt_local(self):
        """
        `Internal Function`

        Adds salt to new local solutions - ensuring multiple solutions with similar result
        """

        directory = self.filepath_full
        fn = self.filename + "."

        # search for current solution files:
        for filename in os.listdir(directory):
            if filename.startswith(fn):
                # check if salt already added:
                if filename.split('.')[-1].isnumeric():
                    os.rename(directory + '/' + filename, directory + '/' + filename + '.' + secrets.token_hex(16))
        return

        # list local available (downloaded) iles in /tmp =================================================================================

    def list_files_with_text_local(self):
        """
        `Internal Function`

        Scans the temporary directory for assignment files

        :Returns:

        - Returns a list of all assignment files (filenames) which are locally available in /tmp as specified in dynex.ini for the current sampler model (`list`)
        """

        directory = self.filepath_full
        fn = self.filename + "."
        # list to store files
        filtered_files = []

        # search for current solution files:
        for filename in os.listdir(directory):
            if filename.startswith(fn) and filename.endswith('model') == False:
                if os.path.getsize(directory + '/' + filename) > 0:
                    filtered_files.append(filename)

        return filtered_files

        # verify correctness of downloaded file (loc and energy) ==========================================================================

    def validate_file(self, file, debugging=False):
        """
        `Internal Function`

        Validates loc and energy provided in filename with voltages. File not matching will be deleted on FTP and locally.
        """

        # v2 has a different format
        if self.config.solver_version == 2:
            return True

        valid = False

        if self.type == 'cnf':
            return True

        # format: xxx.bin.32.1.0.0.000000
        # jobfile chips steps loc energy
        info = file[len(self.filename) + 1:]
        chips = int(info.split(".")[0])
        steps = int(info.split(".")[1])
        loc = int(info.split(".")[2])

        # energy can also be non decimal:
        if len(info.split(".")) > 4:
            energy = float(info.split(".")[3] + "." + info.split(".")[4])
        else:
            energy = float(info.split(".")[3])

        with open(self.filepath + file, 'r') as ffile:
            data = ffile.read()
            # enough data?
            if self.config.mainnet:
                if len(data) > 96:
                    wallet = data.split("\n")[0]
                    tmp = data.split("\n")[1]
                    voltages = tmp.split(", ")[:-1]
                else:
                    voltages = ['NaN']  # invalid file received
            else:  # test-net is not returning wallet
                voltages = data.split(", ")[:-1]

            # convert string voltages to list of floats:
            voltages = list(map(float, voltages))
            if debugging:
                self.logger.debug('DEBUG:')
                self.logger.debug(voltages)

            # valid result? ignore Nan values and other incorrect data
            if len(voltages) > 0 and voltages[0] != 'NaN' and self.num_variables == len(voltages):
                val_loc, val_energy = self._energy(voltages, mapping=False)

                # from later versions onwards, enforce also correctness of LOC (TBD):
                if energy == val_energy:
                    valid = True

                if debugging:
                    self.logger.debug('DEBUG:', self.filename, chips, steps, loc, energy, '=>', val_loc, val_energy,
                                      'valid?',
                                      valid)

            else:
                if debugging:
                    self.logger.debug('DEBUG:', self.filename, ' NaN or num_variables =', len(voltages), ' vs ',
                                      self.num_variables,
                                      'valid?', valid)

        return valid

    # list and download solution files ================================================================================================
    def list_files_with_text(self, debugging=False):
        """
        `Internal Function`

        Downloads assignment files from the FTP server specified in dynex.ini and stores them in /tmp as specified in dynex.ini
        Downloaded files are automatically deleted on the FTP server.

        :Returns:

        - List of locally in /tmp saved assignment files for the current sampler model (`list`)
        """

        host = self.solutionurl[6:-1]
        username = self.config.ftp_username
        password = self.config.ftp_password
        directory = ""
        text = self.filename
        # Connect to the FTP server
        ftp = FTP(host)
        ftp.login(username, password)

        # Change to the specified directory
        ftp.cwd(directory)

        # List all (fully uploaded) files in the directory (minimum size)
        target_size = 97 + self.num_variables

        for name, facts in ftp.mlsd():
            if 'size' in facts and (int(facts['size']) >= target_size and name.startswith(text)):

                # download file if not already local:
                local_path = self.filepath + name
                if os.path.isfile(local_path) == False or os.path.getsize(local_path) == 0:
                    with open(local_path, 'wb') as file:
                        ftp.retrbinary('RETR ' + name, file.write)
                        file.close()
                    # correct file?
                    if self.validate_file(name, debugging) == False:
                        if self.logging:
                            self.logger.info(
                                f'[DYNEX] REMOVING SOLUTION FILE {name} (WRONG ENERGY REPORTED OR INCORRECT VOLTAGES)')
                        os.remove(local_path)
                        ftp.delete(name)
                        self.api.report_invalid(filename=name, reason='wrong energy reported')
                    else:
                        # correctly downloaded?
                        cnt = 0
                        while os.path.getsize(local_path) == 0:
                            time.sleep(1)
                            with open(local_path, 'wb') as file:
                                if self.logging:
                                    self.logger.info(f'[DYNEX] REDOWNLOADING FILE {name}')
                                ftp.retrbinary('RETR ' + name, file.write)
                                file.close()
                            # correct file?
                            if self.validate_file(name, debugging) == False:
                                if self.logging:
                                    self.logger.info(
                                        f'[DYNEX] REMOVING SOLUTION FILE {name} (WRONG ENERGY REPORTED OR INCORRECT VOLTAGES)')
                                os.remove(local_path)
                                self.api.report_invalid(filename=name, reason='wrong energy reported')
                                break
                            cnt += 1
                            if cnt >= 10:
                                break
                        # finally we delete downloaded files from FTP:
                        self.cnt_solutions = self.cnt_solutions + 1
                        ftp.delete(name)

                        # Close the FTP connection
        ftp.quit()

        # In our status view, we show the local, downloaded and available files:
        filtered_files = self.list_files_with_text_local()

        return filtered_files

    # clean function ======================================================================================================================
    def _clean(self):
        """
        `Internal Function`
        This function can be called after finishing a sampling process on the Mainnet. It ensures that submitted sample-files,
        which have not been parsed and used from the sampler, will be deleted on the FTP server. It is also called automatically
        during __exit___ event of the sampler class.
        """
        if self.config.mainnet:
            files = self.list_files_with_text()
            self.cleanup_ftp(files)

    # on exit ==============================================================================================================================
    def __exit__(self, exc_type, exc_value, traceback):
        """
        `Internal Function`
        Upon __exit__, the function clean() is being called.
        """
        self.logger.info('[DYNEX] SAMPLER EXIT')

    # update function: =====================================================================================================================
    def _update(self, model, logging=True):
        """
        `Internal Function`
        Typically, the sampler object is being initialised with a defined model class. This model can also be updated without
        regenerating a new sampler object by calling the function update(model).
        """
        self.logging = logging
        self.filename = secrets.token_hex(16) + ".bin"

        if model.type == 'cnf':
            # convert to 3sat?
            if (_check_list_length(model.clauses)):
                self.clauses = self.api.d(model.clauses)
            else:
                self.clauses = model.clauses
            _save_cnf(self.clauses, self.filepath + self.filename)

        if model.type == 'wcnf':
            if self.config.solver_version == 1:
                self.clauses = model.clauses
                self.num_variables = model.num_variables
                self.num_clauses = model.num_clauses
            else:
                self.num_variables = model.bqm.num_variables
                self.num_clauses = len(model.bqm.to_qubo()[0])
                self.clauses = model.to_qubo()
            self.var_mappings = model.var_mappings
            self.precision = model.precision
            self._save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses)

        self.type = model.type
        self.assignments = {}
        self.dimod_assignments = {}
        self.bqm = model.bqm

    # print summary of sampler: =============================================================================================================
    def _print(self):
        """
        `Internal Function`
        Prints summary information about the sampler object:

        - :Mainnet: If the mainnet (Dynex platform sampling) or the testnet (local sampling) is being used for sampling (`bool`)
        - :logging: Show progress and status information or be quiet and omit terminal output (`bool`)
        - :tmp filename: The filename of the computation file (`string`)
        - :model type: [cnf, wcnf]: The type of the model: Sat problems (cnf) or QUBU/Ising type problems (wcnf) (`string`)
        - :num_variables: The number of variables of the model (`int`)
        - :num_clauses: The number of clauses of the model (`int`)

        :Example:

        .. code-block::

            DynexSampler object
            mainnet? True
            logging? True
            tmp filename: tmp/b8fa34a815f96098438d68142dfb68b6.dnx
            model type: BQM
            num variables: 15
            num clauses: 120
            configuration: dynex.ini
        """
        self.logger.info('{DynexSampler object}')
        self.logger.info(f'mainnet? {self.config.mainnet}')
        self.logger.info(f'logging? {self.logging}')
        self.logger.info(f'tmp filename: {self.filepath + self.filename}')
        self.logger.info(f'model type: {self.type_str}')
        self.logger.info(f'num variables: {self.num_variables}')
        self.logger.info(f'num clauses: {self.num_clauses}')
        self.logger.info('configuration: dynex.ini')

    # convert a sampler.sampleset[x]['sample'] into an assignment: ==========================================================================
    def _sample_to_assignments(self, lowest_set):
        """
        `Internal Function`
        The voltates of a sampling can be retrieved from the sampler with sampler.sampleset

        The sampler.sampleset returns a list of voltages for each variable, ranging from -1.0 to +1.0 and is a double precision value. Sometimes it is required to transform these voltages to binary values 0 (for negative voltages) or 1 (for positive voltages). This function converts a given sampler.sampleset[x] from voltages to binary values.

        :Parameters:

        - :lowest_set: The class:`dynex.sampler.assignment' which has to be converted (`list`)

        :Returns:

        - Returns the converted sample as `list`
        """
        sample = {}
        i = 0
        for var in self.var_mappings:
            sample[var] = 1
            if (float(lowest_set[i]) < 0):
                sample[var] = 0
            i = i + 1
        return sample

    # sampling entry point: =================================================================================================================
    def sample(self, num_reads=32, annealing_time=10, switchfraction=0.0, alpha=20, beta=20, gamma=1, delta=1,
               epsilon=1, zeta=1, minimum_stepsize=0.00000006, debugging=False, block_fee=0, is_cluster=False, shots=1,
               cluster_type=1):
        """
        `Internal Function` which is called by public function `DynexSampler.sample`
        """

        retval = {}

        # In a malleable environment, it is rarely possible that a worker is submitting an inconsistent solution file. If the job
        # is small, we need to re-sample again. This routine samples up to NUM_RETRIES (10) times. If an error occurs, or
        # a keyboard interrupt was triggered, the return value is a dict containing key 'error'

        for i in range(0, self.num_retries):
            retval = self._sample(num_reads, annealing_time, switchfraction, alpha, beta, gamma, delta, epsilon, zeta,
                                  minimum_stepsize, debugging, block_fee, is_cluster, shots, cluster_type)
            if len(retval) > 0:
                break

            # TODO: support multi-model sampling
            self.logger.info(f'[DYNEX] NO VALID SAMPLE RESULT FOUND. RESAMPLING...{i + 1} / {self.num_retries}')
            # generate a fresh sampling file:
            self.filename = secrets.token_hex(16) + ".bin"
            if self.type == 'cnf':
                # convert to 3sat?
                if (_check_list_length(self.model.clauses)):
                    self.clauses = self.api.r_sat(self.model.clauses)
                else:
                    self.clauses = self.model.clauses
                _save_cnf(self.clauses, self.filepath + self.filename, self.config.mainnet)
            if self.type == 'wcnf':
                self.save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses,
                               self.model.var_mappings)

                # aggregate sampleset:
        if self.type == 'wcnf' and len(retval) > 0 and ('error' in retval) == False:
            retval = retval.aggregate()

        return retval

    # main sampling function =================================================================================================================
    def _sample(self, num_reads=32, annealing_time=10, switchfraction=0.0, alpha=20, beta=20, gamma=1, delta=1,
                epsilon=1, zeta=1, minimum_stepsize=0.00000006, debugging=False, block_fee=0, is_cluster=False, shots=1,
                cluster_type=1):
        """
        `Internal Function` which is called by private function `DynexSampler.sample`. This functions performs the sampling.
        """

        if self.multi_model_mode == True:
            raise Exception('ERROR: Multi-model parallel sampling is not implemented yet')

        if self.type == 'cnf' and self.config.mainnet == False and self.bnb == True:
            raise Exception('ERROR: Your local sampler does not support SAT jobs')

        mainnet = self.config.mainnet
        price_per_block = 0
        self.cnt_solutions = 0

        try:

            # step 1: upload problem file to Dynex Platform: ---------------------------------------------------------------------------------
            if mainnet:
                # create job on mallob system:
                if self.config.solver_version == 1:
                    job_id, self.filename, price_per_block, qasm = self.api.create_job_api(
                        # FIXME Sending arguments by arg=arg
                        self,
                        annealing_time,
                        switchfraction,
                        num_reads,
                        alpha,
                        beta,
                        gamma,
                        delta,
                        epsilon,
                        zeta,
                        minimum_stepsize,
                        block_fee,
                        is_cluster,
                        cluster_type,
                        shots
                    )
                else:
                    job_id, self.filename, price_per_block, qasm = self.api.create_job_api(
                        # FIXME Sending arguments by arg=arg
                        self,
                        annealing_time,
                        switchfraction,
                        num_reads,
                        alpha,
                        beta,
                        gamma,
                        delta,
                        epsilon,
                        zeta,
                        minimum_stepsize,
                        block_fee,
                        is_cluster,
                        cluster_type,
                        shots,
                        0.0 - self.clauses[1]  # TODO useless arg?
                    )

                # show effective price in DNX:
                price_per_block = price_per_block / 1000000000
                # parse qasm data:
                if self.type == 'qasm':
                    _data = qasm
                    _feed_dict = _data['feed_dict']
                    _model = _data['model']
                    if debugging:
                        self.logger.info(f'[DYNEX] feed_dict: {_feed_dict}')
                        self.logger.info(f'[DYNEX] model: {_model}')
                        # construct circuit model:
                    q = zlib.decompress(bytearray.fromhex(_model['q']))
                    q = str(q)[2:-1]
                    offset = float(_model['offset'])
                    bqm = dimod.BinaryQuadraticModel.from_qubo(ast.literal_eval(q), offset)
                    _model = BQM(bqm)
                    self.bqm = bqm
                    if self.config.solver_version == 1:
                        self.clauses = _model.clauses
                        self.num_variables = _model.num_variables
                        self.num_clauses = _model.num_clauses
                    else:
                        self.num_variables = _model.bqm.num_variables
                        self.num_clauses = len(_model.bqm.to_qubo()[0])
                        self.clauses = _model.bqm.to_qubo()
                    self.var_mappings = _model.var_mappings
                    self.precision = _model.precision
                    self._save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses,
                                    self.var_mappings)
                    self.model.clauses = self.clauses
                    self.model.num_variables = self.num_variables
                    self.model.num_clauses = self.num_clauses
                    self.model.var_mappings = self.var_mappings
                    self.model.precision = self.precision
                if self.logging:
                    self.logger.info("[ÐYNEX] STARTING JOB...")
            else:
                # run on test-net:
                if self.type == 'wcnf':
                    localtype = 5
                elif self.type == 'cnf':
                    localtype = 0
                elif self.type == 'qasm':
                    localtype = 5
                    # testnet qasm sampling requires a dedicated library (not in default package):
                    command = 'python3 dynex_circuit_backend.py --mainnet False --file ' + self.model.qasm_filepath + self.model.qasm_filename
                    if debugging:
                        command = command + ' --debugging True'
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                    if debugging:
                        for c in iter(lambda: process.stdout.read(1), b""):
                            sys.stdout.write(c.decode('utf-8'))
                    else:
                        if self.logging:
                            self.logger.info("[DYNEX|TESTNET] *** WAITING FOR READS ***")
                            process.wait()
                    # read returned model:
                    f = open(self.model.qasm_filepath + self.model.qasm_filename + '.model', "r", encoding="utf-8")
                    _data = json.load(f)
                    _feed_dict = _data['feed_dict']
                    _model = _data['model']
                    if debugging:
                        self.logger.debug('[DYNEX|TESTNET] feed_dict:')
                        self.logger.debug(_feed_dict)
                        self.logger.debug('[DYNEX|TESTNET] model:')
                        self.logger.debug(_model)
                    f.close()
                    # construct circuit model:
                    q = zlib.decompress(bytearray.fromhex(_model['q']))
                    q = str(q)[2:-1]
                    offset = _model['offset']
                    bqm = dimod.BinaryQuadraticModel.from_qubo(ast.literal_eval(q), offset)
                    _model = BQM(bqm)
                    self.bqm = bqm
                    if self.config.solver_version == 1:
                        self.clauses = _model.clauses
                        self.num_variables = _model.num_variables
                        self.num_clauses = _model.num_clauses
                    else:
                        self.num_variables = _model.bqm.num_variables
                        self.num_clauses = len(_model.bqm.to_qubo()[0])
                        self.clauses = _model.bqm.to_qubo()
                    self.var_mappings = _model.var_mappings
                    self.precision = _model.precision
                    self.save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses,
                                   self.var_mappings)

                job_id = -1
                command = self.solver_path + "np -t=" + str(localtype) + " -ms=" + str(
                    annealing_time) + " -st=1 -msz=" + str(minimum_stepsize) + " -c=" + str(
                    num_reads) + " --file='" + self.filepath_full + "/" + self.filename + "'"
                # in test-net, it cannot guaranteed that all requested chips are fitting:
                # num_reads = 0

                if alpha != 0:
                    command = command + " --alpha=" + str(alpha)
                if beta != 0:
                    command = command + " --beta=" + str(beta)
                if gamma != 0:
                    command = command + " --gamma=" + str(gamma)
                if delta != 0:
                    command = command + " --delta=" + str(delta)
                if epsilon != 0:
                    command = command + " --epsilon=" + str(epsilon)
                if zeta != 0:
                    command = command + " --zeta=" + str(zeta)

                # use branch-and-bound (testnet) sampler instead?:
                if self.bnb:
                    command = self.solver_path + "dynex-testnet-bnb " + self.filepath_full + "/" + self.filename

                # use v2?
                if self.config.solver_version == 2:
                    command = self.solver_path + "dynexcore"
                    command += " file=" + self.filepath_full + "/" + self.filename
                    command += " num_steps=" + str(annealing_time)
                    command += " population_size=" + str(annealing_time)
                    command += " max_iterations=" + str(num_reads)
                    # command += " cpu_threads=" + str(10)
                    command += " target_energy=" + str(0.0 - self.clauses[1])
                    # command += " ode_steps=" + str(annealing_time)
                    # command += " search_steps=" + str(annealing_time)
                    # command += " mutation_rate=10"
                    command += " init_dt=" + str(minimum_stepsize)
                    # command += " gpu_index=0"
                    self.logger.info(f'[DYNEX DEBUG] Solver command: {command}')

                for shot in range(0, shots):
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                    if debugging:
                        for c in iter(lambda: process.stdout.read(1), b""):
                            sys.stdout.write(c.decode('utf-8'))
                    else:
                        if self.logging:
                            self.logger.info("[DYNEX|TESTNET] *** WAITING FOR READS ***")
                        process.wait()
                    # add salt:
                    self.add_salt_local()

            # step 2: wait for process to be finished: -------------------------------------------------------------------------------------
            t = time.process_time()
            finished = False
            runupdated = False
            cnt_workers = 0

            # initialise display:
            if mainnet and debugging == False:
                clear_output(wait=True)
                table = ([
                    ['DYNEXJOB', 'QUBITS', 'QUANTUM GATES', 'BLOCK FEE', 'ELAPSED', 'WORKERS READ', 'CIRCUITS', 'STEPS',
                     'GROUND STATE']])
                table.append(
                    ['', self.num_variables, self.num_clauses, '', '', '*** WAITING FOR READS ***', '', '', ''])
                ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f")
                self.logger.info(f'\n{ta}\n')

            while not finished:
                total_chips = 0
                total_steps = 0
                lowest_energy = 1.7976931348623158e+308
                lowest_loc = 1.7976931348623158e+308

                # retrieve solutions
                if mainnet:
                    try:
                        files = self.list_files_with_text(debugging)
                        cnt_workers = len(files)
                    except Exception as e:
                        self.logger.info(f'[DYNEX] CONNECTION TO FTP ENDPOINT FAILED: {e}')
                        raise Exception('ERROR: CONNECTION TO FTP ENDPOINT FAILED')
                        files = []
                else:
                    files = self.list_files_with_text_local()
                    time.sleep(1)

                for file in files:
                    if self.type == 'cnf':
                        info = file[len(self.filename) + 1:]
                        chips = -1
                        steps = -1
                        loc = 0
                        energy = 0
                    if self.type == 'wcnf' or self.type == 'qasm':
                        info = file[len(self.filename) + 1:]
                        chips = int(info.split(".")[0])
                        steps = int(info.split(".")[1])
                        loc = int(info.split(".")[2])
                        # energy can also be non decimal:
                        if len(info.split(".")) > 4 and info.split(".")[4].isnumeric():
                            energy = float(info.split(".")[3] + "." + info.split(".")[4])
                        else:
                            energy = float(info.split(".")[3])

                    if mainnet:
                        self.cnt_solutions = cnt_workers
                    else:
                        self.cnt_solutions = self.cnt_solutions + 1
                    total_chips = total_chips + chips
                    total_steps = steps
                    if energy < lowest_energy:
                        lowest_energy = energy
                    if loc < lowest_loc:
                        lowest_loc = loc
                    if self.type == 'cnf' and loc == 0:
                        finished = True
                    if total_chips >= num_reads * 0.90 and self.cnt_solutions >= shots:
                        finished = True

                if cnt_workers < 1:
                    if self.logging:
                        if mainnet and debugging == False:
                            clear_output(wait=True)
                        if mainnet:
                            LOC_MIN, ENERGY_MIN, MALLOB_CHIPS, details = self.api._get_status_details_api(job_id,
                                                                                                          annealing_time,
                                                                                                          wcnf_offset=self.model.wcnf_offset,
                                                                                                          precision=self.model.precision)
                        else:
                            LOC_MIN, ENERGY_MIN, MALLOB_CHIPS = 0, 0, 0
                            details = ""
                        elapsed_time = time.process_time() - t
                        # display:
                        table = ([
                            ['DYNEXJOB', 'QUBITS', 'QUANTUM GATES', 'BLOCK FEE', 'ELAPSED', 'WORKERS READ', 'CIRCUITS',
                             'STEPS', 'GROUND STATE']])
                        table.append([job_id, self.num_variables, self.num_clauses, price_per_block, '',
                                      '*** WAITING FOR READS ***', '', '', ''])
                        ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f")
                        self.logger.info(f'\n{ta}\n{details}')

                else:
                    if self.logging:
                        if mainnet and debugging == False:
                            clear_output(wait=True)
                        if mainnet:
                            LOC_MIN, ENERGY_MIN, MALLOB_CHIPS, details = self.api._get_status_details_api(job_id,
                                                                                                          annealing_time,
                                                                                                          wcnf_offset=self.model.wcnf_offset,
                                                                                                          precision=self.model.precision)
                        else:
                            LOC_MIN, ENERGY_MIN, MALLOB_CHIPS = 0, 0, 0
                            details = ""
                        elapsed_time = time.process_time() - t
                        # display:
                        table = ([
                            ['DYNEXJOB', 'QUBITS', 'QUANTUM GATES', 'BLOCK FEE', 'ELAPSED', 'WORKERS READ', 'CIRCUITS',
                             'STEPS', 'GROUND STATE']])
                        table.append(
                            [job_id, self.num_variables, self.num_clauses, price_per_block, elapsed_time, cnt_workers,
                             total_chips, total_steps,
                             (lowest_energy + self.model.wcnf_offset) * self.model.precision])

                        ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f")
                        self.logger.info(f'\n{ta}\n{details}')

                        # update mallob - job running: -------------------------------------------------------------------------------------------------
                        if runupdated == False and mainnet:
                            self.api.update_job_api(job_id)
                            runupdated = True
                    time.sleep(1)

            # update mallob - job finished: -------------------------------------------------------------------------------------------------
            if mainnet:
                self.api.finish_job_api(job_id, lowest_loc, lowest_energy)
                # update_job_api(job_id, 2, self.logging, workers=cnt_workers, lowest_loc=lowest_loc, lowest_energy=lowest_energy)

            # update final output (display all workers as stopped as well):
            if cnt_workers > 0 and self.logging:
                if mainnet and debugging == False:
                    clear_output(wait=True)
                if mainnet:
                    LOC_MIN, ENERGY_MIN, MALLOB_CHIPS, details = self.api._get_status_details_api(job_id,
                                                                                                  annealing_time,
                                                                                                  all_stopped=True,
                                                                                                  wcnf_offset=self.model.wcnf_offset,
                                                                                                  precision=self.model.precision)
                else:
                    LOC_MIN, ENERGY_MIN, MALLOB_CHIPS = 0, 0, 0
                    details = ""
                elapsed_time = time.process_time() - t
                if mainnet:
                    # display:
                    table = ([
                        ['DYNEXJOB', 'QUBITS', 'QUANTUM GATES', 'BLOCK FEE', 'ELAPSED', 'WORKERS READ', 'CIRCUITS',
                         'STEPS', 'GROUND STATE']])
                    table.append(
                        [job_id, self.num_variables, self.num_clauses, price_per_block, elapsed_time, cnt_workers,
                         total_chips, total_steps, (lowest_energy + self.model.wcnf_offset) * self.model.precision])
                    ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f")
                    self.logger.info(f'\n{ta}\n{details}')

            elapsed_time = time.process_time() - t
            elapsed_time *= 100
            if self.logging:
                self.logger.info(f'[DYNEX] FINISHED READ AFTER {elapsed_time} SECONDS')

            # step 3: now parse voltages: ---------------------------------------------------------------------------------------------------

            sampleset = []
            lowest_energy = 1.7976931348623158e+308
            lowest_loc = 1.7976931348623158e+308
            total_chips = 0
            total_steps = 0
            lowest_set = []
            dimod_sample = []
            for file in files:
                if self.type == 'cnf':
                    info = file[len(self.filename) + 1:]
                    chips = -1
                    steps = -1
                    loc = 0
                    energy = 0
                # format: xxx.dnx.32.1.0.0.000000
                # jobfile chips steps loc energy
                if self.type == 'wcnf' or self.type == 'qasm':
                    info = file[len(self.filename) + 1:]
                    chips = int(info.split(".")[0])
                    steps = int(info.split(".")[1])
                    loc = int(info.split(".")[2])

                    # energy can also be non decimal:
                    if len(info.split(".")) > 4 and info.split(".")[4].isnumeric():
                        energy = float(info.split(".")[3] + "." + info.split(".")[4])
                    else:
                        energy = float(info.split(".")[3])

                total_chips = total_chips + chips
                total_steps = steps

                with open(self.filepath + file, 'r') as ffile:
                    data = ffile.read()
                    # enough data?
                    if mainnet:
                        if len(data) > 96:
                            wallet = data.split("\n")[0]
                            tmp = data.split("\n")[1]
                            voltages = tmp.split(", ")[:-1]
                        else:
                            voltages = ['NaN']  # invalid file received
                    else:  # test-net is not returning wallet
                        voltages = data.split(", ")[:-1]

                # valid result? ignore Nan values and other incorrect data
                if self.type == 'cnf':
                    if len(voltages) > 0 and voltages[0] != 'NaN' and self.num_variables == len(voltages):
                        self.dimod_assignments = {}
                        for i in range(0, len(voltages) - 8):  # REMOVE VALIDATION VARS
                            var = voltages[i]
                            if int(var) > 0:
                                self.dimod_assignments[abs(int(var))] = 1
                            else:
                                self.dimod_assignments[abs(int(var))] = 0

                if self.type in ['wcnf', 'qasm']:
                    if self.config.solver_version == 1:
                        if len(voltages) > 0 and voltages[0] != 'NaN' and self.num_variables == len(voltages):
                            sampleset.append(
                                ['sample', voltages, 'chips', chips, 'steps', steps, 'falsified softs', loc, 'energy',
                                 energy])
                            if loc < lowest_loc:
                                lowest_loc = loc
                            if energy < lowest_energy:
                                lowest_energy = energy
                                lowest_set = voltages
                            # add voltages to dimod return sampleset:
                            dimodsample = {}
                            i = 0
                            for var in range(0, self.num_variables - 8):  # REMOVE VALIDATION VARS
                                # mapped variable?
                                if var in self.var_mappings:
                                    dimodsample[self.var_mappings[var]] = 1
                                    if (float(voltages[i]) < 0):
                                        dimodsample[self.var_mappings[var]] = 0
                                else:
                                    dimodsample[i] = 1
                                    if (float(voltages[i]) < 0):
                                        dimodsample[i] = 0
                                i = i + 1

                            dimod_sample.append(dimodsample)

                        else:
                            self.logger.info(f'[DYNEX] OMITTED SOLUTION FILE: {file} - INCORRECT DATA')
                    else:
                        sampleset.append(
                            ['sample', voltages, 'chips', chips, 'steps', steps, 'falsified softs', loc, 'energy',
                             energy])
                        if loc < lowest_loc:
                            lowest_loc = loc
                        if energy < lowest_energy:
                            lowest_energy = energy
                            lowest_set = voltages
                        # add voltages to dimod return sampleset:
                        dimodsample = {}
                        i = 0
                        for var in range(0, self.num_variables):
                            # mapped variable?
                            if var in self.var_mappings:
                                dimodsample[self.var_mappings[var]] = 1
                                if (float(voltages[i]) < 0):
                                    dimodsample[self.var_mappings[var]] = 0
                            else:
                                dimodsample[i] = 1
                                if (float(voltages[i]) < 0):
                                    dimodsample[i] = 0
                            i = i + 1

                        dimod_sample.append(dimodsample)

            if self.type == 'wcnf' or self.type == 'qasm':
                sampleset.append(
                    ['sample', lowest_set, 'chips', total_chips, 'steps', total_steps, 'falsified softs', lowest_loc,
                     'energy', lowest_energy])

            elapsed_time = time.process_time() - t

            # build sample dict "assignments" with 0/1 and dimod_sampleset ------------------------------------------------------------------
            if (self.type == 'wcnf' or self.type == 'qasm') and len(lowest_set) == self.num_variables:
                sample = {}
                i = 0
                for var in self.var_mappings:
                    # _var = self.var_mappings[var]
                    sample[var] = 1
                    if (float(lowest_set[i]) < 0):
                        sample[var] = 0
                    i = i + 1
                self.assignments = sample

                # generate dimod format sampleset:
                self.dimod_assignments = dimod.SampleSet.from_samples_bqm(dimod_sample, self.bqm)

            if self.logging:
                self.logger.info("[DYNEX] SAMPLESET READY")

            # create return sampleset: ------------------------------------------------------------------------------------------------------
            sampleset_clean = []
            for sample in sampleset:
                sample_dict = _Convert(sample)
                sampleset_clean.append(sample_dict)

        except KeyboardInterrupt:
            if mainnet:
                self.api.cancel_job_api(job_id)
            self.logger.error("[DYNEX] Keyboard interrupt")
            return {'error': 'Keyboard interrupt'}

        # except Exception as e:
        #     if mainnet:
        #         self.api.cancel_job_api(job_id)
        #     self.logger.info(f"[DYNEX] Exception encountered during hadling exception: {e}")
        #     return {'error': 'Exception encountered during handling excepiton', 'details': e}

        self.sampleset = sampleset_clean

        # CQM model?
        if self.model.type_str == 'CQM':
            cqm_sample = self.model.invert(self.dimod_assignments.first.sample)
            self.dimod_assignments = dimod.SampleSet.from_samples_cqm(cqm_sample, self.model.cqm)

        # DQM model?
        elif self.model.type_str == 'DQM':
            cqm_sample = self.model.invert(self.dimod_assignments.first.sample)
            dqm_sample = {}
            for s, c in cqm_sample:
                if cqm_sample[(s, c)] == 1:
                    dqm_sample[s] = c
            self.dimod_assignments = dimod.SampleSet.from_samples(dimod.as_samples(dqm_sample), 'DISCRETE', 0)

        return self.dimod_assignments


def test():
    """
    Performs test of the dynex.ini settings. Successful completion is required to start using the sampler.
    """
    allpassed = True
    config = DynexConfig()
    config.logger.info('[DYNEX] TEST: dimod BQM construction...')

    bqm = dimod.BinaryQuadraticModel({'a': 1.5}, {('a', 'b'): -1}, 0.0, 'BINARY')
    model = BQM(bqm, logging=False)
    config.logger.info('[DYNEX] PASSED')
    config.logger.info('[DYNEX] TEST: Dynex Sampler object...')
    sampler = _DynexSampler(model, mainnet=False, logging=False, test=True, config=config)
    config.logger.info('[DYNEX] PASSED')
    config.logger.info('[DYNEX] TEST: submitting sample file...')
    worker_user = sampler.solutionuser.split(':')[0]
    worker_pass = sampler.solutionuser.split(':')[1]
    ret = sampler.upload_file_to_ftp(sampler.solutionurl[6:-1], worker_user, worker_pass,
                                     sampler.filepath + sampler.filename, '', sampler.logging)
    if ret == False:
        config.logger.error('[DYNEX] FAILED')
        raise Exception("DYNEX TEST FAILED")
    else:
        config.logger.info('[DYNEX] PASSED')
    time.sleep(1)
    config.logger.info('[DYNEX] TEST: retrieving samples...')
    try:
        files = sampler.list_files_with_text()
        config.logger.info('[DYNEX] PASSED')
    except:
        config.logger.error('[DYNEX] FAILED')
        raise Exception("DYNEX TEST FAILED")
    if allpassed:
        config.logger.info('[DYNEX] TEST RESULT: ALL TESTS PASSED')
        with open('dynex.test', 'w') as f:
            f.write('[DYNEX] TEST RESULT: ALL TESTS PASSED')
    else:
        config.logger.info('[DYNEX] TEST RESULT: ERRORS OCCURED')
    return allpassed
