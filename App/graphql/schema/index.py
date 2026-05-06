"""
Owner: ArelyXl
Description: Compose el esquema raíz de GraphQL unificando los queries y mutations de los módulos (actualmente solo auth), generando el esquema final de Strawberry.
"""
import strawberry
from auth.adapters.driving.graphql.auth_resolver import Query as AuthQuery, Mutation as AuthMutation

@strawberry.type
class RootQuery(AuthQuery):
    pass

@strawberry.type
class RootMutation(AuthMutation):
    pass

schema = strawberry.Schema(query=RootQuery, mutation=RootMutation)
