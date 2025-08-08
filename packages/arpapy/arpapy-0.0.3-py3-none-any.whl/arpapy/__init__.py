# -*- coding: utf-8 -*-
from .model.phoneme import Phoneme
from .model.stress import Stress
from .excepts import PhonemeError
from .arpa import get_arpa
from .const import vowels, consonants, auxiliary, all_diacritics_ipa, suprasegmental_duration_ipa, suprasegmental_prosodic_ipa, suprasegmental_pitch_ipa
from .segment import segment_string, categorize_character, categorize_string, CharacterCategory
from typing import Iterable, Tuple, Set

def get_supported_arphabet():
    return set([o.arpabet for o in vowels + consonants + auxiliary])

def compare_supported_arphabet(arpabet: Iterable[str]) -> Tuple[Set[str], Set[str]]:
    # remove 0/1/2 stress from arpabet
    arpabet = set([o[:-1] if o[-1] in {"0", "1", "2"} else o for o in arpabet])
    i_dont_support = arpabet - get_supported_arphabet()
    you_dont_support = get_supported_arphabet() - arpabet
    return i_dont_support, you_dont_support

aa = {
    "AH0",
    "S",
    "AH1",
    "EY2",
    "AE2",
    "EH0",
    "OW2",
    "UH0",
    "NG",
    "B",
    "G",
    "AY0",
    "M",
    "AA0",
    "F",
    "AO0",
    "ER2",
    "UH1",
    "IY1",
    "AH2",
    "DH",
    "IY0",
    "EY1",
    "IH0",
    "K",
    "N",
    "W",
    "IY2",
    "T",
    "AA1",
    "ER1",
    "EH2",
    "OY0",
    "UH2",
    "UW1",
    "Z",
    "AW2",
    "AW1",
    "V",
    "UW2",
    "AA2",
    "ER",
    "AW0",
    "UW0",
    "R",
    "OW1",
    "EH1",
    "ZH",
    "AE0",
    "IH2",
    "IH",
    "Y",
    "JH",
    "P",
    "AY1",
    "EY0",
    "OY2",
    "TH",
    "HH",
    "D",
    "ER0",
    "CH",
    "AO1",
    "AE1",
    "AO2",
    "OY1",
    "AY2",
    "IH1",
    "OW0",
    "L",
    "SH",
}

print(compare_supported_arphabet(aa))