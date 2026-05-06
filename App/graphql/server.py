"""
Owner: ArelyXl
Description: Configura el servidor ASGI de Strawberry GraphQL usando el esquema unificado definido en graphql/schema/index.py.
"""
from strawberry.asgi import GraphQL
from graphql.schema.index import schema

app = GraphQL(schema)
