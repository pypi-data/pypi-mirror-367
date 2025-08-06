# Description

`processview` Toolkit for workflow processes supervision.

When processing several datasets within the same workflow / orange instance user can quickly be confused about
what has been process or not and what is currently processing. To ease comprehension and get a state of processes and datasets we can add a 'process view' widget to orange-canvas as in the following screenshot:

![processview example](https://gitlab.esrf.fr/workflow/processview/-/raw/master/doc/img/explaining_processview.png?inline=false)

Processes must inherit from processview `SuperviseProcess` class. And datasets from `Dataset` class. Then you must notify the manager evolution of the dataset vs process states.

# Installation

``` python
pip install processview[full]
```
