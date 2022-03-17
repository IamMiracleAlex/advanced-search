import inspect
from http.client import BAD_REQUEST

from sqlalchemy import and_, or_, not_

from .helpers import primary_key_names, session_query


class ComparisonToNull(Exception):
    """Raised when a client attempts to use a filter object that compares a
    resource's attribute to ``NULL`` using the ``==`` operator.

    """
    pass


class UnknownField(Exception):
    """Raised when the user attempts to reference a field that does not
    exist on a model in a search.

    """

    def __init__(self, field):

        #: The name of the unknown attribute.
        self.field = field


class BadRequest(Exception):
    http_code = BAD_REQUEST

    def __init__(self, cause=None, details=None):
        self.cause = cause
        self.details = details



#: The mapping from operator name (as accepted by the search method) to a
#: function which returns the SQLAlchemy expression corresponding to that
#: operator.
#:
#: Each of these functions accepts either one, two, or three arguments. The
#: first argument is the field object on which to apply the operator. The
#: second argument, where it exists, is either the second argument to the
#: operator or a dictionary as described below. The third argument, where it
#: exists, is the name of the field.
#:
#: For functions that accept three arguments, the second argument may be a
#: dictionary containing ``'name'``, ``'op'``, and ``'val'`` mappings so that
#: :func:`create_operation` may be applied recursively. For more information
#: and examples, see :ref:`search`.
#:
#: Some operations have multiple names. For example, the equality operation can
#: be described by the strings  ``'eq'``, ``'equals'``, etc.
OPERATORS = {
    'eq': lambda f, a: f == a,
    'is': lambda f, a: f == a,
    'contains': lambda f, a: f.ilike(a),
    'contain': lambda f, a: f.ilike(a),
    'ilike': lambda f, a: f.ilike(a),
    'like': lambda f, a: f.like(a),
    'not_like': lambda f, a: ~f.like(a),
    'in': lambda f, a: f.in_(a),
    'not_in': lambda f, a: ~f.in_(a),
}


class Filter(object):
    """Represents a filter to apply to a SQLAlchemy query object.

    A filter can be, for example, a comparison operator applied to a field of a
    model and a value or a comparison applied to two fields of the same
    model. For more information on possible filters, see :ref:`search`.

    `fieldname` is the name of the field of a model which will be on the
    left side of the operator.

    `operator` is the string representation of an operator to apply. The
    full list of recognized operators can be found above.

    If `argument` is specified, it is the value to place on the right side
    of the operator. If `otherfield` is specified, that field on the model
    will be placed on the right side of the operator.

    .. admonition:: About `argument` and `otherfield`

       Some operators don't need either argument and some need exactly one.
       However, this constructor will not raise any errors or otherwise
       inform you of which situation you are in; it is basically just a
       named tuple. Calling code must handle errors caused by missing
       required arguments.

    """

    def __init__(self, fieldname, operator, argument=None, otherfield=None):
        self.fieldname = fieldname
        self.operator = operator
        self.argument = argument
        self.otherfield = otherfield


    @staticmethod
    def from_dictionary(model, dictionary):
        """Returns a new :class:`Filter` object with arguments parsed from
        `dictionary`.

        `dictionary` is a dictionary of the form::

            {'name': 'age', 'op': 'lt', 'val': 20}

        
        where ``dictionary['name']`` is the name of the field of the model on
        which to apply the operator, ``dictionary['op']`` is the name of the
        operator to apply, ``dictionary['val']`` is the value on the right to
        which the operator will be applied.

        'dictionary' may also be an arbitrary Boolean formula consisting of
        dictionaries such as these. For example::

            {'or':
                 [{'and':
                       [dict(name='name', op='like', val='%y%'),
                        dict(name='age', op='ge', val=10)]},
                  dict(name='name', op='eq', val='John')
                  ]
             }

        This method raises :exc:`UnknownField` if ``dictionary['name']``
        does not refer to an attribute of `model`.

        """
        # If there are no ANDs, NOTs or ORs, we are in the base case of the
        # recursion.
       
        if 'or' not in dictionary and 'and' not in dictionary and 'not' not in dictionary:
            fieldname = dictionary.get('name')
            if not hasattr(model, fieldname):
                raise UnknownField(fieldname)
            operator = dictionary.get('op')
            otherfield = dictionary.get('field')
            argument = dictionary.get('val')
           
            return Filter(fieldname, operator, argument, otherfield)
        # For the sake of brevity, rename this method.
        from_dict = Filter.from_dictionary
        # If there is an OR, NOT or an AND in the dictionary, recurse on the
        # provided list of filters.

        if 'or' in dictionary:
            subfilters = dictionary.get('or')
            return DisjunctionFilter(*[from_dict(model, filter_)
                                       for filter_ in subfilters])
        elif 'not' in dictionary:
            subfilters = dictionary.get('not')
            return NegationFilter(*[from_dict(model, filter_)
                                       for filter_ in subfilters])
        else:
            subfilters = dictionary.get('and')
            return ConjunctionFilter(*[from_dict(model, filter_)
                                       for filter_ in subfilters])


