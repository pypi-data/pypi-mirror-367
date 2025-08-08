# -*- coding: utf-8 -*-

class Phoneme:

    def __init__(self, arpabet: str, ipa: str, is_vowel: bool):
        '''
        :param arpabet: ARPAbet
        :param ipa: 国际音标
        :param is_vowel: 是否是元音
        '''
        self._arpabet = arpabet
        self._is_vowel = is_vowel
        self._ipa = ipa
    
    def __repr__(self) -> str:
        return f"Phoneme(arpabet={self.arpabet}, ipa={self.ipa}, is_vowel={self.is_vowel})"

    @property
    def ipa(self):
        return self._ipa

    @property
    def arpabet(self):
        return self._arpabet

    @property
    def is_vowel(self):
        return self._is_vowel
