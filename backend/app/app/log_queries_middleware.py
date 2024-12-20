import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class QueryCountMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        num_queries = len(connection.queries)
        logger.info(f"{request.path} executed {num_queries} database queries.")
        return response
