# qe-qulacs

## What is it?


`qe-qulacs` is an [Orquestra](https://www.zapatacomputing.com/orquestra/) module that allows you to use [Qulacs](https://github.com/qulacs/qulacs) simulator in your Orquestra workflows.
It complies to the backend interface defined in the [`z-quantum-core`](https://github.com/zapatacomputing/z-quantum-core/blob/master/src/python/orquestra/core/interfaces/backend.py).

## Usage

### Workflow
In order to use `qe-qulacs` in your workflow, you need to add it as a resource:

```yaml
resources:
- name: qe-qulacs
  type: git
  parameters:
    url: "git@github.com:zapatacomputing/qe-qulacs.git"
    branch: "master"
```

and then import in a specific step:

```yaml
- - name: my-task
    template: template-1
    arguments:
      parameters:
      - backend-specs: "{'module_name': 'qequlacs.simulator', 'function_name': 'QulacsSimulator'}"
      - resources: [qe-qulacs]
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
