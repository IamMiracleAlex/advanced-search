# Advanced Search

This implements advanced search and filters for error logs stored in the database.

This **README** file contains the instructions you will need to run this program.

## Usage
This endpoint `http://localhost:8000/advanced-search/?q=<json_tree>` accepts a search expression represented by a json tree and returns a JSON list of all records matching the search expression.

The tree has three types of inner nodes:
- grouping nodes (labelled as 'AND', 'OR')
    - a grouping node is used to combine multiple operation and control operation priorities
        - the AND node only allows a log message if it's allowed by all its children
        - the OR node only allows a log message if it's allowed by at least one of its children
    - a grouping node can have an arbitrary number of children (>1) and children can be of any type
- negating nodes (labelled as 'NOT')
    - a negating node has only one child. The child can either be a grouping node or an operation node
    - a negating node only allows a log message if it's not allowed by its child 
- operation nodes (labelled as 'IS', 'CONTAIN')
    - operation nodes are the only parents for leaf nodes. The left leaf of an operation node is a field name. The right leaf is a value
    - operation nodes allow all log messages for which the result of applying the operation on the 'field' with the 'value' is true
    
### Examples

- To perform a search using operation nodes

    ```http://localhost:5000/advanced-search/?q={"CONTAINS":{"message": "error"}}```
    - returns all records with the field "message" containing the word "error"

    ```    
        []
    ```

    ```http://localhost:5000/advanced-search/?q={"IS":{"browser": "chrome"}}```
    - returns all records with the field "browser" being exactly the word "chrome"

    ```    
        []
    ```
- To perform a search using negating nodes

    ```http://localhost:5000/advanced-search/?q={"NOT":{"IS":{"country": "Italy"}}}```
    - returns all records with the field "country" NOT exactly equal to the word "Italy"
    ```
    [
        {
            "id": 1,
            "browser": "Chrome",
            "page_url": null,
            "country": "Norway",
            "message": "Sed sagittis. Nam congue, risus semper porta volutpat, quam pede lobortis ligula, sit amet eleifend pede libero quis orci.",
            "created": "2019-08-13 00:00:00"
        },
        {
            "id": 2,
            "browser": "IE",
            "page_url": null,
            "country": "South Africa",
            "message": "Proin risus. Praesent lectus.",
            "created": "2019-04-05 00:00:00"
        },

    ...

    ]

    ```

- To perform a search using grouping nodes

    ```http://localhost:5000/advanced-search/?q={"OR":[{"IS": {"browser": "Safari"}}, {"IS": {"country": "Germany"}}]}```

    - returns all nodes where the field "browser" is exactly the word "Safari" or the field "country" is exactly the word "Germany"

    ```
    [
        {
            "id": 6,
            "browser": "Safari",
            "page_url": null,
            "country": "China",
            "message": "Integer a nibh. In quis justo.",
            "created": "2019-02-12 00:00:00"
        },
        {
            "id": 9,
            "browser": "Safari",
            "page_url": null,
            "country": "Russia",
            "message": "Nulla ac enim.",
            "created": "2019-09-06 00:00:00"
        },

        ...

    ]
    ```

- To perform a search using all nodes

    ```http://localhost:5000/advanced-search/?q={"NOT": {"OR": [{"AND": [{"IS": {"browser": "safari"}},{"IS": {"country": "Germany"}}]},{"CONTAINS": {"message": "stacktrace"}}]}}```
    - returns all records that DO NOT match one or both of these conditions:
        - the field "message" contains the word "stacktrace"
        - the field "browser" is the word "safari" AND the field "country" is the word "Germany"
    ```
    [
        {
            "id": 1,
            "browser": "Chrome",
            "page_url": null,
            "country": "Norway",
            "message": "Sed sagittis. Nam congue, risus semper porta volutpat, quam pede lobortis ligula, sit amet eleifend pede libero quis orci.",
            "created": "2019-08-13 00:00:00"
        },
        {
            "id": 2,
            "browser": "IE",
            "page_url": null,
            "country": "South Africa",
            "message": "Proin risus. Praesent lectus.",
            "created": "2019-04-05 00:00:00"
        },

        ...
    ]

    ```
## Acceptance Criteria 2 (Satisfied)
- The existing repository has been refactored using software development principles that are adequate to the size and nature of the project 
- Important updates
    - I made `/logger/` a package
    - I removed `/logger/app.py` and partly replaced by `/logger/__init__.py`
    - I added a `run.py` for running the application
    - I moved `tests/` to the root directory
    - I updated `Dockerfile` and `docker-compose.yml`
    - I updated the secret key value at `/instance/config.py/Config` -- see the `.env` for new value
    - I made use of environment variables, specifically from a `.env` file (however, I have allowed the `.env` to remain in the source code for ease of replication by the reviewer or tester )

- Old folder structure
```
├── Dockerfile
├── README.md
├── docker-compose.yml
├── logger
│   ├── app.py
│   ├── config.py
│   ├── data.json
│   ├── models
│   │   ├── __init__.py
│   │   └── logs.py
│   ├── populate_db.py
│   ├── tests
│   │   ├── __init__.py
│   │   └── test_search.py
│   └── views
│       ├── __init__.py
│       └── search.py
├── requirements.txt
├── run.sh
├── task-README.md
└── test.sh
```

- New folder structure    
```
├── Dockerfile
├── README.md
├── docker-compose.yml
├── env
├── instance
│   └── config.py
├── logger
│   ├── __init__.py
│   ├── data.json
│   ├── models
│   │   ├── __init__.py
│   │   └── logs.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── filters.py
│   │   └── helpers.py
│   └── views
│       ├── __init__.py
│       └── search.py
├── populate_db.py
├── requirements.txt
├── run.py
├── run.sh
├── task-README.md
├── test.sh
└── tests
    ├── __init__.py
    └── test_search.py
```

- Sources:
    - https://github.com/jamescurtin/demo-cookiecutter-flask
    - https://flask.palletsprojects.com/en/2.0.x/patterns/packages/
    - https://www.youtube.com/watch?v=44PvX0Yv368
    - https://github.com/pallets/flask/tree/main/examples/tutorial
    - https://itnext.io/flask-project-structure-the-right-choice-to-start-4553740fad98


## Additions
For development simplicity, I have modified the docker and docker-compose files to:
- Match the new folder structure
- Add Flask hot reload capabilities
-  Add ability to get code printed to the console

I have also added tests cases that covers grouping nodes, negating nodes, operation nodes and all nodes combined. Please see `tests/test_search.py` for the test cases.
The section **"Utilities"** below shows how the test can be run.

I have also added a complete documentation of changes and additions to the `task-README.md` (you are here already)

## Utilities
Make sure you have a recent version of docker and docker-compose installed before running the utilities.
- test.sh: runs tests with pytest.
- run.sh: runs a flask development server on port 5000. (e.g. http://localhost:5000/search/chrome/philippines (may vary depending on your docker installation))
 
---