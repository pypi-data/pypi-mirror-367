# For the full documentation, see [readthedocs](https://elabforms.readthedocs.io)
# elabforms

A set of tools to create and manage standardized forms for eLabFTW.

---

## Create a virtual environment

```bash
python3 -m venv myenv
source myenv/bin/activate
````

---

## Installation

You will need `template_part` files to generate the final template.
These files are located in the `elabforms_INTProjects` and `elabforms_BIDSMetadata` repositories — private Git repositories at NIT.

**Reminder:**
A `template_part` is an elabform with a single `groupfield`.
You need to create a `template_file_list.csv` file listing the parts you want to concatenate, **in this order**, for example:

```csv
template_part_Example_1.json
template_part_Example_2.json
...
template_part_Example_N.json
```

Each line corresponds to one template part file.

---

## User mode

Install the package from Test PyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple elabforms==0.0.6
```

### Usage

* Test the installation by running:

  ```bash
  eform --help
  ```

* To create a new form, run:

  ```bash
  eform template_file_list.csv template_generated.json
  ```

```

## Example
Assuming you have a file `template_file_list.csv` with the following content:
```csv
template_part_Example_1.json
template_part_Example_2.json
```

This will generate the file `template_generated.json` which will contain the content of the two files concatenated together.


```

 let 's template_part_Example_1.json` ![GENERIC_BIDS_SESSION](docs/GNERIC_BIDS_SESSION.png) 

with content:
```json
{
    "elabftw": {
        "extra_fields_groups": [
            {
                "id": 1,
                "name": "GENERIC_BIDS_SESSION"
            }
        ]
    },
    "extra_fields": {
        "session_id": {
            "type": "text",
            "value": "",
            "group_id": 1,
            "position": 0,
            "required": true,
            "description": "Ex: '01 or predrug or 20231206'"
        },
        "Session duration": {
            "type": "number",
            "value": "",
            "group_id": 1,
            "position": 3,
            "description": "The duration of the session [in minutes]",
            "blank_value_on_duplicate": true
        }
    }
}
```
and `template_part_Example_2.json` ![GENERIC_BIDS_SESSION](docs/RUN_BIDS.png),
with the following content:
```json
{
  "elabftw": {
    "display_main_text": true,
    "extra_fields_groups": [
      {
        "id": 2,
        "name": "Run "
      }
    ]
  },
  "extra_fields": {
    "TaskName": {
      "type": "text",

      "group_id": 2,
      "position": 0,

      "description": "Code name of the task (no space and only alphanumeric characters).\n Ex: 'rest or facesnback or headnodding'"
    },
    "RunNumber": {
      "type": "text",
      "value": "",
      "group_id": 2,
      "position": 2
    },
    "StartTime": {
      "type": "text",
      "value": "",
      "group_id": 2
    },
    "RunComment": {
      "type": "text",
      "value": "",
      "group_id": 2,
      "position": 3,
      "description": "Comment about the subject behavior during the run."
    },
    "TaskDescription": {
      "type": "text",
      "value": "  ",
      "group_id": 2,
      "position": 1,
      "description": "Description of the task"
    }
  }
}
```

This will generate the following file " template_generated.json" ![GENERIC_BIDS_SESSION](docs/template_generated.png),

which will contain the content of the two files `template_part_Example_1.json` and `template_part_Example_2.json` concatenated together.
```json
{
    "elabftw": {
        "extra_fields_groups": [
            {
                "id": 1,
                "name": "GENERIC_BIDS_SESSION"
            },
            {
                "id": 2,
                "name": "Run "
            }
        ]
    },
    "extra_fields": {
        "session_id": {
            "type": "text",
            "value": "",
            "group_id": 1,
            "position": 0,
            "required": true,
            "description": "Ex: '01 or predrug or 20231206'"
        },
        "Session duration": {
            "type": "number",
            "value": "91",
            "group_id": 1,
            "position": "3",
            "description": "The duration of the session [in minutes]",
            "blank_value_on_duplicate": true
        },
        "TaskName": {
            "type": "text",
            "group_id": 2,
            "position": 0,
            "description": "Code name of the task (no space and only alphanumeric characters).\n Ex: 'rest or facesnback or headnodding'"
        },
        "RunNumber": {
            "type": "text",
            "value": "",
            "group_id": 2,
            "position": 2
        },
        "StartTime": {
            "type": "text",
            "value": "",
            "group_id": 2
        },
        "RunComment": {
            "type": "text",
            "value": "",
            "group_id": 2,
            "position": 3,
            "description": "Comment about the subject behavior during the run."
        },
        "TaskDescription": {
            "type": "text",
            "value": "  ",
            "group_id": 2,
            "position": 1,
            "description": "Description of the task"
        }
    }
}
```bash
