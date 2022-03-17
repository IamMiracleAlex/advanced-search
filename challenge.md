# Welcome to the Backend Engineer Task!

This **README** file contains the instructions you will need to complete your task in the form of a User Story – the format regularly used by Hotjar engineers in our weekly sprints.

#### Instructions

- This master branch already contains code which you will use for your task. Please add any new code to a new feature branch. When you’re done with the task, please submit a GitLab merge request to master.

- If you cannot satisfy all the acceptance criteria within the given timeframe, simply prioritize what you feel is important and mention what you have excluded and why in your README file (*task-README.md*).

- For the parts of the task which you feel are unclear, we encourage you to make your own assumptions as long as they are documented in your README file  (*task-README.md*). However, if you have a question or concern that is blocking you from completing the work, please reach out to us via email.

A week after your task start date, a Hotjar engineer will review your merge request and you will receive an email within 48 hours notifying you of the next steps. 

---

### User Story

As a Hotjar user, I want to be able to search for error logs using advanced filters.

#### Background

The objective of this user story is to implement an API endpoint for an existing log storage service written in Python.

Error logs are stored in a database table with the following structure:


| Field name | Type     |
|------------|----------|
| id         | Integer  |
| created    | DateTime |
| browser    | String   |
| page_url   | String   |
| country    | String   |
| message    | String   |

An **endpoint**, allowing for searches by browser or country, already exists.

#### Acceptance Criteria
- ##### Acceptance Criteria 1
    - The functionality must be implemented as an endpoint separate from the existing simple search endpoint.
    - The endpoint must accept a search expression represented by a json tree 
        - The tree has three types of inner nodes:
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
    - Search tree examples:
        - ```{"CONTAINS":{"message": "error"}}```
            - returns all records with the field "message" containing the word "error"
        - ```{"IS":{"browser": "chrome"}}```
            - returns all records with the field "browser" being exactly the word "chrome"
        - ```{"NOT":{"IS":{"country": "Italy"}}}```  
            - returns all records with the field "country" NOT exactly equal to the word "Italy"
        - ```{"NOT": {"OR": [{"AND": [{"IS": {"browser": "safari"}},{"IS": {"country": "Germany"}}]},{"CONTAINS": {"message": "stacktrace"}}]}}```
            - returns all records that DO NOT match one or both of these conditions:
                - the field "message" contains the word "stacktrace"
                - the field "browser" is the word "safari" AND the field "country" is the word "Germany"
    - The endpoint must return a JSON list of all records matching the search expression.
- ##### Acceptance Criteria 2
    - The existing repository must be refactored using software development principles that are adequate to the size and nature of the project 

#### Important Notes
- Solutions and future enhancements which would require too much time to be implemented can be described in your README file (*task-README.md*) instead.
- In addition to Python, any other technologies may be used to complete the task as long as choices can be justified.

#### Utilities
Make sure you have a recent version of docker and docker-compose installed before running the utilities.
- test.sh: runs tests with pytest.
- run.sh: runs a flask development server on port 5000. (e.g. http://localhost:5000/search/chrome/philippines (may vary depending on your docker installation))
 
---

### Good luck!