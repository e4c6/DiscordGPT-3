#  e4c6 ~ 2021
from __future__ import annotations

from abc import ABC, abstractmethod

import Abstraction.IObserver


class ISubject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    @abstractmethod
    def attach(self, observer: Abstraction.IObserver.IObserver) -> None:
        """
        Attach an observer to the subject.
        """
        pass

    @abstractmethod
    def detach(self, observer: Abstraction.IObserver.IObserver) -> None:
        """
        Detach an observer from the subject.
        """
        pass

    @abstractmethod
    def notify(self) -> None:
        """
        Notify all observers about an event.
        """
        pass
