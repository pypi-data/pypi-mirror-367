from .const import vowels, consonants, auxiliary, all_diacritics_ipa, suprasegmental_duration_ipa, suprasegmental_prosodic_ipa, suprasegmental_pitch_ipa

remove_diacritics = lambda x: "".join(
    [i for i in x if i not in all_diacritics_ipa])

remove_duration = lambda x: "".join(
    [i for i in x if i not in suprasegmental_duration_ipa])
remove_prosodic = lambda x: "".join(
    [i for i in x if i not in suprasegmental_prosodic_ipa])
remove_pitch = lambda x: "".join(
    [i for i in x if i not in suprasegmental_pitch_ipa])
remove_suprasegmental = lambda x: remove_pitch(
    remove_prosodic(remove_duration(x)))
