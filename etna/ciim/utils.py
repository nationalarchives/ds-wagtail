

def value_from_dictionary_in_list(dictionaries, key, default=None):
    return next((i for i in dictionaries if key in i), {}).get(key, default)
