## Introduction

```cyjax-misp-input-module``` is an input module for [MISP](https://www.misp-project.org). It can be used to ingest Cyjax indicators of compromise as MISP events and attributes.

The library is available on [Python Package Index](http://pypi.python.org/pypi/cyjax-misp-input-module).

## Install

You can install the ```cyjax-misp-input-module``` library with pip:

```
pip install --user cyjax-misp-input-module
```

## Configuration

To setup the module, you have to provide:
- Cyjax API key: the API key for the Cyjax platform API
- MISP URL: the URL to connect to MISP
- MISP API key: the API key for MISP REST API. You can find your key by clicking on Home -> REST client. Then copy
the value from `Authorization` header. 
- MISP SSL: Whether to use SSL connection to MISP server.
- MISPEvent published flag - whether the MISP events should be published by default

Then please run:

```
$HOME/.local/bin/cyjax-misp-input-module --setup

=== MISP input module for Cyjax Threat Intelligence platform ===

Please provide the Cyjax API key: g5d9fig0db5b6b7022d3a5d3c93883g4
Please provide the MISP URL: https://misp.domain.com
Please provide the MISP API key: X2QrvRBwblBbd9nGa8Z2aJHDYZFoVFFiAadolPUU
Should the MISP SSL be used? [yes/no] (default: yes): yes
Should the MISP events be published by default? [yes/no]: no
```

## Run

Please setup a cronjob to run the MISP input module every one hour:

```
crontab -e
0 * * * * $HOME/.local/bin/cyjax-misp-input-module
```

## Uninstall

To remove the MISP input module please run:

```
pip uninstall cyjax-misp-input-module
rm $HOME/.config/cyjax_misp_input.json
```