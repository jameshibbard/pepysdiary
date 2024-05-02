import re
import time

from django.db import models
from django.utils import timezone
from treebeard.mp_tree import MP_NodeManager

from pepysdiary.encyclopedia import category_lookups
from pepysdiary.encyclopedia.wikipedia_fetcher import WikipediaFetcher


class CategoryManager(MP_NodeManager):
    def map_category_choices(self):
        """
        The categories we DO use on the maps page.
        As opposed to the Topic.MapCategory, which appears to be unused.
        This structure is used to generate the SELECT field on the
        /encyclopedia/map/ page.
        The numbers are the IDs of the relevant Categories.

        To add a new option to the map, you should ONLY need to add it to
        this structure, and everything else should work...
        You might also want to adjust the start_coords in pepys.js if the map
        should be focused on something other than central London.
        """
        return (
            (
                "London",
                (
                    (category_lookups.PLACES_LONDON_AREAS, "Areas of London"),
                    (
                        category_lookups.PLACES_LONDON_CHURCHES,
                        "Churches and cathedrals in London",
                    ),
                    (category_lookups.PLACES_LONDON_GOVERNMENT, "Government buildings"),
                    (category_lookups.PLACES_LONDON_LIVERY_HALLS, "Livery halls"),
                    (
                        category_lookups.PLACES_LONDON_STREETS,
                        "Streets, gates, squares, piers, etc",
                    ),
                    (category_lookups.PLACES_LONDON_TAVERNS, "Taverns in London"),
                    (category_lookups.PLACES_LONDON_THEATRES, "Theatres in London"),
                    (category_lookups.PLACES_LONDON_WHITEHALL, "Whitehall Palace"),
                    (category_lookups.PLACES_LONDON_ROYAL, "Other royal buildings"),
                    (category_lookups.PLACES_LONDON_OTHER, "Other London buildings"),
                ),
            ),
            (category_lookups.PLACES_LONDON_ENVIRONS, "London environs"),
            (category_lookups.PLACES_BRITAIN_WATERWAYS, "Waterways in Britain"),
            (category_lookups.PLACES_BRITAIN_REST, "Rest of Britain"),
            (category_lookups.PLACES_WORLD_REST, "Rest of the world"),
        )

    def valid_map_category_ids(self):
        """
        Returns a list of the category IDs in map_category_choices().
        Assumes we only have one sub-level.
        There's probably some clever one-line way of doing this, but still.
        """
        choices = self.map_category_choices()
        ids = []
        for tup1 in choices:
            if isinstance(tup1[0], int):
                ids.append(tup1[0])
            else:
                for tup2 in tup1[1]:
                    ids.append(tup2[0])
        return ids


