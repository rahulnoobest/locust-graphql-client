import time
import json
import urllib
from locust import User, events
from src.graphqlclient.graphqlclient import GraphQLClient


class MeasuredGraphQLClient(GraphQLClient):

    def execute(self, label, query, variables=None, type="graphql"):
        start_time = time.time()
        try:
            data = super().execute(query, variables)
            result = json.loads(data)
        except urllib.error.HTTPError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type=type, name=label, response_time=total_time, exception=e)
        except urllib.error.URLError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type=type, name=label, response_time=total_time, exception=e)
        except ValueError as err:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type=type, name=label, response_time=total_time, exception=err)
        else:
            total_time = int((time.time() - start_time) * 1000)
            if "errors" in result:
                events.request_failure.fire(request_type=type, name=label, response_time=total_time,
                                            exception=result["errors"])
            else:
                events.request_success.fire(request_type=type, name=label, response_time=total_time, response_length=0)
        return result


class GraphQLLocust(User):
    abstract = True

    def __init__(self, *args, **kwargs):
        super(GraphQLLocust, self).__init__(*args, **kwargs)
        self.client = MeasuredGraphQLClient(endpoint=self.host)
