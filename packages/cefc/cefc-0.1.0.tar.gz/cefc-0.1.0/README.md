# CEfC

A *call-effect-commit* schema for safe data management Python.

This a metaprogramming framework that enables the safe execution
of Python code by tracking data modifications and commiting to them
only after functions complete their runs without errors. You can 
create fast-failing services that can rerun with new inputs from the
same uncorrupted state. 

The framework also treats exceptions-as-values, meaning that you can
check the validity of return arguments if you want, otherwise they
are cascaded throughout service calls.


## :zap: Quickstart

Install *CEfC* per `pip install cefc`. Then create and run the
following code snippet:

```python
from cefc import service

@service
def func(a: list, b: int):
    a[0] = 1
    a[0] /= b

@service
def outer_func(a: list, b:int):
    return func(a, b)

a = [1,2,3]
outer_func(a, b=0)
print(a)
```

You will see the following output, where `a` is unaffected by would-be
modifications and there is a final warning about not having handled the
division-by-zero error at any point.

![Error example](docs/error.png)


## :hammer_and_wrench: Safe types

This is a list of types whose safety is (planned to be) guaranteed 
when presented as service arguments. Note that the safety of global state 
is not guaranteed, but globals can be passed as preset arguments too.

- [x] list
- [ ] dict
- [ ] numpy array or GPU tensor
- [ ] object