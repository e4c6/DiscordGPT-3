#  e4c6 ~ 2021

from enum import Enum


class PreferredEngine(Enum):
    ADA = [1, "ada"]
    BABBAGE = [2, "babbage"]
    CONTENT_FILTER_ALPHA_C4 = [3, "content-filter-alpha-c4"]
    CONTENT_FILTER_DEV = [4, "content-filter-dev"]
    CURIE = [5, "curie"]
    CURIE_INSTRUCT_BETA = [6, "curie-instruct-beta"]
    CURSING_FILTER_V6 = [7, "cursing-filter-v6"]
    DAVINCI = [8, "davinci"]
    DAVINCI_INSTRUCT_BETA = [9, "davinci-instruct-beta"]

    def __eq__(self, other):
        return self.value[0] == other.value[0]

    def __ne__(self, other):
        return self.value[0] != other.value[0]

    def __gt__(self, other):
        return self.value[0] > other.value[0]

    def __ge__(self, other):
        return self.value[0] >= other.value[0]

    def __lt__(self, other):
        return self.value[0] < other.value[0]

    def __le__(self, other):
        return self.value[0] <= other.value[0]

    def __str__(self):
        return self.value[1]

    def __hash__(self):
        return hash(self.value[1])
