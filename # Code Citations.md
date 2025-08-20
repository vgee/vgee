# Code Citations

## License: BSD-3-Clause
https://github.com/refnx/refnx/blob/b407b80af82302bfe4ef788a7f9fd4cb409a13dc/azure-pipelines.yml.bak

```
`yaml
# Python package

```


## License: Apache-2.0
https://github.com/cryptaliagy/krait/blob/d1dbf96dedf2eb1c306cd40dec2b56cadc57d145/src/krait/templates/azure-azure-pipeline.yml.jinja2

```
`yaml
# Python package

```


## License: GPL-3.0
https://github.com/StephenRoille/project-9de3c634ca/blob/174c643f4ab83b5fc8a6b9a1b1296daa03b74fdd/README.md

```
`yaml
# Python package

```


## License: BSD-3-Clause
https://github.com/refnx/refnx/blob/b407b80af82302bfe4ef788a7f9fd4cb409a13dc/azure-pipelines.yml.bak

```
`yaml
# Python package
# Create and test a Python package on multiple Python versions.
# Add steps that analyze code, save the dist with the build record, publish to a PyPI-compatible index, and more:
# https://docs.microsoft.com/azure/devops/pipelines/languages/python

trigger:
- main

pool:
  vmImage: ubuntu-latest

strategy:
  matrix:
    Python38:
      python.version: '3.8'
    Python39:
      python.version: '3.9'
    Python310:
      python.version: '3.10'
    Python311:
      python.version: '3.11'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '$(python.version)'
  displayName: 'Use Python $(python.version)'

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    pip install flake8 black
    flake8 .
    black --check .
  displayName: 'Linting and Formatting'

- script: |
    pip install pytest pytest-azurepipelines
    pytest
  displayName: 'pytest'
```


## License: Apache-2.0
https://github.com/cryptaliagy/krait/blob/d1dbf96dedf2eb1c306cd40dec2b56cadc57d145/src/krait/templates/azure-azure-pipeline.yml.jinja2

```
`yaml
# Python package
# Create and test a Python package on multiple Python versions.
# Add steps that analyze code, save the dist with the build record, publish to a PyPI-compatible index, and more:
# https://docs.microsoft.com/azure/devops/pipelines/languages/python

trigger:
- main

pool:
  vmImage: ubuntu-latest

strategy:
  matrix:
    Python38:
      python.version: '3.8'
    Python39:
      python.version: '3.9'
    Python310:
      python.version: '3.10'
    Python311:
      python.version: '3.11'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '$(python.version)'
  displayName: 'Use Python $(python.version)'

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    pip install flake8 black
    flake8 .
    black --check .
  displayName: 'Linting and Formatting'

- script: |
    pip install pytest pytest-azurepipelines
    pytest
  displayName: 'pytest'
```


## License: GPL-3.0
https://github.com/StephenRoille/project-9de3c634ca/blob/174c643f4ab83b5fc8a6b9a1b1296daa03b74fdd/README.md

```
`yaml
# Python package
# Create and test a Python package on multiple Python versions.
# Add steps that analyze code, save the dist with the build record, publish to a PyPI-compatible index, and more:
# https://docs.microsoft.com/azure/devops/pipelines/languages/python

trigger:
- main

pool:
  vmImage: ubuntu-latest

strategy:
  matrix:
    Python38:
      python.version: '3.8'
    Python39:
      python.version: '3.9'
    Python310:
      python.version: '3.10'
    Python311:
      python.version: '3.11'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '$(python.version)'
  displayName: 'Use Python $(python.version)'

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    pip install flake8 black
    flake8 .
    black --check .
  displayName: 'Linting and Formatting'

- script: |
    pip install pytest pytest-azurepipelines
    pytest
  displayName: 'pytest'
```


## License: неизвестно
https://github.com/BeardedPlatypus/personal-website-content/blob/013c0f51fee43b2f5065f92255f2c3b6e1f37523/articles/on-ci-static-website.md

```
latest

strategy:
  matrix:
    Python38:
      python.version:
```


## License: неизвестно
https://github.com/hiryamada/notes/blob/dfd3465fb1552b051c9668b64951b83a73eff25d/AZ-400/mod06-hands-on-multiple-jobs.md

```
latest

strategy:
  matrix:
    Python38:
      python.version:
```


## License: неизвестно
https://github.com/BeardedPlatypus/personal-website-content/blob/013c0f51fee43b2f5065f92255f2c3b6e1f37523/articles/on-ci-static-website.md

```
latest

strategy:
  matrix:
    Python38:
      python.version: '3.8'
    Python39:
      python.version: '3.9'
    Python310:
      python.version: '3.10'
    Python311:
      python.version: '3.11'

steps:

```


## License: неизвестно
https://github.com/hiryamada/notes/blob/dfd3465fb1552b051c9668b64951b83a73eff25d/AZ-400/mod06-hands-on-multiple-jobs.md

```
latest

strategy:
  matrix:
    Python38:
      python.version: '3.8'
    Python39:
      python.version: '3.9'
    Python310:
      python.version: '3.10'
    Python311:
      python.version: '3.11'

steps:

```

