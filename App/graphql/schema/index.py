import strawberry
from account_provider.adapters.driving.graphql.account_provider_resolver import Query as AccountProviderQuery, Mutation as AccountProviderMutation
from auth.adapters.driving.graphql.auth_resolver import Query as AuthQuery, Mutation as AuthMutation
from boundaries.adapters.driving.graphql.boundarie_resolver import Query as BoundarieQuery
from identification_type.adapters.driving.graphql.identification_type_resolver import Query as IdentificationTypeQuery, Mutation as IdentificationTypeMutation
from person.adapters.driving.graphql.person_resolver import Query as PersonQuery, Mutation as PersonMutation
from user_account.adapters.driving.graphql.user_account_resolver import Query as UserAccountQuery, Mutation as UserAccountMutation


@strawberry.type
class RootQuery(AccountProviderQuery, AuthQuery, BoundarieQuery, IdentificationTypeQuery, PersonQuery, UserAccountQuery):
    pass


@strawberry.type
class RootMutation(AccountProviderMutation, AuthMutation, IdentificationTypeMutation, PersonMutation, UserAccountMutation):
    pass


schema = strawberry.Schema(query=RootQuery, mutation=RootMutation)
