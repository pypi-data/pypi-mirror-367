SHARED_PYTHON_KEYWORDS = ["format"]


def clean_keyword(current_item):
    if current_item[0].isnumeric() or current_item in SHARED_PYTHON_KEYWORDS:
        return f"_{current_item}"
    return current_item


def clean_keywords_list(_list):
    for i in range(len(_list)):
        _list[i] = clean_keyword(_list[i])
    return _list


def remove_quotes(obj):
    return str(obj).replace('"', "").replace("'", "")


def write_to_py_file(file_path="", file_name="generated_python_file", data=""):
    temp_path = file_path + file_name + ".py"
    with open(temp_path, "w") as f:
        f.write(data)


def check_for_substrings(string, comparison_list, return_difference=False):
    if not [sub for sub in ["__"] if (sub in string)]:
        for sub in comparison_list:
            if sub in string:
                if return_difference:
                    return string.replace(sub, "")
                return string


__all__ = [
    "clean_keyword",
    "clean_keywords_list",
    "remove_quotes",
    "write_to_py_file",
    "check_for_substrings",
]
