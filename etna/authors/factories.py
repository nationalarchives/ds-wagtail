import factory


class AuthorPageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "authors.AuthorPage"
