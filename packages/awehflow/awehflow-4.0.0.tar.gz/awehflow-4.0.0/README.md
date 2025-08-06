# Awehflow

![coverage report](https://gitlab.com/spatialedge/awehflow/badges/master/coverage.svg)
![pipeline status](https://gitlab.com/spatialedge/awehflow/badges/master/pipeline.svg)

Configuration based Airflow pipelines with metric logging and alerting out the box.

## Prerequisites

### Development environment
In order to develop awehflow for a given version of Airflow follow these steps
1. Install and configure miniconda
1. On Mac, if running ARM create an x86 version of conda using the snippet below
  ```bash
    ### add this to ~/.zshrc (or ~/.bashrc if you're using Bash)
    create_x86_conda_environment () {
      # create a conda environment using x86 architecture
      # first argument is environment name, all subsequent arguments will be passed to `conda create`
      # example usage: create_x86_conda_environment myenv_x86 python=3.9
      
      CONDA_SUBDIR=osx-64 conda create $@
      conda activate $2
      conda config --env --set subdir osx-64
    }
  ```
1. Define the version that you'd like to install
  ```bash
  export AIRFLOW_VERSION="2.1.4"
  ```
1. Create a conda environment for your version of Airflow, the bash below
  ```bash
  create_x86_conda_environment -n "airflow_$AIRFLOW_VERSION" "python=3.8.12"
  ```
1. Configure the AIRFLOW_HOME directory
  ```bash
  conda deactivate
  conda activate "airflow_$AIRFLOW_VERSION"
  conda env config vars set AIRFLOW_HOME="$HOME/airflow/airflow_$AIRFLOW_VERSION"
  conda deactivate
  conda activate airflow_"$AIRFLOW_VERSION"
  echo "$AIRFLOW_HOME"
  ```
1. Install airflow using `pip`
  ```bash
  conda activate airflow_$AIRFLOW_VERSION
  pip install --no-cache-dir "apache-airflow==$AIRFLOW_VERSION"
  ```
1. Install required providers
  ```bash
  conda activate airflow_$AIRFLOW_VERSION
  pip install --no-cache-dir "apache-airflow[google]==$AIRFLOW_VERSION"
  pip install --no-cache-dir "apache-airflow-providers-ssh==3.7.0"
  pip install --no-cache-dir "apache-airflow[postgres]==$AIRFLOW_VERSION"
  ```
  1. On MacOS ARM install the psycop binary
    ```bash
    pip install --no-cache-dir "psycopg2-binary==`pip list | grep -i 'psycopg2 ' | tr -s ' ' | cut -d' ' -f 2`"
    ```
1. Customisation per version
  1. For `2.2.3`
    1. force the MarkupSafe package version
      ```bash
      pip install --no-cache-dir markupsafe==2.0.1
      ```
  1. For `2.5.3`
    1. force pendulum package version
      ```bash
      pip install --no-cache-dir "pendulum==2.0.0"
      ```
    1. force Flask-Session package version
      ```bash
      pip install --no-cache-dir "Flask-Session==0.5.0"
      ```
1. Install the awehflow requirements
  ```bash
  pip install --no-cache-dir -r requirements.txt
  ```
1. Init the airflow db
  ```bash
  airflow db init
  ```

You will need the following to run this code:
  * Python 3

## Installation

```
pip install awehflow[default]
```

If you are installing on Google Cloud Composer with Airflow 1.10.2:

```
pip install awehflow[composer]
```

### Event & metric tables
Create a `postgresql` database that can be referenced via Airflow connection. In the DB create the following tables
  - Jobs data table
    ```sql
    CREATE TABLE public.jobs (
      id serial4 NOT NULL,
      run_id varchar NOT NULL,
      dag_id varchar NULL,
      "name" varchar NULL,
      project varchar NULL,
      status varchar NULL,
      engineers json NULL,
      error json NULL,
      start_time timestamptz NULL,
      end_time timestamptz NULL,
      reference_time timestamptz NULL,
      CONSTRAINT job_id_pkey PRIMARY KEY (id),
      CONSTRAINT run_id_dag_id_unique UNIQUE (run_id, dag_id)
    );
    ```

  - Task metrics table
    ```sql
    CREATE TABLE public.task_metrics (
      id serial4 NOT NULL,
      run_id varchar NULL,
      dag_id varchar NULL,
      task_id varchar NULL,
      job_name varchar NULL,
      value json NULL,
      created_time timestamptz NULL,
      reference_time timestamptz NULL,
      CONSTRAINT task_metrics_id_pkey PRIMARY KEY (id)
    );
    ```

  - Data metrics table
    ```sql
    CREATE TABLE public.data_metrics (
      id serial4 NOT NULL,
      platform varchar NULL,
      "source" varchar NULL,
      "key" varchar NULL,
      value json NULL,
      reference_time timestamptz NULL,
      CONSTRAINT data_metrics_pkey PRIMARY KEY (id),
      CONSTRAINT unique_metric UNIQUE (platform, source, key, reference_time)
    );
    ```

## Usage

Usage of `awehflow` can be broken up into two parts: bootstrapping and configuration of pipelines

### Bootstrap

In order to expose the generated pipelines (`airflow` _DAGs_) for `airflow` to pick up when scanning for _DAGs_, one has to create a `DagLoader` that points to a folder where the pipeline configuration files will be located:

```python
import os

from awehflow.alerts.slack import SlackAlerter
from awehflow.core import DagLoader
from awehflow.events.postgres import PostgresMetricsEventHandler

"""airflow doesn't pick up DAGs in files unless 
the words 'airflow' and 'DAG' features"""

configs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configs')

metrics_handler = PostgresMetricsEventHandler(jobs_table='jobs', task_metrics_table='task_metrics')

slack_alerter = SlackAlerter(channel='#airflow')

loader = DagLoader(
    project="awehflow-demo",
    configs_path=configs_path,
    event_handlers=[metrics_handler],
    alerters=[slack_alerter]
)

dags = loader.load(global_symbol_table=globals())
```

As seen in the code snippet, one can also pass in _"event handlers"_ and _"alerters"_ to perform actions on certain pipeline events and potentially alert the user of certain events on a given channel. See the sections below for more detail.
The global symbol table needs to be passed to the `loader` since `airflow` scans it for objects of type `DAG`, and then synchronises the state with its own internal state store.

\*_caveat_: `airflow` ignores `python` files that don't contain the words _"airflow"_ and _"DAG"_. It is thus advised to put those words in a comment to ensure the generated _DAGs_ get picked up when the `DagBag` is getting filled.

#### Event Handlers

As a pipeline generated using `awehflow` is running, certain events get emitted. An event handler gives the user the option of running code when these events occur.

The following events are (potentially) potentially emitted as a pipeline runs:

* `start`
* `success`
* `failure`
* `task_metric`

Existing event handlers include:

* `PostgresMetricsEventHandler`: persists pipeline metrics to a Postgres database
* `PublishToGooglePubSubEventHandler`: events get passed straight to a Google Pub/Sub topic

An `AlertsEventHandler` gets automatically added to a pipeline. Events get passed along to registered alerters.

#### Alerters

An `Alerter` is merely a class that implements an `alert` method. By default a `SlackAlerter` is configured in the `dags/PROJECT/bootstrap.py` file of an awehflow project.  awehflow supports the addition of multiple alerters, which allows success or failure events to be sent to mutliple channels

##### YAML configuration
In order to add alerts to an awehflow DAG add the following to the root space of the configuration
```YAML
alert_on:
  - 'failure' # Send out a formatted message if a task in the DAG fails. This is optional
  - 'success' # Send out a formatted message once the DAG completes successfully. This is optional
```

##### Available alerters

###### `SlackAlerter` - `awehflow.alerts.slack.SlackAlerter`
Sends an alert to a specified slack channel via the Slack webhook functionality

- Parameters
  - `channel` - The name of the channel that the alerts should be sent to
  - `slack_conn_id` - The name of the airflow connection that contains the token information, default: `slack_default`
- Connection requirements - Create a HTTP connection with the name specified for `slack_conn_id`, the required HTTP fields are:
  - `password` - The slack token issued by your admin team, which allows for the sending of messages via the slack python API


##### `GoogleChatAlerter` - `awehflow.alerts.googlechat.GoogleChatAlerter`
Sends an alert to the configured Google Chat space
- Parameters
  - `gchat_conn_id` - The name of the airflow connection that contains the GChat space information, default: `gchat_default`
- Connection requirements - Create a HTTP connection with the name specified for the `gchat_conn_id`, the requried HTTP fields are:
  - `host` - The GChat spaces URL `https://chat.googleapis.com/v1/spaces`
  - `password` - The GChat spaces key configuration information, ex `https://chat.googleapis.com/v1/spaces/SPACES_ID?key=SPACES_KEY`
    - `SPACES_ID` - Should be supplied by your GChat admin team
    - `SPACES_KEY` - Should be supplied by your GChat admin team


### Configuration
Awehflow configuration files can be written as .yml OR .hocon files either formats are supported

Shown below is sample hocon configuration file
  ```h
  {
    name: my_first_dag,
    version: 1,
    description: "This is my first dag",
    owner: The name of the owner of the DAG
    schedule: "10 0 * * *",
    start_date: 2022-01-01,
    end_date: 2022-01-01,
    catchup: true,
    concurrency: 1 // Defaults to airflow configuration
    max_active_tasks: 1 // Defaults to airflow configuration
    max_active_runs: 1 // Defaults to airflow configuration
    dagrun_timeout: None
    doc_md: The DAG documentation markdown
    access_control: None // A dict of roles that have specific permissions
    is_paused_upon_creation: None // Defaults to airflow configuration
    tags: [
      'tag one',
      'tag two'
    ],
    dag_params: { 
      /* This dict will define DAG parameters and defaulted when triggering a DAG manually with CONF,
      Values are accessible as template values {{ dag_run.conf["config_value_1"] }}
      */
      'config_value_1': 'SOME TEXT',
      'config_value_2': 1234
    },
    alert_on:[ // Whether the events alert should send a message on success OR failure
      success,
      failure
    ],
    params: { // parameter values that will be passed in to each task for rendering
      default: {
        source_folder: /tmp
      },
      production: {
        source_folder: /data
      }
    },
    default_dag_args: { //The default DAG arguments whichis also passed to each task in the dag
      retries: 1
    },
    pre_hooks: [ // Pre hook sensors are executed BEFORE the start task
      {
        id: 'pre_hook_ping_sensor'
        operator: 'airflow.sensors.bash.BashSensor'
        params: {
          bash_command: 'echo ping'
          mode: 'reschedule'
        }
      }
    ],
    dependencies: [ // Dependencies sensors are executed AFTER the start task to the DAG start time being logged
      {
        id: 'dependenciy_ping_sensor'
        operator: 'airflow.sensors.bash.BashSensor'
        params: {
          bash_command: 'echo ping'
          mode: 'reschedule'
        }
      }
    ],
    tasks: [ // The array of Tasks that defines the DAG
        {
          id: first_dummy_task, // The task ID that will be shown in the task bubble or tree
          operator: airflow.operators.dummy.DummyOperator, // The fully qualified path to the Class of the Operator
        },
        {
          id: first_bash_task, // The task ID that will be shown in the task bubble or tree
          operator: airflow.operators.bash.BashOperator, // The fully qualified path to the Class of the Operator
          params: { 
            /* 
            The dictionary of parameters that will be passed to the Operator, the "default_dag_args" dict will be merged with this.
            Any parameter of the Operator Class can be added to this dict, template rending of values depends on the specific Operator
            */
            bash_command: 'echo "Hello World"'
          },
          upstream: [ // The list of tasks that must be executed prior to this task
            first_dummy_task
          ]
        }
      ]
  }
  ```

This configuration does the following:
  - Creates a DAG called `my_first_dag`
    - Scheduled to run daily 10min past midnight
    - Catchup has been enabled to ensure all runs of the DAG since 2022-01-01 are executed
  - Pre hooks
    - Check if the command `echo ping` succeeds
  - Dependencies
    - Check if the command `echo ping` succeeds
  - Tasks
    - First run a dummy task that does nothing
    - If the dummy task succeeds, execute the bash command

## Running the tests

Tests may be run with
```bash
python -m unittest discover tests
```

or to run code coverage too:

```bash
coverage run -m unittest discover tests && coverage html
```

