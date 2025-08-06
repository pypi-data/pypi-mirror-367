import dearpygui.dearpygui as dpg


def __find_item_by_type(item_type):
    for _id in dpg.get_all_items():
        if item_type in dpg.get_item_type(_id):
            return _id


def find_texture_registry():
    texture_registry = __find_item_by_type("mvTextureRegistry")

    if not texture_registry:
        texture_registry = dpg.add_texture_registry()

    return texture_registry


def __non_empty(dictionary):
    return {k: v for k, v in dictionary.items() if v or isinstance(v, int)}


def __has_parent(tag):
    try:
        return dpg.get_item_parent(tag)
    except SystemError as e:
        print(f"{tag}, does not have parent")


def __delete_if_exists(tag):
    try:
        dpg.delete_item(tag)
    except SystemError as e:
        print(f"{tag}, could not be deleted")


def __image(
    texture_tag,
    image_tag,
    width,
    height,
    data,
    image_parent="",
    texture_function=dpg.add_raw_texture,
    remove_previous=True,
    show=True,
    button_callback=None,
    image_function=dpg.add_image
):

    if button_callback:
        image_function = dpg.add_image_button
    
    if not image_parent:
        image_parent = __has_parent(image_tag)
        if not image_parent:
            image_parent = dpg.last_container()

    if remove_previous:
        __delete_if_exists(image_tag)
        __delete_if_exists(texture_tag)
    else:
        texture_tag = None

    try:
        image_function(
            **__non_empty(
                {
                    "parent": image_parent,
                    "show": show,
                    "tag": image_tag,
                    "callback": button_callback,
                    "texture_tag": texture_function(
                        **__non_empty(
                            {
                                "width": width,
                                "height": height,
                                "default_value": data,
                                "tag": texture_tag,
                                "parent": find_texture_registry(),
                            }
                        )
                    ),
                }
            )
        )
    except SystemError as e:
        print(e)


def image_from_data_source(
    texture_tag,
    image_tag,
    width,
    height,
    data,
    image_parent="",
    texture_function=dpg.add_raw_texture,
    show=True,
    button_callback=None
):
    __image(
        width=width,
        height=height,
        data=data,
        image_parent=image_parent,
        image_tag=image_tag,
        texture_tag=texture_tag,
        texture_function=texture_function,
        show=show,
        button_callback=button_callback
    )


def image_from_file(
    image_tag,
    texture_tag,
    file_path="",
    image_parent="",
    texture_function=dpg.add_raw_texture,
    show=True,
    button_callback=None
):

    width, height, c, data = dpg.load_image(file_path)

    __image(
        width=width,
        height=height,
        data=data,
        image_parent=image_parent,
        image_tag=image_tag,
        texture_tag=texture_tag,
        texture_function=texture_function,
        show=show,
        button_callback=button_callback
    )
