from wagtail.search.query import PlainText
from wagtail.search.utils import AND, normalise_query_string


def normalise_native_search_query(query: str | None) -> str | PlainText:
    # to use when searching
    if query and "AND" in query:
        logical_query_segments = []
        for segment in query.split("AND"):
            normalized = normalise_query_string(segment)
            if isinstance(normalized, str):
                logical_query_segments.append(
                    PlainText(normalized, operator="and")
                )
            else:
                logical_query_segments.append(normalized)
        return AND(logical_query_segments)
    return query
