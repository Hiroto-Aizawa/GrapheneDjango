# プロジェクトのセットアップ

## セットアップ

```bash
# ルートディレクトリの作成
$ mkdir graphene_project
$ cd grapehen_project

# 仮想環境の作成&有効化
$ virtualenv graphene_venv
$ source graphene_venv/bin/activate

# djangoとgraphene_djangoのインストール
(graphene_venv) $ python3 -m pip install django graphene_django

# プロジェクトディレクトリ&アプリケーションの作成
(graphene_venv) $ django-admin startproject graphene_project .
(graphene_venv) $ cd graphene_project
(graphene_venv) $ django-admin startapp ingredients
```

### アプリケーション修正

```
# graphene_project/graphene_project/ingredients/apps.py

from django.apps import AppConfig


class IngredientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'graphene_project.ingredients'
```

### モデルの作成

```python3
# graphene_project/ingredients/models.py

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField()
    category = models.ForeignKey(
        Category, related_name="ingredients", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
```

### setings.py の設定

```python3
# graphene_project/graphene_project/settings.py

INSTALLED_APPS = [
    ...
    'graphene_django',
    'graphene_project.ingredients',

]

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

GRAPHENE = {
    'SCHEMA': 'graphene_project.schema.schema',
}
```

### admin.py の設定

```python3
# graphene_project/admin.py

from django.contrib import admin
from graphene_project.ingredients.models import Category, Ingredient

# Register your models here.
admin.site.register(Category)
admin.site.register(Ingredient)

```

### テスト用データの読み込み

[ingredients.json](https://raw.githubusercontent.com/graphql-python/graphene-django/master/examples/cookbook/cookbook/ingredients/fixtures/ingredients.json)を DL する

`graphene_project/ingredients/fixtures/ingredients.json`  
となるように階層を作成し、json ファイルを格納する

```bash
# マイグレーションファイルの作成
(grapehen_venv) $ python3 manage.py makemigrations ingredients

# マイグレーションの適用
(grapehen_venv) $ python3 manage.py migrate

# fixtureのロード
(graphene_venv) $ python3 manage.py loaddata ingredients
 Installed 6 object(s) from 1 fixture(s)
```

### schema.py の作成

Django プロジェクトにクエリを発行するには、以下のものが必要です：

・オブジェクトタイプを定義したスキーマ  
・クエリを入力として受け取り、結果を返すビュー

GraphQL は、オブジェクトを、皆さんが慣れ親しんでいるような階層構造ではなく、グラフ構造として世界に提示します。  
この表現を作成するために、Graphene はグラフに現れるオブジェクトの各タイプについて知る必要があります。

また、このグラフには、すべてのアクセスを開始するルート・タイプがあります。これが以下の Query クラスである。

それぞれの Django モデルに対応する GraphQL タイプを作成するために、 DjangoObjectType クラスをサブクラス化します。

このクラスは、Django モデルのフィールドに対応する GraphQL フィールドを自動的に定義します。

```python3
# graphene_project/schema.py

import graphene
from graphene_django import DjangoObjectType

from graphene_project.ingredients.models import Category, Ingredient

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "ingredients")

class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "notes", "category")

class Query(graphene.ObjectType):
    all_ingredients = graphene.List(IngredientType)
    category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))

    def resolve_all_ingredients(root, info):
        # We can easily optimize query count in the resolve method
        return Ingredient.objects.select_related("category").all()

    def resolve_category_by_name(root, info, name):
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None

schema = graphene.Schema(query=Query)
```

### urls.py の設定

```python3
# graphene_project

from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

```

### GraphQL のテスト

サーバーを起動する

```bash
(graphene_venv) $ python3 manage.py runserver
```

[localhost:8000/graphql](http://127.0.0.1:8000/graphql)へアクセスし、最初のクエリを入力する

```
query {
	allIngredients {
		id
        name
  }
}
```

おわかりのように、GraphQL は非常に強力で、Django モデルを統合することで、動作するサーバをすぐに始めることができます。

`django-filter` や自動ページ分割のようなものを実際に使いたいのであれば、 [Relay チュートリアル](https://docs.graphene-python.org/projects/django/en/latest/tutorial-relay/#relay-tutorial)を続けるべきです。

Graphene のドキュメントをチェックし、[Graphene](https://docs.graphene-python.org/en/latest/) にも慣れておくとよいでしょう。

## 参考サイト

[Graphene-Python - Basic Tutorial](https://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/)
