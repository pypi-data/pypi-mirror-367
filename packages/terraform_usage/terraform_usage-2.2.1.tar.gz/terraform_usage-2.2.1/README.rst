===================
**terraform_usage**
===================

Overview
--------

A Python module to call the Terraform Cloud API and retrieve data for total and applied Runs of Workspaces.  

> **CAUTION!** This may take a while to run if the Organization has a large number of Workspaces and / or Runs.

Usage
-----

Installation:

.. code-block:: BASH

   pip3 install terraform_usage
   # or
   python3 -m pip install terraform_usage

Bash:

.. code-block:: BASH

   python </path/to>/terraform_usage -o <organization> -t <token> -k <keyword> -f <filename> -s <start_date> -e <end_date> -m <mode> -u <api_url> -p <page_size> -d <delay>

Python:

.. code-block:: PYTHON

   import terraform_usage as tfu
   workspaces = tfu.list_workspaces(
      <organization>,
      <token>,
      <keyword>,
      <api_url>,
      <page_size>,
      <delay>
   )
   runs = tfu.analyze_runs(
      workspaces,
      <token>,
      <start_date>,
      <end_date>,
      <mode>,
      <api_url>,
      <page_size>,
      <delay>
   )
   create_csv(
      [run.values() for run in runs],
      <filename>,
      <mode>
   )

Execution example:

.. code-block:: BASH

   python </path/to>/terraform_usage -o abdahmad -t $TFE_TOKEN -k "*abdahmad-*" -m advanced -f abdahmad.csv -s 2023-11-01 -e 2023-11-30

   Run parameters:
   Organization: abdahmad
   Keyword: *abdahmad-*
   Filename: abdahmad.csv
   Start date: 2023-11-01
   End date: 2023-11-30
   Mode: advanced
   API URL: https://app.terraform.io/api/v2
   Page size: 50
   Delay: 1.0
   -------
   Getting page 1 of Workspaces.
   Found 3 Workspaces.
   Getting Run data for Workspace ids-aws-abdahmad-dev.
   Getting page 1 of Runs.
   Getting Run data for Workspace ids-aws-abdahmad-prod.
   Getting page 1 of Runs.
   Getting Run data for Workspace ids-aws-abdahmad-test.
   Getting page 1 of Runs.
   Creating CSV file abdahmad.csv.
   Writing data to abdahmad.csv.
    
Output in CSV file example:

.. code-block:: TXT

   workspace,all_runs,successful_applies,total_time
   abdahmad-dev,4,0,53
   abdahmad-prod,0,0,0
   abdahmad-test,0,0,0

Execution Modes
---------------

- basic
    - Function
        - Get total number of Runs and successful Applies for all time.
    - Available filters
        - Workspace name pattern
    - Pros and cons
        - Faster execution
        - Less details

- advanced
    - Function
        - Get total number of Runs, successful Applies, and total Run time.
    - Available filters
        - Workspace name pattern
        - Start date
        - End date
    - Pros and cons
        - Potentially slower execution for a large number of Workspaces and Runs.
        - More details

Arguments
---------

- organization - Terraform Cloud Organization name. Required.
- token - Terraform Cloud API token. Required.
- keyword - Workspace name keyword to filter by. Default is "all".
- filename - CSV filename to save the output data to. Default is "report.csv".
- start_date - Start date for Run lookups. Default is "all".
- end_date - End date for Run lookups. Default is "all".
- mode - Execution mode ("basic" or "advanced"). Default is "basic".
- api_url - Terraform Cloud API URL. Default is "https://app.terraform.io/api/v2".
- page_size - Number of items per page. Default is 50.
- delay - Delay (in seconds) between API calls. Default is 1.0.

Error Handling
--------------

- Error: Skipping run due to missing attribute(s).
    - A Run is missing a timestamp for a status. Normally caused by Runs stuck in Pending state, which should be discarded if they aren't meant to complete, successfully or otherwise.
- Error: One or more Python exceptions.
    - Multiple possible causes. One of the most common is due to the script hitting the Terraform Cloud API rate limit (30 requests per second). There is a safeguard that slows down execution to avoid this.

API Documentation
-----------------

https://developer.hashicorp.com/terraform/cloud-docs/api-docs

New Features
------------

- Added Workspace resource listing.

Create Python code (*execute_tfu.py*):

.. code-block:: PYTHON

   import os
   import terraform_usage as tfu
   from pprint import pprint as pp
   resources = tfu.list_resources(
      "<workspace_id>",
      os.environ['TFE_TOKEN'],
      os.environ['TFE_URL'],
      20,
      1
   )
    pp(resources)

Set environment variables and execute:

.. code-block:: BASH

   export TFE_TOKEN="<tfe-token>"
   export TFE_URL="https://app.terraform.io/api/v2"

   python3 execute_tfu.py
