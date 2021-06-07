# qe-qulacs

[![codecov](https://codecov.io/gh/zapatacomputing/qe-qulacs/branch/master/graph/badge.svg?token=6G6TU70MH0)](https://codecov.io/gh/zapatacomputing/qe-qulacs)

## What is it?


`qe-qulacs` is an [Orquestra](https://www.zapatacomputing.com/orquestra/) module that allows you to use [Qulacs](https://github.com/qulacs/qulacs) simulator in your Orquestra workflows.
It complies to the backend interface defined in the [`z-quantum-core`](https://github.com/zapatacomputing/z-quantum-core/blob/master/src/python/orquestra/core/interfaces/backend.py).

## Usage

### Workflow
In order to use `qe-qulacs` in your workflow, you need to add it as an `import` in your Orquestra workflow:

```yaml
imports:
- name: qe-qulacs
  type: git
  parameters:
    repository: "git@github.com:zapatacomputing/qe-qulacs.git"
    branch: "master"
```

and then add it in the `imports` argument of your `step`:

```yaml
- name: my-step
  config:
    runtime:
      language: python3
      imports: [qe-qulacs]
```

Once that is done, you can use Qulacs simulator in a step of your workflow by specifying the `backend-specs` dictionary:

```yaml
- name: my-step
  config:
    ...
  inputs:
    - backend_specs: '{"module_name": "qequlacs.simulator", "function_name": "QulacsSimulator"}'
```

You can pass additional arguments, such as `n_samples`, as parameters in the `backend-specs` dictionary.

### Task

In order to use backend in the python code you can either simply create an object:

```python
from qequlacs import QulacsSimulator
backend = QulacsSimulator()
```

or use `backend-specs` parameter to make your code work with other backends too:

```python
from zquantum.core.utils import create_object
backend_specs = {{inputs.parameters.backend-specs}}
backend = create_object(backend_specs)
```

## Development and contribution

You can find the development guidelines in the [`z-quantum-core` repository](https://github.com/zapatacomputing/z-quantum-core).
