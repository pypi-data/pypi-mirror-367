## neurons_metrics_package * NeuronsMemoryTestPipeline

## Summary
This package contains three subpackages: 
1. qa: QA_modules.py
2. frt_metrics
    - frt score calculation modules: FRT_metric.py
3. mrt_metrics
    - free memory recall text recognition: MRT_text_processing.py
    - ad recognition / brand recognition score computation modules: MRT_free_recall_metric.py

Each section is the alone standing computational package that provides scores for the selected metrics.

## Installation

Install the latest package

```
!pip install NeuronsMemoryTestPipeline
```

If the above Installation Process is not working, consider to use:

```
python3 -m pip install NeuronsMemoryTestPipeline


```

## Used Libraries:
python = "^3.8"
fuzzywuzzy = "*"
google_cloud_aiplatform = "*"
matplotlib = "*"
numpy = "*"
pandas = "*"
protobuf = "*"
scikit_learn = "*"
scipy = "*"
seaborn = "*"
setuptools = "*"
torch = "*"
tqdm = "*"
transformers = "*"
vertexai = "*"


## Authors
Irina White (i.white@neuronsinc.com) and Theo Sell (t.sell@neuronsinc.com)


## Project status
Project is under continuous update and monitoring.
