# Data Science Studies

A collection of notebooks concerning data science and its mathematical foundations.

## Prerequisites

- Python 3.12
- A virtual environment with the packages listed in `requirements.txt`

Conda can be used to create environments using various versions of Python.

```bash
conda create -n ds-studies python=3.12
conda activate ds-studies
```

As an alternative or in addition to the Conda environment, a virtual environment can be crated.

```bash
python -m venv venv
source venv/bin/activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

## Install TensorFlow Docker

Install the NVIDIA Container Toolkit.

see <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html>

Enable GPU support with Docker Compose.

see <https://docs.docker.com/compose/how-tos/gpu-support/>

Pull NVIDIA TensorFlow Image.

see <https://catalog.ngc.nvidia.com/orgs/nvidia/containers/tensorflow>  
see <https://docs.nvidia.com/ngc/gpu-cloud/ngc-catalog-user-guide/index.html>
