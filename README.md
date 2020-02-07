Mikrokosmos
===========

**A (test) data generator and scenario simulation framework**

Mikrokosmos allows you to define and run scenarios of simulated events through its command line client, `mikro`. Scenarios are described as YAML files [...]. Simulation data can be output in multiple formats – logs, json data etc.

Mikrokosmos was designed specifically to generate test data, so most of its included functionality is geared towards this.

Installation
------------

Mikrokosmos requires Python 3.6 or higher, and is tested with PyPy3.

```bash
$ pip install --user mikrokosmos
```

Usage
-----

Generate static data from a scenario:

```bash
$ mikro gen scenario.yml
```

License
-------

Mikrokosmos is copyright © 2020 Protojour AS, and is licensed under MIT. See [LICENSE.txt](https://github.com/protojour/mikrokosmos/blob/master/LICENSE.txt) for details.
