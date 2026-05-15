import strawberry
from auth.adapters.driving.graphql.auth_resolver import Query as AuthQuery, Mutation as AuthMutation
from boundaries.adapters.driving.graphql.boundarie_resolver import Query as BoundarieQuery


@strawberry.type
class RootQuery(AuthQuery, BoundarieQuery):
    pass


@strawberry.type
class RootMutation(AuthMutation):
    pass


schema = strawberry.Schema(query=RootQuery, mutation=RootMutation)
