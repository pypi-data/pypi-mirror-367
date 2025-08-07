from typing import Union


def get_class_alias(alias: Union[str, type]) -> type:
    """
    Возвращает класс по его строковому псевдониму вида module:class

    :param alias: Строковый псевдоним. Импортируемое имя модуля и имя класса, разделенные двоеточием.
    :type  alias: Union[str, type]

    :rtype: Type
    """
    loaded = alias

    if type(alias) is str:
        from importlib import import_module
        m, c = alias.split(':', 1)
        loaded = getattr(import_module(m), c)

    if type(loaded) is not type:
        raise TypeError(f'Not a type or a type-alias "{alias}"')

    return loaded