class TopicManager(models.Manager):
    def pepys_homes_ids(self):
        """The IDs of the Topics about the places Pepys has lived."""
        return [102, 1023]

    def fetch_wikipedia_texts(self, topic_ids=None, num=None):
        """
        Passed a list of Topic IDs, this calls the method that fetches and
        munges the Wikipedia HTML for any of those Topics that have
        `wikipedia_fragment`s set.

        topic_ids is a list of topic IDs (ints).
        num is either the number of topics to update, or the string 'all'.

        If num is set then topic_ids is ignored.

        By default, this method will fetch nothing.

        Returns a dict with 'success' and 'failure' elements. Each of those is
        a list containing the relevant Topic IDs.
        Success is when we fetched the Wikipedia text for a topic.
        Failure is when we tried but failed.
        Topics that have no Wikipedia URL fragments aren't counted (as we
        don't even try to fetch their texts).
        """
        if topic_ids is None:
            topic_ids = []

        results = {
            "success": [],
            "failure": [],
        }

        qs = self.model.objects.only("id", "wikipedia_fragment").exclude(
            wikipedia_fragment__exact=""
        )

        if num == "all":
            # We don't modify the QuerySet
            pass
        elif isinstance(num, int):
            # We want any topics with wikipedia_last_fetch = NULL to be
            # returned first, before any low datetimes. By default they would
            # be listed last. This fixes that.
            # http://stackoverflow.com/a/12631576/250962
            qs = qs.extra(
                select={"null_fetch": "wikipedia_last_fetch is null"},
                order_by=["-null_fetch", "wikipedia_last_fetch"],
            )[:num]
        else:
            qs = qs.filter(pk__in=topic_ids)

        fetcher = WikipediaFetcher()

        if qs.count() > 0:
            for topic in qs:
                fetched = fetcher.fetch(topic.wikipedia_fragment)
                if fetched["success"] is True:
                    topic.wikipedia_html = fetched["content"]
                    topic.wikipedia_last_fetch = timezone.now()
                    topic.save()
                    results["success"].append(topic.id)
                else:
                    results["failure"].append(topic.id)
                # Be nice when fetching things:
                time.sleep(0.5)

        return results

    def make_order_title(self, text, *, is_person=False):
        """
        If is_person we change:

        "Fred Bloggs" to "Bloggs, Fred"
        "Sidney Smythe (1st Lord Smythe)" to "Smythe, Sidney (1st Lord Smythe)"
        "Sir Heneage Finch (Solicitor-General)" to "Finch, Sir Heneage (Solicitor-General)"
        "Capt. Henry Terne" to "Terne, Capt. Henry"
        "Capt. Aldridge" to "Aldridge, Capt."
        "Mr Hazard" to "Hazard, Mr"
        "Johann Heinrich Alsted" to "Alsted, Johann Heinrich"
        "Monsieur d'Esquier" to "Esquier, Monsieur d'"
        "Adriaen de Haes" to "Haes, Adriaen de"
        "Jan de Witt (Grand Pensionary of Holland)" to "Witt, Jan de (Grand Pensionary of Holland)"
        "Peter de la Roche" to "Roche, Peter de la"
        "Monsieur du Prat" to "Prat, Monsieur du"
        "Catherine of Braganza (Queen)" to "Braganza, Catherine of (Queen)"
        "Michiel van Gogh (Dutch Ambassador, 1664-5)" to "Gogh, Michiel van (Dutch Ambassador, 1664-5)"
        "Mr Butler (Mons. L'impertinent)" to "Butler, Mr (Mons. L'impertinent)"
        'Abd Allah al-Ghailan ("Guiland")' to 'Ghailan, Abd Allah al- ("Guiland")'
        "Sir Anthony Ashley Cooper (Baron Ashley)" to "Cooper, Sir Anthony Ashley (Baron Ashley)"

        Stay the same:
        "Mary (c, Pepys' chambermaid)"
        "Shelston"
        "Mary I of England"
        "Philip IV (King of Spain, 1621-1665)"
        "Ivan the Terrible"

        If not is_person we change:
        "The Royal Prince" to "Royal Prince, The"
        "The Alchemist (Ben Jonson)" to "Alchemist, The (Ben Jonson)"
        "'A dialogue concerning...'" to "A dialogue concerning...'"
        """  # noqa: E501
        order_title = text

        if text != "":
            if is_person:
                # First we take off any bit in parentheses at the end.
                name_match = re.match(r"^(.*?)(?:\s)?(\(.*?\))?$", text)
                parentheses = ""
                matches = name_match.groups()
                if matches[1] is not None:
                    parentheses = f" {matches[1]}"
                # The actual name part of the string:
                name = matches[0]

                pattern = r"""
                    # Optionally match a title:
                    (Ald\.|Capt\.|Col\.|Don|Dr|Lady|Lieut\.|Lord|Lt-Adm\.|Lt-Col\.|Lt-Gen\.|Maj\.(?:-Gen\.)?(?:\sAld\.)?(?:\sSir)?|Miss|(?:Mrs?)|Ms|Pope|Sir)?
                    # Ignore any space after a title:
                    (?:\s)?
                    # Match a single first name:
                    (.*?)
                    # Match any other names up until the end:
                    (?:\s(.*?))?
                    # That's it:
                    $
                """
                name_match = re.match(pattern, name, re.VERBOSE)
                matches = list(name_match.groups())

                # We need to trap anything that's like:
                # "Mary I of England"
                # "Philip IV (King of Spain, 1621-1665)"
                # "Ivan the Terrible"
                monarch_match = None
                if matches[2] is not None:
                    monarch_match = re.match(
                        r"^(I|II|III|IV|V|VI|VII|VIII|XI|XII|XIII|XIV|XV|the)(?:\s|$)",
                        matches[2],
                    )
                if monarch_match is not None:
                    # Looks like it's a king-type person.
                    # Leave the text as it was.
                    pass
                else:
                    # Save any title, plus a space, or just nothing:
                    title = ""
                    if matches[0] is not None:
                        title = f"{matches[0]}"

                    if matches[2] is not None:
                        # The "surname" part has something in it.

                        if matches[2][:1] == "(":
                            # Not sure what this would catch, because the example below
                            # is split up with the very first regex.
                            # eg, (None, 'Mary', "(c, Pepys' chambermaid)", None)
                            # leave it as-is.
                            pass
                        elif matches[1][-1:] == ",":
                            # eg, (None, 'Godefroy,', "Comte d'Estrades")
                            # leave it as-is.
                            pass
                        else:
                            # A little fix first for surnames like "d'Esquier".
                            # We want to move any leading "d'" or "l'" from the
                            # start of the surname to the end of the first names.
                            # So that we'll order by "Esquier".
                            apostrophe_match = re.match(
                                r"^(.*?)\s?(d'|l'|al-)(.*?)$", matches[2]
                            )
                            if apostrophe_match is not None:
                                # Will be something like ("Pierre", "d'", "Esquier")
                                # or ('', "d'", "Esquier"):
                                apostrophe_matches = apostrophe_match.groups()
                                if apostrophe_matches[0] == "":
                                    # Will be like "Monsieur d'":
                                    matches[1] = f"{matches[1]} {apostrophe_matches[1]}"
                                else:
                                    matches[1] = (
                                        f"{matches[1]} {apostrophe_matches[0]} "
                                        f"{apostrophe_matches[1]}"
                                    )
                                # Will be like "Esquier":
                                matches[2] = apostrophe_matches[2]

                            # See what's in the "surname" part.
                            # One word or more?
                            surname_match = re.match(r"^(.*)(?:\s)(.*?)$", matches[2])
                            if surname_match is None:
                                # "surname" was just one word, simple.
                                # eg, (None, 'Fred', 'Bloggs', None)
                                if title == "":
                                    order_title = (
                                        f"{matches[2]}, {matches[1]}{parentheses}"
                                    )
                                else:
                                    order_title = (
                                        f"{matches[2]}, {title} "
                                        f"{matches[1]}{parentheses}"
                                    )
                            else:
                                # "surname" has more than one word.
                                # eg, (None, 'Adriaen', 'de Haes', None)
                                surname_matches = surname_match.groups()
                                # surname_matches might now be like:
                                # ('de la', 'Roche')
                                pre_surname = ""
                                if surname_matches[0]:
                                    pre_surname = f" {surname_matches[0]}"
                                if title != "":
                                    title += " "
                                order_title = (
                                    f"{surname_matches[1]}, "
                                    f"{title}{matches[1]}{pre_surname}{parentheses}"
                                )
                    elif title != "":
                        # eg, ('Mr', 'Hazard', None)
                        # Need to remove extra space from title, eg 'Mr ':
                        if parentheses == "":
                            order_title = f"{matches[1]}, {title}"
                        else:
                            order_title = f"{matches[1]}, {title}{parentheses}"
                    else:
                        pass

            else:  # Not a person.
                # Remove leading 'The '.
                the_pattern = re.compile(r"^The\s(.*?)(?:\s\((.*?)\))?$")
                the_match = the_pattern.match(text)
                if the_match is not None:
                    # Starts with 'The '.
                    matches = the_match.groups()
                    if matches[1] is None:
                        # eg, ('Royal Prince', None)
                        order_title = f"{matches[0]}, The"
                    else:
                        # eg, ('Alchemist', 'Ben Jonson')
                        order_title = f"{matches[0]}, The ({matches[1]})"

                # Remove leading apostrophe.
                apos_pattern = re.compile(r"^'(.*)$")
                apos_match = apos_pattern.match(text)
                if apos_match is not None:
                    order_title = apos_match.groups()[0]

        return order_title
