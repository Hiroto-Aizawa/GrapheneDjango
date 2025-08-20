import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import models as auth_models


class User(DjangoObjectType):
    class Meta:
        model = auth_models.User


class Query(graphene.ObjectType):
    users = graphene.List(User)

    @graphene.resolve_only_args
    def resolve_users(self):
        return auth_models.User.objects.all()


schema = graphene.Schema(query=Query)