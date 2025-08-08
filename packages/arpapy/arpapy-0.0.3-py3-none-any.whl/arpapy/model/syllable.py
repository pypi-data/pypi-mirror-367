# -*- coding: utf-8 -*-
from .stress import Stress
from .phoneme import Phoneme
from typing import Optional, List

class Syllable:

    def __init__(self):
        self.stress: Optional[Stress] = None
        self._phoneme_list: List[Phoneme] = []
        self._have_vowel: bool = False
    
    def __repr__(self) -> str:
        return f"Syllable(stress={self.stress}, phoneme_list={self._phoneme_list}, have_vowel={self.have_vowel})"

    @property
    def have_vowel(self):
        return self._have_vowel

    def is_empty(self):
        return len(self._phoneme_list) <= 0

    def add_phoneme(self, phoneme: Phoneme):
        self._phoneme_list.append(phoneme)
        if phoneme.is_vowel:
            if not self.stress:
                self.stress = Stress.No
            self._have_vowel = True

    def translate_to_arpabet(self):
        translations = []

        for phoneme in self._phoneme_list:
            if phoneme.is_vowel:
                assert self.stress is not None
                translations.append(phoneme.arpabet + self.stress.mark_arpabet())
            else:
                translations.append(phoneme.arpabet)

        return " ".join(translations)
