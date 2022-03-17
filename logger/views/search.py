import json

from flask import request

from flask_restful import Resource

from logger.utils.filters import search
from logger.utils.helpers import cleanup


class LogSimpleSearch(Resource):

    def get(self, browser, country):
        """ Simple search endpoint that returns log messages. """

        from logger import db

        statement = """select * from log where browser ilike '%s' or country ilike '%s'""" % (browser, country)

        ret_value = []
        for r in db.engine.execute(statement):
            log_as_dict = dict(r)
            log_as_dict['created'] = str(log_as_dict['created'])
            ret_value.append(log_as_dict)

        return ret_value


class LogAdvancedSearch(Resource):

    def get(self):
        """ 
        Advanced search endpoint that returns log messages. 
        GET: /advanced-search/?q=<query>
        """

        from logger import db
        from logger.models.logs import Log

        params = request.args.get('q')

        result  = []
        if params:
            params = json.loads(params)
            filters = cleanup(params)
            query = search(db.session, Log, filters=filters)

            for log in query.all():
                result.append(dict(
                    id=log.id,
                    browser=log.browser,
                    page_url=log.page_url,
                    country=log.country,
                    message=log.message,
                    created=str(log.created)
                ))
        
        return result