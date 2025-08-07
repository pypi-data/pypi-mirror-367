<!-- # ![Rex Banner](./src/lhcb_rex/tools/figures/Rex_banner.png) -->
# ![Rex Banner](https://github.com/alexmarshallbristol/Rex-image/blob/master/Rex_banner.png?raw=true)

# Rex 

```Rex``` offers a fast emulation of the LHCb detector simulation. From truth level kinematics to reconstructed quantities and all commonly used reconstruction quality variables. 

## Table of Contents
- [About](#about)
- [Installation](#installation)
- [Usage](#usage)

## About

A full description of the tool can be found in this [📖 arXiv preprint](https://arxiv.org/abs/2507.05069/). 

[📖 Project Docs](https://lhcb-rex.docs.cern.ch/) | [💬 Mattermost Chat](https://mattermost.cern.ch/your-channel) | [📬 Developer Email](mailto:alex.marshall@bristol.ac.uk)

## Installation 

### Prerequisites  
- Python 3.9

Install with ```pip```:
```shell
pip install lhcb-rex
```

## Usage

Examples below

<details>
    <summary>Click to see an example</summary>

```python
import lhcb_rex

lhcb_rex.run(
    events=1000,
    decay="Bs0 -> mu+ mu-",
    naming_scheme="MOTHER -> DAUGHTER1 DAUGHTER2",
    decay_models="PHSP -> NA NA",
    workingDir="./Bs_mumu",
)
```

</details>

## Installation for development

```shell
git clone
uv sync
uv run pip install -e .
```

---

📬 Have questions? Reach out at [alex.marshall@bristol.ac.uk](mailto:alex.marshall@bristol.ac.uk)


### Notes for me

```/dice/users/am13743/fast_vertex_quality/graveyard```
```/dice/users/am13743/fast_vertex_quality/checkpoints/```

Relevant tags/checkpoints:
- ```21_03_2025``` - Plotting for paper draft

```shell
rm -rf dist/
uv build
uv publish
```