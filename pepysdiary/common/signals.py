import operator
from functools import reduce

from django.contrib.postgres.search import SearchVector
from django.db import transaction
from django.db.models import TextField, Value
from django.db.models.signals import post_save
from django.dispatch import receiver

# Signals for models from all apps that have search indexes.

# All this inspired by
# https://github.com/simonw/simonwillisonblog/blob/master/blog/signals.py


@receiver(post_save)
def on_save(sender, **kwargs):
    """Only do something if this object has a search_document property
    and an index_components() method.
    """
    obj = kwargs["instance"]
    if (
        not hasattr(obj, "search_document")
        or not hasattr(obj, "index_components")
        or not callable(obj.index_components)
    ):
        return
    transaction.on_commit(make_updater(kwargs["instance"]))


def make_updater(instance):
    """Updates the search index for an object.
    Assumes it has a search_document attribute and an index_components()
    method. The latter should be something like:

    def index_components(self):
        return ((self.title, "A"), (self.body, "B"))
    """
    components = instance.index_components()
    pk = instance.pk

    def on_commit():
        search_vectors = []
        for text, weight in components:
            search_vectors.append(
                SearchVector(Value(text, output_field=TextField()), weight=weight)
            )
        instance.__class__.objects.filter(pk=pk).update(
            search_document=reduce(operator.add, search_vectors)
        )

    return on_commit