class JunctionFilter(Filter):
    """A conjunction or disjunction of other filters.

    `subfilters` is a tuple of :class:`Filter` objects.

    """

    def __init__(self, *subfilters):
        self.subfilters = subfilters

    def __iter__(self):
        return iter(self.subfilters)


class ConjunctionFilter(JunctionFilter):
    """A conjunction of other filters."""


class DisjunctionFilter(JunctionFilter):
    """A disjunction of other filters."""


class NegationFilter(JunctionFilter):
    """A negation of other filters."""


def create_operation(model, fieldname, operator, argument):
    """Translates an operation described as a string to a valid SQLAlchemy
    query parameter using a field of the specified model.

    More specifically, this translates the string representation of an
    operation, for example ``'eq'``, to an expression corresponding to a
    SQLAlchemy expression, ``field == argument``. The recognized operators
    are given by the keys of :data:`OPERATORS`. For more information on
    recognized search operators, see OPERATORS above:.

    `model` is an instance of a SQLAlchemy declarative model being
    searched.

    `fieldname` is the name of the field of `model` to which the operation
    will be applied as part of the search.

    `operation` is a string representating the operation which will be
     executed between the field and the argument received. For example,
     ``'contains'``, ``'is'``, ``'like'``, ``'in'`` etc.

    `argument` is the argument to which to apply the `operator`.

    This function raises the following errors:
    * :exc:`KeyError` if the `operator` is unknown (that is, not in
      :data:`OPERATORS`)
    * :exc:`TypeError` if an incorrect number of arguments are provided for
      the operation (for example, if `operation` is `'=='` but no
      `argument` is provided)
    * :exc:`AttributeError` if no column with name `fieldname` or
      `relation` exists on `model`

    """
    # raises KeyError if operator not in OPERATORS
    opfunc = OPERATORS[operator]
    numargs = len(inspect.getfullargspec(opfunc).args)
    # raises AttributeError if `fieldname` does not exist
    field = getattr(model, fieldname)
    # each of these will raise a TypeError if the wrong number of argments
    # is supplied to `opfunc`.
    if numargs == 1:
        return opfunc(field)
    if argument is None:
        msg = ('Cannot compare a value to NULL.')
        raise ComparisonToNull(msg)
    if numargs == 2:
        return opfunc(field, argument)
    return opfunc(field, argument, fieldname)


def create_filter(model, filt):
    """Returns the operation on `model` specified by the provided filter.

    `filt` is an instance of the :class:`Filter` class.

    Raises one of :exc:`AttributeError`, :exc:`KeyError`, or
    :exc:`TypeError` if there is a problem creating the query.
    """
    # If the filter is not a conjunction, negation or a disjunction, simply proceed
    # as normal.
    if not isinstance(filt, JunctionFilter):
        fname = filt.fieldname
        val = filt.argument
        # get the other field to which to compare, if it exists
        if filt.otherfield:
            val = getattr(model, filt.otherfield)
        # for the sake of brevity...
        return create_operation(model, fname, filt.operator, val)
    # Otherwise, if this filter is a conjunction, disjunction or a negation, make
    # sure to apply the appropriate filter operation.

    if isinstance(filt, ConjunctionFilter):
        return and_(create_filter(model, f) for f in filt)
    if isinstance(filt, DisjunctionFilter):    
        return or_(create_filter(model, f) for f in filt)
    if isinstance(filt, NegationFilter):
        return not_(*[create_filter(model, f) for f in filt])


def search(session, model, filters=None):
    """Returns a SQLAlchemy query instance with the specified parameters.

    Each instance in the returned query meet the requirements specified by
    ``filters``.

    This function returns a single instance of the model matching the search
    parameters.

    `model` is the SQLAlchemy model on which to create a query.

    Raises :exc:`UnknownField` if one of the named fields given in one
    of the `filters` does not exist on the `model`.

    Raises one of :exc:`AttributeError`, :exc:`KeyError`, or :exc:`TypeError`
    if there is a problem creating the query.

    """
   
    query = session_query(session, model)

    try:
        # Filter the query.
        filters = [Filter.from_dictionary(model, f) for f in filters]

        # This function call may raise an exception.
        filters = [create_filter(model, f) for f in filters]
    except UnknownField as e:
        raise BadRequest(cause=e, details=f'Invalid filter object: No such field "{e.field}"') from e
    except Exception as e:
        raise BadRequest(cause=e, details='Unable to construct query') from e

    query = query.filter(*filters)

    # Order the query order by primary
    pks = primary_key_names(model)
    pk_order = (getattr(model, field).asc() for field in pks)
    query = query.order_by(*pk_order)

    return query
