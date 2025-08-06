from abc import ABC, abstractmethod
from typing import Iterable, Callable, Any



class ListenerProviderInterface(ABC):
    """
    Интерфейс для поставщика слушателей событий.
    Определяет метод для получения слушателей, соответствующих конкретному событию.
    """

    @abstractmethod
    def get_listeners_for_event(self, event: object) -> Iterable[Callable[..., Any]]:
        """
        Возвращает итерируемую коллекцию слушателей для заданного события.

        :param event: Событие, для которого нужно получить слушателей.
                            Может быть любого типа, но обычно это экземпляр класса события.
        :type event: Object


        :returns: Итерируемая коллекция callable-объектов (функций или методов). Каждый callable должен быть совместим
                  по типу с переданным событием. Может быть списком, генератором или другим итерируемым объектом.
        :rtype: Iterable[Callable[..., Any]]
        """
        raise NotImplementedError
