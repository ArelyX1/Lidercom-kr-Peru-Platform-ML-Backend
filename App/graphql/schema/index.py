import strawberry
from auth.adapters.driving.graphql.auth_resolver import Query as AuthQuery, Mutation as AuthMutation
from boundaries.adapters.driving.graphql.boundarie_resolver import Query as BoundarieQuery
from identification_type.adapters.driving.graphql.identification_type_resolver import Query as IdentificationTypeQuery, Mutation as IdentificationTypeMutation
from person.adapters.driving.graphql.person_resolver import Query as PersonQuery, Mutation as PersonMutation
from user_account.adapters.driving.graphql.user_account_resolver import Query as UserAccountQuery


@strawberry.type
class RootQuery(AuthQuery, BoundarieQuery, IdentificationTypeQuery, PersonQuery, UserAccountQuery):
    pass


@strawberry.type
class RootMutation(AuthMutation, IdentificationTypeMutation, PersonMutation):
    pass


schema = strawberry.Schema(query=RootQuery, mutation=RootMutation)
