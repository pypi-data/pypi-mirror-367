import asyncio

import requests
from graphql import parse, print_ast
from graphql.error import GraphQLSyntaxError
from requests.exceptions import RequestException


class GraphQLExecutor:
    def __init__(self, graphql_endpoint, debug):
        self.graphql_endpoint = graphql_endpoint
        self.debug = debug
        self._semaphore = asyncio.Semaphore(1)

    async def execute_async(self, query: str, variables: dict = None):
        async with self._semaphore:
            return self._execute(query, variables)

    def _execute(self, query: str, variables: dict = None):
        try:
            parsed_query = print_ast(parse(query))
            headers = {}

            request_data = {"query": parsed_query, "variables": variables}
            if self.debug:
                print("request data", request_data)
            response = requests.post(
                self.graphql_endpoint, json=request_data, headers=headers
            )

            if not response.text:
                raise RuntimeError("Empty response received from GraphQL endpoint.")

            response_data = response.json()
            if "errors" in response_data:
                raise RuntimeError(
                    f"GraphQL request failed with errors: {response_data['errors']}"
                )
            res = {"data": response_data["data"]}
            if self.debug:
                print("response ===> ", res)
            return res

        except (RequestException, GraphQLSyntaxError) as e:
            raise RuntimeError(f"Invalid GraphQL syntax: {e}")

    def execute(self, query: str, variables: dict = None):
        return self._execute(query, variables)
