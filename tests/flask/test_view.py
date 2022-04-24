import json

import strawberry
from flask import Flask, Response, request
from strawberry.flask.views import GraphQLView as BaseGraphQLView
from strawberry.types import ExecutionResult, Info


def test_custom_context():
    class CustomGraphQLView(BaseGraphQLView):
        def get_context(self, response: Response):
            return {
                "request": request,
                "response": response,
                "custom_value": "Hi!",
            }

    @strawberry.type
    class Query:
        @strawberry.field
        def custom_context_value(self, info: Info) -> str:
            return info.context["custom_value"]

    schema = strawberry.Schema(query=Query)

    app = Flask(__name__)
    app.debug = True

    app.add_url_rule(
        "/graphql",
        view_func=CustomGraphQLView.as_view("graphql_view", schema=schema),
    )

    with app.test_client() as client:
        query = "{ customContextValue }"

        response = client.get("/graphql", json={"query": query})
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert data["data"] == {"customContextValue": "Hi!"}


def test_custom_process_result():
    class CustomGraphQLView(BaseGraphQLView):
        def process_result(self, result: ExecutionResult):
            return {}

    @strawberry.type
    class Query:
        @strawberry.field
        def abc(self) -> str:
            return "ABC"

    schema = strawberry.Schema(query=Query)

    app = Flask(__name__)
    app.debug = True

    app.add_url_rule(
        "/graphql",
        view_func=CustomGraphQLView.as_view("graphql_view", schema=schema),
    )

    with app.test_client() as client:
        query = "{ abc }"

        response = client.get("/graphql", json={"query": query})
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert data == {}


def test_context_with_response():
    @strawberry.type
    class Query:
        @strawberry.field
        def response(self, info: Info) -> bool:
            response: Response = info.context["response"]
            response.status_code = 401

            return True

    schema = strawberry.Schema(query=Query)

    app = Flask(__name__)
    app.debug = True

    app.add_url_rule(
        "/graphql",
        view_func=BaseGraphQLView.as_view("graphql_view", schema=schema),
    )

    with app.test_client() as client:
        query = "{ response }"

        response = client.get("/graphql", json={"query": query})
        assert response.status_code == 401
