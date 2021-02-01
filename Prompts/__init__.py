from .EN import *
from .TR import *

language_map = {
    "EN": {
        "answer": answer_en,
        "complete": completion_en,
        "emojify": emojify_scaffold,
        "foulmouth": foulmouth_en,
        "headline": headline_en,
        "headline_out": headline_en_out,
        "sarcasm": sarcasm_en,
        "sentiment": sentiment_en,
        "song": song_en
    },
    "TR": {
        "answer": answer_tr,
        "complete": completion_tr,
        "emojify": emojify_scaffold,
        "foulmouth": foulmouth_tr,
        "headline": headline_tr,
        "headline_out": headline_tr_out,
        "sarcasm": sarcasm_tr,
        "sentiment": sentiment_tr,
        "song": song_tr
    }
}
