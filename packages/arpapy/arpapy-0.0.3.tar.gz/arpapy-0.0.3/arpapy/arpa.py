#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .const import vowels, consonants, auxiliary, stress_ipa

from .excepts import PhonemeError
from .model.syllable import Syllable
from .model.stress import Stress
from .model.phoneme import Phoneme

from typing import Dict, Optional, List, Union


class IPA2ARPA:

    def __init__(self, debug: bool = False):
        self.debug = debug
        self._ipa_to_phoneme: Dict[str, Phoneme] = {}

        for o in vowels + consonants + auxiliary:
            self._ipa_to_phoneme[o.ipa] = o

        self._stress_libs_dic = stress_ipa

    def print(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def convert(self, ipa: str, preserve_syllable: bool = False) -> List[str]:
        # note that this method only greedily look ahead for the next character
        # so it expect at most 2 characters to form a ARPA phoneme
        # e.g. if "a" and "abc" in IPA are a ARPA phoneme, given "a" as input, it
        # will convert "a" and an error will be raised for "bc".
        # a common example is two IPA characters with diacritics, making up 4 characters
        # but we don't support any diacritics for now, so this is not an issue.
        # I will rewrite a better one when I got time - Koke_Cacao
        if ipa == "":
            return []

        self.print(f"Converting: {ipa}")

        # Definitions:
        # Syllable: multiple Phonemes that end with a vowel
        # Phoneme: a unit for ARPA, which can be a vowel or a consonant
        temp_character: str = ''  # accumulated characters from last iteration
        temp_phoneme: Optional[
            Phoneme] = None  # accumulated phoneme from last iteration (linked to temp_character)
        out: List[Syllable] = []
        syllable = Syllable()
        for index, character in enumerate(ipa):
            self.print(
                f"=========== Processing [{index}] {character} ===========")
            self.print(
                f"temp_character: {temp_character}; temp_phoneme: {temp_phoneme};"
            )
            self.print(f"syllable: {syllable}; out: {out};")

            stress: Optional[Stress] = self._stress_libs_dic.get(
                character, None)
            if stress is not None:
                if index > 0 and temp_phoneme is None:
                    # If the stress is not the first character,
                    # and we don't have a complete phoneme yet,
                    # then we will never form a phoneme because stress symbol can't be in the middle of a phoneme
                    raise PhonemeError(
                        f'Unable to recognize the phoneme: {temp_character}. IPA: {ipa}'
                    )
                if temp_phoneme is not None:
                    # if we have a complete phoneme, add it to the syllable
                    syllable.add_phoneme(phoneme=temp_phoneme)
                    # in addition, since a stress symbol can't be in the middle of a syllable
                    # we know we have a complete syllable as well
                    out.append(syllable)
                    self.print(
                        f"Observe Stress: {character}; Phoneme Complete: {temp_phoneme}; Syllable Complete: {syllable};"
                    )
                    # prepare for next iteration
                    syllable = Syllable()
                    temp_phoneme = None
                    temp_character = ''
                    syllable.stress = stress
                    continue
                # else it must be the case that it is the first character
                assert index == 0
                self.print(f"Observe Stress: {character} (first character);")
                # prepare for next iteration
                syllable.stress = stress
                continue

            current_phoneme = self._ipa_to_phoneme.get(
                temp_character + character, None)
            self.print(f"current_phoneme: {current_phoneme}")

            if current_phoneme is not None or temp_phoneme is None:
                # when this character, after added, can form a phoneme
                # or even if it can't form a phoneme, without this character can't form a phoneme either
                # then we know we need to wait to see more characters
                self.print(
                    f"Observe Character: {character}; Last Phoneme: {temp_phoneme}; Current Phoneme: {current_phoneme}; Waiting..."
                )
                temp_character += character
                temp_phoneme = current_phoneme
                continue

            # otherwise, we know without this character we can form a phoneme
            # but with this character, we can no longer form a phoneme
            # so we know we have a phoneme without addition of this character
            syllable.add_phoneme(temp_phoneme)
            if temp_phoneme.is_vowel:
                out.append(syllable)
                syllable = Syllable()
                self.print(
                    f"Observe Character: {character}; Last Phoneme: {temp_phoneme}; Current Phoneme: {current_phoneme}; Phoneme {temp_phoneme} completed. Syllable {syllable} completed."
                )
            else:
                self.print(
                    f"Observe Character: {character}; Last Phoneme: {temp_phoneme}; Current Phoneme: {current_phoneme}; Phoneme {temp_phoneme} completed."
                )

            # prepare for next iteration
            temp_character = character  # clear the temp_character and add the current character to it
            temp_phoneme = self._ipa_to_phoneme.get(temp_character, None)

        if temp_phoneme is not None:
            syllable.add_phoneme(temp_phoneme)
            if syllable.stress and not syllable.have_vowel:
                raise PhonemeError(
                    f"Got a stress but no vowel in syllable: {syllable}. IPA: {ipa}"
                )
            self.print(
                f"Last Phoneme: {temp_phoneme}; Phoneme {temp_phoneme} completed. Syllable {syllable} completed. (outside loop)"
            )
            out.append(syllable)
        else:
            raise PhonemeError(
                f'Unable to recognize the phoneme: {temp_character}. IPA: {ipa}'
            )

        if preserve_syllable:
            return [_.translate_to_arpabet() for _ in out]
        else:
            return list(" ".join([_.translate_to_arpabet()
                                  for _ in out]).split(" "))


from .espeak import get_ipa_transcriptions
from .segment import CharacterCategory

CONVERTER: Optional[IPA2ARPA] = None


def get_arpa(
    s: Union[List[str], str],
    preserve_syllable: bool = False,
    debug: bool = False,
    lang: CharacterCategory = CharacterCategory.LATIN,
) -> List[str]:
    global CONVERTER
    if CONVERTER is None:
        CONVERTER = IPA2ARPA()
    CONVERTER.debug = debug
    if isinstance(s, str):
        s = [s]
    ipa = get_ipa_transcriptions(
        phrases=s,
        preserve_suprasegmental=False,
        preserve_diacritics=False,
        lang=str(lang),
    )
    l = []
    for i in ipa:
        l += CONVERTER.convert(i, preserve_syllable=preserve_syllable)
    return l
