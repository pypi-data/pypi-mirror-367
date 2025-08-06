# Dynex SDK

The Dynex SDK provides a neuromorphic Ising/QUBO sampler which can be called from any Python code. Developers and
application developers already familiar with the Dimod framework, PyQUBO or the Ocean SDK will find it very easy to run
computations on the Dynex neuromorphic computing platform: The Dynex Sampler object can simply replace the default
sampler object which typically is used to run computations on, for example, the D-Wave system – without the limitations
of quantum machines. The Dynex SDK is a suite of open-source Python tools for solving hard problems with neuromorphic
computing which helps reformulate your application’s problem for solution by the Dynex computing platform. It also
handles communication between your application code and the Dynex neuromorphic computing platform automatically.

# Installation

```
pip install dynex
``` 

# Config guide

Key Features:
- Environment variable priority (ENV > config file)
- Automatic config file discovery

DynexConfig has attrs:
- solver_version : int 1 or 2 (by default equal 1)
- mainnet : bool
- retry_count : int (by default equal 5)
- config_path : str
- solver_path : str 

```python
import dynex
import dimod
from pyqubo import Array

from dynex import DynexConfig

N = 15
K = 5
numbers = [4.8097315016016315, 4.325157567810298, 2.9877429101815127,
           3.199880179616316, 0.5787939511978596, 1.2520928214246918,
           2.262867466401502, 1.2300003067401255, 2.1601079352817925,
           3.63753899583021, 4.598232793833491, 2.6215815162575646,
           3.4227134835783364, 0.28254151584552023, 4.2548151473817075]

q = Array.create('q', N, 'BINARY')
H = sum(numbers[i] * q[i] for i in range(N)) + 5.0 * (sum(q) - K) ** 2
model = H.compile()
Q, offset = model.to_qubo(index_label=True)

bqm = dimod.BinaryQuadraticModel.from_qubo(Q, offset)
config = DynexConfig(solver_version=2, mainnet=False)

model = dynex.BQM(bqm, logging=True, config=config)
sampler = dynex.DynexSampler(model, bnb=False, description='Dynex SDK test', config=config)
``` 

You can use:
```python
config = DynexConfig(
    config_path="./custom/dynex.ini",
    solver_path="./solvers/dynexcore",
    mainnet=False,
    solver_version=2
)
```
or set api&ftp params by env
```dotenv
export DYNEX_API_KEY=your-key
export DYNEX_API_SECRET=your-secret
export DYNEX_API_ENDPOINT=https://api.dynex.dev
```
