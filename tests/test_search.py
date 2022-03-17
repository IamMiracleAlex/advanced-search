import json

from logger import app


def test_simple_search():
    app.testing = True
    client = app.test_client()

    res = client.get('/search/browser/philippines')

    assert len(res.json) == 8

    res = client.get('/search/IE/philippines')

    assert len(res.json) == 31


def test_advanced_search_with_operation_node():
    '''To perform a search using operation nodes'''

    app.testing = True
    client = app.test_client()

    params = {"IS": {"browser": "Chrome"}}
    params = json.dumps(params)
    response = client.get('/advanced-search/?q={}'.format(params))

    assert len(response.json) == 27


def test_advanced_search_with_negating_node():
    '''To perform a search using negating nodes'''

    app.testing = True
    client = app.test_client()

    params = {"NOT": {"IS": {"country": "Italy"}}}
    params = json.dumps(params)
    response = client.get('/advanced-search/?q={}'.format(params))
   
    assert len(response.json) == 100    


def test_advanced_search_with_grouping_node():
    '''To perform a search using grouping nodes'''

    app.testing = True
    client = app.test_client()

    params = {"OR": 
                [{"IS": {"browser": "Safari"}},
                {"IS": {"country": "Germany"}}
            ]}
    params = json.dumps(params)
    response = client.get('/advanced-search/?q={}'.format(params))

    assert len(response.json) == 21   

 
def test_advanced_search_with_all_nodes():
    '''To perform a search using all nodes'''
    
    app.testing = True
    client = app.test_client()

    params = {"NOT": 
                {"OR": 
                    [{"AND": 
                        [{"IS": {"browser": "safari"}},
                        {"IS": {"country": "Germany"}}
                    ]},
                    {"CONTAINS": {"message": "stacktrace"}}
                    ]
                }
            }
    params = json.dumps(params)
    response = client.get('/advanced-search/?q={}'.format(params))
   
    assert len(response.json) == 100    