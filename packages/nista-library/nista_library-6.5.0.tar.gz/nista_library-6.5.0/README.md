<!-- nista_library documentation master file, created by
sphinx-quickstart on Thu May 18 13:55:53 2023.
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive. -->
# Welcome to nista_library’s documentation!

## Tutorial

### Create new Poetry Project

Navigate to a folder where you want to create your project and type

```shell
poetry new my-nista-client
cd my-nista-client
```

### Add reference to your Project

Navigate to the newly created project and add the PyPI package

```shell
poetry add nista-library
```

### Your first DataPoint

In order to receive your datapoint you need a workspaceID and a dataPointId. This can be retrieved from your browser.


* Navigate to app.nista.io and login


* Browse your DataLibrary and open a DataPoint


* You can extract the information from the URL of your browser: [https://app.nista.io/workspace](https://app.nista.io/workspace)/{WORKSPACE_ID}/dashboard/datalibrary/datapoint/{DATA_POINT_ID}

```default
from data_point_client.models.get_data_request import GetDataRequest

from nista_library import KeyringNistaConnection, NistaDataPoint

connection = KeyringNistaConnection(workspace_id="YOUR_WORKSPACE_ID")

data_point_id = "DATA_POINT_ID"
data_point = NistaDataPoint(connection=connection, data_point_id=data_point_id)

request = GetDataRequest(
    window_seconds=600,
    remove_time_zone=True,
)

data_point_data = data_point.get_data_point_data(request=request, timeout=90)

if isinstance(data_point_data, list):
    print(data_point_data[0])
```

### Run and Login

Run your file in poetry’s virtual environment

```shell
$ poetry install
$ poetry run python demo.py
2021-09-02 14:51.58 [info     ] Authentication has been started.
```

In order to login your browser will be openend. If not please copy the URL from the log message your Browser and follow the Login process. If you don’t want to login for every request, please use a Keystore.

### Keystore

Once you loggedin, the library will try to store your access token in your private keystore. Next time you run your programm, it might request a password to access your keystore again to gain access to nista.io
Please take a look at [Keyring](https://pypi.org/project/keyring/) for details.

## Examples

### Show received Data in a plot

The most easy way to receive data is to adresse the Datapoint directly and Plot it.
this is a snippet from the examples project

```shell
poetry new my-nista-client
cd my-nista-client
poetry add nista-library
poetry add structlog
poetry add matplotlib
poetry add tk
```

```default
from structlog import get_logger
from data_point_client.models.get_data_request import GetDataRequest

from nista_library import NistaConnection, NistaDataPoint

from plotter import Plotter

log = get_logger()


def direct_sample(connection: NistaConnection):
    data_point_id = "DATA_POINT_ID"
    data_point = NistaDataPoint(connection=connection, data_point_id=data_point_id)

    request = GetDataRequest(
        window_seconds=600,
        remove_time_zone=True,
    )

    data_point_data = data_point.get_data_point_data(request=request, timeout=90)

    log.info("Data has been received. Plotting")
    if isinstance(data_point_data, list):
        Plotter.plot(data_point_data)
```

### List DataPoints and filter by Name

You can list all DataPoints from your Workspace by querying the API. Use Filter lambda expressions in order to reduce the list to the entries you want.

In this example we use the Name in order to find DataPoints that start with “Chiller Cooling Power Production”

```default
import matplotlib.pyplot as plt
from structlog import get_logger
from data_point_client.models.get_data_request import GetDataRequest

from nista_library import NistaConnection, NistaDataPoints

from plotter import Plotter

log = get_logger()


def filter_by_name(connection: NistaConnection):
    dataPoints = NistaDataPoints(connection=connection)
    data_point_list = list(dataPoints.get_data_point_list())

    for data_point in data_point_list:
        log.info(data_point)

    # Find Specific Data Points
    filtered_data_points = filter(
        lambda data_point: data_point.name.startswith(
            "Chiller Cooling Power Production"
        ),
        data_point_list,
    )
    for data_point in filtered_data_points:
        request = GetDataRequest(
            window_seconds=600,
            remove_time_zone=True,
        )

        data_point_data = data_point.get_data_point_data(request=request, timeout=90)

        if isinstance(data_point_data, list):
            Plotter.plot(data_point_data)
```

### Filter by Physical Quantity

In order to find DataPoints by it’s Unit or Physical Quantity the filter query can be extended to load more data for every datapoint.

```default
from typing import List
from structlog import get_logger
from data_point_client.models.get_data_request import GetDataRequest

from nista_library import NistaConnection, NistaDataPoints, NistaDataPoint

from plotter import Plotter

log = get_logger()


def filter_by_unit(connection: NistaConnection):
    dataPoints = NistaDataPoints(connection=connection)
    data_point_list: List[NistaDataPoint] = list(dataPoints.get_data_point_list())

    for data_point in data_point_list:
        log.info(data_point)

    # Find Specific Data Points
    filtered_data_points = filter(
        lambda data_point: data_point.data_point_response.store.gnista_unit.physical_quantity.startswith(
            "Energy"
        ),
        data_point_list,
    )
    for data_point in filtered_data_points:
        log.info(data_point)
        request = GetDataRequest(
            window_seconds=600,
            remove_time_zone=True,
        )

        data_point_data = data_point.get_data_point_data(request=request, timeout=90)

        if isinstance(data_point_data, list):
            Plotter.plot(
                data_point_data, data_point.data_point_response.store.gnista_unit.name
            )
```

## Links

### Website



![image](https://app.nista.io/assets/wordmark.svg)

[nista.io](https://nista.io)

### Source Code



![image](https://about.gitlab.com/images/icons/logos/slp-logo.svg)

[Gitlab](https://gitlab.com/campfiresolutions/public/nista.io-python-library)

### PyPi



![image](https://pypi.org/static/images/logo-small.2a411bc6.svg)

[PyPi.io](https://pypi.org/project/nista-library/)
