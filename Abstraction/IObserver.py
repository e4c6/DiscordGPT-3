#  e4c6 ~ 2021
from __future__ import annotations

from abc import ABC, abstractmethod

import Abstraction.ISubject


class IObserver(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self, subject: Abstraction.ISubject.ISubject) -> None:
        """
        Receive update from subject.
        """
        pass
