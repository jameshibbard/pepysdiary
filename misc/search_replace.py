from django.db.models import F, Func, Value

from pepysdiary.encyclopedia.models import Topic
from pepysdiary.indepth.models import Article
from pepysdiary.news.models import Post

# This was used to replace all the instances of old Media URLs with new
# ones. Saved in case we need it, or similar, again.
# Copy and paste stuff into the Django shell.

# Don't forget to change src= and href=
# And there are 3+ Annotations that contain direct references to media files
# (change those manually in the admin).

to_find = 'href="/media/'
to_replace = 'href="https://pepysdiary-production.s3.amazonaws.com/media/'


def replace_func(field_name, find_str, replace_str):
    return Func(F(field_name), Value(find_str), Value(replace_str), function="replace")


Article.objects.update(
    intro=replace_func("intro", to_find, to_replace),
    intro_html=replace_func("intro_html", to_find, to_replace),
    text=replace_func("text", to_find, to_replace),
    text_html=replace_func("text_html", to_find, to_replace),
)

Post.objects.update(
    intro=replace_func("intro", to_find, to_replace),
    intro_html=replace_func("intro_html", to_find, to_replace),
    text=replace_func("text", to_find, to_replace),
    text_html=replace_func("text_html", to_find, to_replace),
)

Topic.objects.update(
    summary=replace_func("summary", to_find, to_replace),
    summary_html=replace_func("summary_html", to_find, to_replace),
)
