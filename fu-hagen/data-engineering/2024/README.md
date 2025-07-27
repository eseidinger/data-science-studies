# Infrastructure for the *Data Engineering for Data Science* Course

Detailed installation instructions can be found [here](https://dbis.pages.dbis-pro1.fernuni-hagen.de/docker-hadoop-cluster/).


**Contents**

- [Infrastructure for the *Data Engineering for Data Science* Course](#infrastructure-for-the-data-engineering-for-data-science-course)
  - [Quick Start](#quick-start)
  - [Update to the Latest Release](#update-to-the-latest-release)
  - [Change Log](#change-log)
    - [0.4.0 (2023-05-30)](#040-2023-05-30)
    - [0.3.3 (2023-03-31)](#033-2023-03-31)
    - [0.3.2 (2023-12-02)](#032-2023-12-02)
    - [0.3.1 (2022-12-08)](#031-2022-12-08)
    - [0.3.0 (2022-12-08)](#030-2022-12-08)
    - [0.2.1 (2022-10-13)](#021-2022-10-13)
    - [0.2.0 (2022-09-30)](#020-2022-09-30)




## Quick Start

Clone the project

```bash
git clone https://code.dbis-pro1.fernuni-hagen.de/pub-access/data-engineering-infrastructure.git \
data-engineering-infrastructure.git
```

Change to the cloned directory

```bash
cd data-engineering-infrastructure.git 
```

Checkout the current release

```bash
git checkout $(git tag | sort -V | tail -1)
```

Starting the cluster (to run in background use: `docker-compose up -d`)

```bash
docker-compose up
```

> *NOTE:* Place your files (jupyter notebooks, etc.) under the `workspace/` folder


To start only the *client-node* (Jupyter-Notebook) if the Hadoop-Cluster is not needed:

```bash
docker-compose up client-node
```

To start the cluster with an alternative configuration for limited main memory:

```bash
docker-compose -f docker-compose.yml -f docker-compose-small.yml up
```

**WebUI-URL's:**

- Jupyter-Notebook: [**127.0.0.1:8888**](http://127.0.0.1:8888)
- Hadoop Resource-Manager: [**127.0.0.1:8088**](http://127.0.0.1:8088)


## Update to the Latest Release

First stop and delete the containers of the currently used version

```bash
docker-compose down
```

Then download the new tags from the remote server

```bash
git fetch --tags
```

Finally you can switch to the latest release (tag)

```bash
git checkout $(git tag | sort -V | tail -1)
```




## Change Log

### [0.4.0](https://code.dbis-pro1.fernuni-hagen.de/pub-access/data-engineering-infrastructure/-/tree/v0.4.0) (2023-05-30)

**Improvements**

- An alternative configuration is available to use the Spark cluster on machines with 8 GB of main memory.

**Bugs**

- The Python library *six* has been updated, making stacktraces more readable (previously there were error messages from *six* in almost every stacktrace).




### [0.3.3](https://code.dbis-pro1.fernuni-hagen.de/pub-access/data-engineering-infrastructure/-/tree/v0.3.3) (2023-03-31)

**Improvements**

- Installation of *pandasql* in the *client-node*
- Memory overhead default values was added to the *spark-defaults.conf* file

**Bugs**

- A notebook with attached images failed to export to PDF using nbconvert. Therefore a preprocessor for processing notebook cells with attachments was added




### [0.3.2](https://code.dbis-pro1.fernuni-hagen.de/pub-access/data-engineering-infrastructure/-/tree/v0.3.2) (2023-12-02)

**Bugs**

- Installation of *psycopg* (PostgreSQL-driver) was incomplete in the *client-node*




### [0.3.1](https://code.dbis-pro1.fernuni-hagen.de/pub-access/data-engineering-infrastructure/-/tree/v0.3.1) (2022-12-08)

**Bugs**

- Description how to upgrade to the latest release corrected




### [0.3.0](https://code.dbis-pro1.fernuni-hagen.de/pub-access/data-engineering-infrastructure/-/tree/v0.3.0) (2022-12-08)

**Improvements**

- The following Python modules were added to the client-node (Jupyter-Notebook): *seaborn*, *psycopg* (PostgreSQL-driver), *pymongo* (MongoDB-driver), *cassandra-driver*
- Support for Docker-in-Docker (dind) within the *client-node* added
- PlantUML diagrams can be created in Jupyter-Notebooks (*client-node*)
- Notebook parameters have been modified so that the notebook server can be used remotely, e.g. with VSCode

**Bugs**

- Variable in `~/.bashrc` for the default Python version was not used in Jupyter Notebook bash cells. Python versions are now managed using *update-alternatives*




### [0.2.1](https://code.dbis-pro1.fernuni-hagen.de/pub-access/data-engineering-infrastructure/-/tree/v0.2.1) (2022-10-13)

**Bugs**

-  Variable values in the *hadoop-conf.env* file that contain other variables are now enclosed in single quotes to avoid interpretation by the host




### [0.2.0](https://code.dbis-pro1.fernuni-hagen.de/pub-access/data-engineering-infrastructure/-/tree/v0.2.0) (2022-09-30)

**Improvements**

- Support for arm64 architecture added
