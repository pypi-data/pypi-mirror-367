from typing import Union, Dict, Optional, final


@final
class AliasManager:
    """
    Менеджер псевдонимов пути.
    """

    def __init__(self):
        self._aliases: Dict[str, Union[str, Dict[str, str]]] = {}

    def get(self, alias: str, throw_exception: bool = True) -> Union[str, bool]:
        """
        Преобразует псевдоним пути в реальный путь.

        Алгоритм преобразования:
        1. Если псевдоним не начинается с '@', возвращается как есть
        2. Иначе ищется самый длинный зарегистрированный псевдоним, совпадающий с началом переданного
        3. Если псевдоним не найден, либо выбрасывается исключение, либо возвращается False


        :param alias: Псевдоним для преобразования (например "@root/config")
        :param throw_exception: Выбрасывать исключение при ошибке?
        :return: Реальный путь или False при ошибке (если throw_exception=False)
        :raises ValueError: Если псевдоним невалиден и throw_exception=True
        """
        if not alias.startswith('@'):
            return alias

        pos = alias.find('/')
        root = alias if pos == -1 else alias[:pos]

        if root in self._aliases:
            root_value = self._aliases[root]

            if isinstance(root_value, str):
                return root_value if pos == -1 else root_value + alias[pos:]

            # Ищем самый специфичный (длинный) псевдоним
            for name, path in root_value.items():
                if alias.startswith(name + '/' if '/' not in name else name):
                    return path + alias[len(name):]

        if throw_exception:
            raise ValueError(f"Invalid path alias: {alias}")
        return False

    def get_root(self, alias: str) -> Union[str, bool]:
        """
        Возвращает корневой псевдоним для переданного.

        :param alias: Псевдоним для анализа.
        :return: Корневой псевдоним или False если не найден
        """
        pos = alias.find('/')
        root = alias if pos == -1 else alias[:pos]

        if root in self._aliases:
            root_value = self._aliases[root]

            if isinstance(root_value, str):
                return root

            # Ищем самый специфичный (длинный) псевдоним
            for name in root_value.keys():
                if alias.startswith(name + '/' if '/' not in name else name):
                    return name

        return False


    def set(self, alias: str, path: Optional[str]) -> None:
        """
        Регистрирует псевдоним пути.

        :param alias: Псевдоним (должен начинаться с '@').
        :param path: Соответствующий путь или None для удаления псевдонима
        :raises ValueError: Если path содержит невалидный псевдоним
        """
        if not alias.startswith('@'):
            alias = '@' + alias

        pos = alias.find('/')
        root = alias if pos == -1 else alias[:pos]

        if path is not None:
            # Обработка случая когда path сам является псевдонимом
            if path.startswith('@'):
                path = self.get(path)
            else:
                path = path.rstrip('\\/')

            if root not in self._aliases:
                if pos == -1:
                    self._aliases[root] = path
                else:
                    self._aliases[root] = {alias: path}
            else:
                root_value = self._aliases[root]

                if isinstance(root_value, str):
                    if pos == -1:
                        self._aliases[root] = path
                    else:
                        self._aliases[root] = {
                            alias: path,
                            root: root_value
                        }
                else:
                    root_value[alias] = path
                    # Сортируем по убыванию длины ключей
                    self._aliases[root] = dict(sorted(
                        root_value.items(),
                        key=lambda item: len(item[0]),
                        reverse=True
                    ))
        elif root in self._aliases:
            root_value = self._aliases[root]

            if isinstance(root_value, dict):
                if alias in root_value:
                    del root_value[alias]
                    if len(root_value) == 1 and root in root_value:
                        self._aliases[root] = root_value[root]
            elif pos == -1:
                del self._aliases[root]
