# PARSE: Physical Attribute Representativity and Stationarity Evaluator

## General information

PARSE is an open source package for representativity analysis of 3D binary images. It aims at representativity analysis for different scalar and vector metrics. Using PARSE library, one can estimate determenistic and statistical representative elementary volumes (dREV and sREV) for these metrics. Stationarity analysis and comparison of different images using vector metrics are also possible.

Currently, we provide the following metrics for REV analysis:
- Porosity.
- Permeability.
- Euler density.
- Correlation functions (two-point probabilty $S_2$, lineal path function $L_2$, cluster function $C_2$, surface-surface function $F_{ss}$, surface-void function  $F_{sv}$, pore-size function $P$,
chord length function $p$).
- Pore-network model characterstics (pore and throat numbers, pore and throat radii, connectivity, mean pore and throat radii, mean connectivity).
- Persistence diagrams.

## Prerequisites

Python 3.x and Julia 1.x with packages StatsBase.jl, LinearAlgebra.jl, CorrelationFunctions.jl (version=0.11.0)
and EulerCharacteristic.jl should be installed.

## Installation

To install the latest PyPI release as a library run

```
python3 -m pip install revanalyzer
```

or you can clone this repository and run from local folder

```
python3 -m pip install .
```

## Documentation
	
Documentation is available here on
[GitHub Pages](https://fatimp.github.io/REVAnalyzer/index.html).

To build the documentation locally clone this repository, then read /docs/README.md

## Tutorials

Numerous Jupiter notebooks with examples which show the functionality of PARSE library are available here:
-  [REV analysis for porosity](https://github.com/fatimp/REVAnalyzer/blob/main/examples/REV_porosity.ipynb)
-  [REV analysis for permeability](https://github.com/fatimp/REVAnalyzer/blob/main/examples/REV_permeability.ipynb)
-  [REV analysis for Euler density](https://github.com/fatimp/REVAnalyzer/blob/main/examples/REV_Euler.ipynb)
-  [REV analysis for correlation functions](https://github.com/fatimp/REVAnalyzer/blob/main/examples/REV_CF.ipynb)
-  [REV analysis for pore-network model characteristics](https://github.com/fatimp/REVAnalyzer/blob/main/examples/REV_PNM_characteristics.ipynb)
-  [REV analysis for persistence diagrams](https://github.com/fatimp/REVAnalyzer/blob/main/examples/REV_PD.ipynb)
-  [Comparison of two images using vector metric](https://github.com/fatimp/REVAnalyzer/blob/main/examples/image_compare.ipynb)
-  [Stationarity analysis](https://github.com/fatimp/REVAnalyzer/blob/main/examples/stationarity_analysis.ipynb)

## Describing scientific papers

Mathematical backgound for REV analysis, description of metrics used in 'REVAnalyzer' and application evamples with real 
porous image data:

[Andrey S. Zubov, Aleksey N. Khlyupin, Marina V. Karsanina, Kirill M. Gerke (2024). En search for representative elementary volume (REV) within heterogeneous materials: A survey of scalar and vector metrics using porous media as an example. Advances in Water Resources, 19, 104762.](https://www.sciencedirect.com/science/article/abs/pii/S0309170824001490)

## Authors

Andrey S. Zubov, Center for Computational Physics, Landau School for Physics and Research, Moscow Institute of Physics and Technology.
