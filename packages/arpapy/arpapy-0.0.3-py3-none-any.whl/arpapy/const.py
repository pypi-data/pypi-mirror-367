from .model.phoneme import Phoneme
from .model.stress import Stress

vowels = [
    Phoneme(arpabet='AA', ipa='ɑ', is_vowel=True),
    Phoneme(arpabet='AA', ipa='a', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='AA', ipa='ɶ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='AA', ipa='ä', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='AA', ipa='ɒ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='AE', ipa='æ', is_vowel=True),
    Phoneme(arpabet='AE', ipa='ɐ', is_vowel=True),
    Phoneme(arpabet='AH', ipa='ʌ', is_vowel=True),
    Phoneme(arpabet='AO', ipa='ɔ', is_vowel=True),
    Phoneme(arpabet='AW', ipa='aʊ', is_vowel=True),
    Phoneme(arpabet='AX', ipa='ə', is_vowel=True),
    Phoneme(arpabet='AXR', ipa='ɚ',
            is_vowel=True),  # added by Koke_Cacao (not used)
    Phoneme(arpabet='ER', ipa='ər', is_vowel=True),
    Phoneme(arpabet='AY', ipa='aɪ', is_vowel=True),
    Phoneme(arpabet='EH', ipa='ɛ', is_vowel=True),  # modified by Koke_Cacao
    Phoneme(arpabet='EH', ipa='œ', is_vowel=True),  # modified by Koke_Cacao
    Phoneme(arpabet='ER', ipa='ɜr', is_vowel=True),
    Phoneme(arpabet='ER', ipa='ɜ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='ER', ipa='ɤ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='ER', ipa='ɞ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='EY', ipa='eɪ', is_vowel=True),
    Phoneme(arpabet='EY', ipa='e', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='IH', ipa='ɪ', is_vowel=True),
    Phoneme(arpabet='IX', ipa='ɨ', is_vowel=True),
    Phoneme(arpabet='IY', ipa='i:', is_vowel=True),
    Phoneme(arpabet='IY', ipa='i', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='OW', ipa='oʊ', is_vowel=True),
    Phoneme(arpabet='OW', ipa='o', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='OW', ipa='əl', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='OY', ipa='ɔɪ', is_vowel=True),
    Phoneme(arpabet='UH', ipa='ʊ', is_vowel=True),
    Phoneme(arpabet='UH', ipa='ɵ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='UH', ipa='ɘ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='UH', ipa='ᵻ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='UH', ipa='ø', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='UW', ipa='u', is_vowel=True),
    Phoneme(arpabet='UW', ipa='ɯ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='UX', ipa='ʉ', is_vowel=True),
    Phoneme(arpabet='UX', ipa='ʏ', is_vowel=True),  # added by Koke_Cacao
    Phoneme(arpabet='UX', ipa='y', is_vowel=True),  # added by Koke_Cacao
]

consonants = [
    Phoneme(arpabet='B', ipa='b', is_vowel=False),
    Phoneme(arpabet='CH', ipa='tʃ', is_vowel=False),
    Phoneme(arpabet='D', ipa='d', is_vowel=False),
    Phoneme(arpabet='DH', ipa='ð', is_vowel=False),
    Phoneme(arpabet='DX', ipa='ɾ', is_vowel=False),
    Phoneme(arpabet='F', ipa='f', is_vowel=False),
    Phoneme(arpabet='G', ipa='ɡ', is_vowel=False),  # not used
    Phoneme(arpabet='G', ipa='g', is_vowel=False),  # added by Koke_Cacao
    Phoneme(arpabet='HH', ipa='h', is_vowel=False),
    Phoneme(arpabet='JH', ipa='dʒ', is_vowel=False),
    Phoneme(arpabet='K', ipa='k', is_vowel=False),
    Phoneme(arpabet='L', ipa='l', is_vowel=False),
    Phoneme(arpabet='M', ipa='m', is_vowel=False),
    Phoneme(arpabet='M', ipa='ɱ', is_vowel=False),  # added by Koke_Cacao
    Phoneme(arpabet='N', ipa='n', is_vowel=False),
    Phoneme(arpabet='N', ipa='ɳ', is_vowel=False),  # added by Koke_Cacao
    Phoneme(arpabet='NX', ipa='ŋ', is_vowel=False),  # modified by Koke_Cacao
    Phoneme(arpabet='NX', ipa='ɴ', is_vowel=False),  # added by Koke_Cacao
    Phoneme(arpabet='P', ipa='p', is_vowel=False),
    Phoneme(arpabet='Q', ipa='ʔ', is_vowel=False),
    Phoneme(arpabet='R', ipa='ɹ', is_vowel=False),
    Phoneme(arpabet='R', ipa='r', is_vowel=False),  # added by Koke_Cacao
    Phoneme(arpabet='S', ipa='s', is_vowel=False),
    Phoneme(arpabet='SH', ipa='ʃ', is_vowel=False),
    Phoneme(arpabet='SH', ipa='ɬ', is_vowel=False),  # added by Koke_Cacao
    Phoneme(arpabet='SH', ipa='x', is_vowel=False),  # added by Koke_Cacao
    Phoneme(arpabet='T', ipa='t', is_vowel=False),
    Phoneme(arpabet='TH', ipa='θ', is_vowel=False),
    Phoneme(arpabet='V', ipa='v', is_vowel=False),
    Phoneme(arpabet='V', ipa='ᵝ', is_vowel=False), # added by Koke_Cacao
    Phoneme(arpabet='W', ipa='w', is_vowel=False),
    Phoneme(arpabet='WH', ipa='ʍ', is_vowel=False),
    Phoneme(arpabet='Y', ipa='j', is_vowel=False),
    Phoneme(arpabet='Z', ipa='z', is_vowel=False),
    Phoneme(arpabet='ZH', ipa='ʒ', is_vowel=False),

    # all are added by Koke_Cacao
    Phoneme(arpabet='K', ipa='c', is_vowel=False),
]

auxiliary = [
    Phoneme(arpabet='/', ipa=' ', is_vowel=False), # "hello/there/how/are/you"
    Phoneme(arpabet='-', ipa='\n', is_vowel=False), # "Hello - how are you?"
]

stress_ipa = {
    "'": Stress.Primary,
    "ˈ": Stress.Primary,
    'ˌ': Stress.Secondary,
}


suprasegmental_duration_ipa = [
    "ː",  # long
    "ˑ",  # half-long
    "◌̆",  # extra-short
]
suprasegmental_prosodic_ipa = [
    "|",  # minor (foot) group (short break)
    "‖",  # major (intonation) group (long break)
    ".",  # syllable break
    "‿",  # link (absence of a break)
]
suprasegmental_pitch_ipa = [
    "↗︎",  # global rise
    "↘︎",  # global fall
]

# diacritics
airstream_diacritics__ipa = [_[-1] for _ in ["◌ʼ"]]
syllabicity_diacritics_ipa = [
    _[-1] for _ in [
        "◌̩",
        "◌̍"  # syllabic
        "◌̯",
        "◌̑"  # non-syllabic
    ]
]
consonant_release_diacritics_ipa = [
    _[-1] for _ in [
        "◌ʰ",  # aspirated
        "◌ⁿ",  # nasal release
        "◌ᶿ",  # Voiceless dental fricative release
        "◌ᵊ",  # Mid central vowel release
        "◌̚",  # No audible release
        "◌ˡ",  # Lateral release
        "◌ˣ",  # Voiceless velar fricative release
    ]
]
phonation_diacritics_ipa = [
    _[-1] for _ in [
        "◌̥",
        "◌̊",  # Voiceless
        "◌̤",  # Breathy voiced
        "◌̬",  # Voiced
        "◌̰",  # Creaky voiced
    ]
]
articulation_diacritics_ipa = [
    _[-1] for _ in [
        "◌̪",
        "◌͆",  # Dental
        "◌̺",  # Apical
        "◌̟",
        "◌᫈",  # Advanced
        "◌̈",  # Centralized
        "◌̝",
        "◌˔",  # Raised
        "◌̼",  # Linguolabial
        "◌̻",  # Laminal
        "◌̠",
        "◌᫢",  # Retracted (backed)
        "◌̽",  # Mid-centralized
        "◌̞",
        "◌˕",  # Lowered
    ]
]
coarticulation_diacritics_ipa = [
    _[-1] for _ in [
        "◌̹",
        "◌͗",  # More rounded
        "◌ʷ",  # Labialized
        "◌ˠ",  # Velarized
        "◌ˤ",  # Pharyngealized
        "◌̘",
        "◌꭪",  # Advanced tongue root
        "◌̃",  # Nasalized
        "◌̜",
        "◌͑",  # Less rounded
        "◌ʲ",  # Palatalized
        "◌̴",  # Velarized or pharyngealized
        "◌̙",
        "◌꭫",  # Rhotacized
        "◌˞",  # Rhoticity
    ]
]
all_diacritics_ipa = airstream_diacritics__ipa + syllabicity_diacritics_ipa + consonant_release_diacritics_ipa + phonation_diacritics_ipa + articulation_diacritics_ipa + coarticulation_diacritics_ipa
