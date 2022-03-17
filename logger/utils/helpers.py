import inspect
from functools import lru_cache

from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm.attributes import QueryableAttribute


grouping_nodes = ['AND', 'OR']
negating_nodes = ['NOT']
operation_nodes = ['IS', 'CONTAINS', 'EQ', 'ILIKE', 'LIKE', 'CONTAIN', 'IN', 'NOT_IN', 'NOT_LIKE', 'EQUALS']


@lru_cache()
def primary_key_names(model):
    """Returns all the primary keys for a model."""
    return [key for key, field in inspect.getmembers(model)
            if isinstance(field, QueryableAttribute)
            and hasattr(field, 'property')
            and isinstance(field.property, ColumnProperty)
            and field.property.columns[0].primary_key]


def session_query(session, model):
    """Returns a SQLAlchemy query object for the specified `model`.

    If `model` has a ``query`` attribute already, ``model.query`` will be
    returned. If the ``query`` attribute is callable ``model.query()`` will be
    returned instead.

    If `model` has no such attribute, a query based on `session` will be
    created and returned.

    """
    if hasattr(model, 'query'):
        if callable(model.query):
            query = model.query()
        else:
            query = model.query
        if hasattr(query, 'filter'):
            return query
    return session.query(model)



def extract_list(l):
    '''
    Needed by `:func: extract()` to complete the transformation of data. 
    This handles the special case where dict value is a list
    '''
    if isinstance(l, list):
        for i in l:
            if isinstance(i, list):
                extract_list(i)
            elif isinstance(i, dict):
                extract(i)  


def extract(data):
    ''' 
    `data` can be a `dict` of lists and dicts together, this
    function recursively transforms the data in the format {'fieldname': <data>, 'op': <op>, 'val': <val>}
    for operation nodes and retains the format for negation and grouping nodes. 
    '''

    for key, value in list(data.items()):
        if key in operation_nodes:
            data.update({
                'name': next(iter(value)),
                'op': key.lower(),
                'val': next(iter(value.values()))
            })
            data.pop(key)

        # make keys small letter
        if key in negating_nodes or key in grouping_nodes:
            data[key.lower()] = data.pop(key)

        if isinstance(value, dict):
            extract(value)
        else:
            extract_list(value)
    return data


def cleanup(data):
    '''
    Presents data in an acceptable format for ``search`` function - 
    The function `extract()` sometimes returns data in the form {'key' {'key: 'value'}}
    In such cases, this function transforms it to [{'key' [{'key: 'value'}]}]
    '''
    
    extracted_data = extract(data)
    for k, v in extracted_data.items():
        if isinstance(v, dict):
            extracted_data[k] = [v]
    return [extracted_data]        