import re
from enum import Enum, auto
from typing import List, Tuple, Iterable

# Define the CharacterCategory Enum
class CharacterCategory(Enum):
    PUNCTUATION = auto()
    CHINESE = auto()
    JAPANESE = auto()
    KOREAN = auto()
    LATIN = auto()
    NON_LATIN = auto()
    MATH_SYMBOL = auto()
    SYMBOLS_EMOJI = auto()
    UNKNOWN = auto()
    
    def __str__(self):
        if self == CharacterCategory.PUNCTUATION:
            return "en-us"
        elif self == CharacterCategory.CHINESE:
            return "cmn"
        elif self == CharacterCategory.JAPANESE:
            return "ja"
        elif self == CharacterCategory.KOREAN:
            return "ko"
        elif self == CharacterCategory.LATIN:
            return "en-us"
        elif self == CharacterCategory.NON_LATIN:
            return "en-us"
        elif self == CharacterCategory.MATH_SYMBOL:
            return "en-us"
        elif self == CharacterCategory.SYMBOLS_EMOJI:
            return "en-us"
        else:
            return "en-us"

# Define categorize_character function
def categorize_character(char: str) -> CharacterCategory:
    """Categorizes a single character into one of the following categories:

    Args:
        char (str): A single character to categorize.

    Raises:
        ValueError: If the input is not a single character.

    Returns:
        CharacterCategory: The category of the input character.
    """
    if len(char) != 1:
        raise ValueError("Input must be a single character.")

    # Regex for punctuation in any language
    punctuation_regex = r"[^\w\s]"
    # Regex for Chinese
    chinese_regex = r"^[\u4E00-\u9FFF]+$"
    # Japanese Hiragana and Katakana
    japanese_regex = r"^[\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF]+$"
    # Korean Hangul
    korean_regex = r"^[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]+$"
    # Regex for English/Italian/Spanish-like characters (Latin script with accents)
    latin_regex = r"[A-Za-z\u00C0-\u017F]"
    # Regex for Non-Latin Alphabets (Cyrillic, Greek, Hebrew, etc.)
    non_latin_regex = r"[\u0400-\u04FF\u0370-\u03FF\u0590-\u05FF\u0600-\u06FF\u0900-\u097F\u0E00-\u0E7F]"
    # Regex for Mathematical Symbols
    math_symbols_regex = r"[+\-*/=<>∑√∫∞∂π±≠≈≡]"
    # Regex for Symbols/Emoji (Emojis, arrows, and miscellaneous symbols)
    symbols_emoji_regex = r"[\u2600-\u26FF\u2700-\u27BF\u2190-\u21FF\u1F600-\u1F64F\u1F680-\u1F6FF\u1F300-\u1F5FF]"

    if re.match(punctuation_regex, char):
        return CharacterCategory.PUNCTUATION
    elif re.match(chinese_regex, char):
        return CharacterCategory.CHINESE
    elif re.match(japanese_regex, char):
        return CharacterCategory.JAPANESE
    elif re.match(korean_regex, char):
        return CharacterCategory.KOREAN
    elif re.match(latin_regex, char):
        return CharacterCategory.LATIN
    elif re.match(non_latin_regex, char):
        return CharacterCategory.NON_LATIN
    elif re.match(math_symbols_regex, char):
        return CharacterCategory.MATH_SYMBOL
    elif re.match(symbols_emoji_regex, char):
        return CharacterCategory.SYMBOLS_EMOJI
    else:
        return CharacterCategory.UNKNOWN

def categorize_string(input_string: str) -> List[Tuple[str, CharacterCategory]]:
    """Categorizes each character in a string into one of the following categories:

    Args:
        input_string (str): The input string to categorize.

    Returns:
        List[Tuple[str, CharacterCategory]]: A list of tuples containing the character and its category.
    """
    if not input_string:
        return []

    categorized_result = []
    current_category = None
    current_group = ""

    for char in input_string:
        char_category = categorize_character(char)
        
        # If the category changes, save the current group and start a new one
        if char_category != current_category:
            if current_group:
                categorized_result.append((current_group, current_category))
            current_group = char
            current_category = char_category
        else:
            current_group += char

    # Append the last group
    if current_group:
        categorized_result.append((current_group, current_category))

    return categorized_result

def segment_string(s: str, foreground_category: Iterable[CharacterCategory]) -> List[Tuple[str, CharacterCategory]]:
    """
    Segments a string such that only foreground_categories are preserved as segment labels.
    All background categories between two **same** foreground categories are merged into
    that same foreground category's segment.

    Steps:
      1) Calls `categorize_string` to split the input into (lump, category) pairs.
      2) Identifies indices where the lump's category is in the given foreground_category set.
      3) Merges consecutive lumps that have the same foreground category (absorbing all
         background lumps in between).
      4) Returns a list of (combined_text, foreground_category) pairs.
    """
    # 1) Categorize the entire string into lumps of (text, category).
    lumps = categorize_string(s)
    if not lumps:
        return []
    
    # 1.1) If there is a CharacterCategory.CHINESE that is less than 3 characters and surrounded by CharacterCategory.JAPANESE,
    #      on both sides, then turn it into CharacterCategory.JAPANESE.
    for i in range(1, len(lumps) - 1):
        if (lumps[i][1] == CharacterCategory.CHINESE and
            lumps[i - 1][1] == CharacterCategory.JAPANESE and
            lumps[i + 1][1] == CharacterCategory.JAPANESE and
            len(lumps[i][0]) < 3):
            lumps[i] = (lumps[i][0], CharacterCategory.JAPANESE)

    # Convert the iterable to a set for quick membership checks.
    foreground_set = set(foreground_category)

    # 2) Gather the indices where the lump category is in the foreground set.
    foreground_indices = [
        i for i, (_, cat) in enumerate(lumps)
        if cat in foreground_set
    ]

    # If there are no foreground lumps, treat the lumps as the first foreground lump
    if not foreground_indices:
        foreground_indices = [0]

    result_segments = []

    # 3) Build segments by merging lumps that share the same foreground category
    #    (including all background lumps between them).
    i = 0
    while i < len(foreground_indices):
        current_fg_idx = foreground_indices[i]
        current_fg_cat = lumps[current_fg_idx][1]

        # Move j forward while the next foreground index has the same category
        # (i.e., lumps[foreground_indices[j]].category == current_fg_cat).
        j = i + 1
        while j < len(foreground_indices) and lumps[foreground_indices[j]][1] == current_fg_cat:
            j += 1

        # If we stopped because we reached a different foreground category 
        # or ran out of lumps, define end_idx accordingly.
        if j < len(foreground_indices):
            end_idx = foreground_indices[j]  # We'll merge up until just before that index
        else:
            end_idx = len(lumps)  # Merge until the end of the lumps

        # Merge everything from current_fg_idx up to end_idx
        segment_text = "".join(lumps[idx][0] for idx in range(current_fg_idx, end_idx))
        result_segments.append((segment_text, current_fg_cat))

        # Advance i to j to handle the next distinct foreground category group.
        i = j

    return result_segments

if __name__ == "__main__":
    test_string = "😊yo ♠你好hello, 人😊♠ 出自日本童谣'あわてん坊のおつかい'"
    result = segment_string(test_string, [CharacterCategory.LATIN, CharacterCategory.CHINESE, CharacterCategory.JAPANESE])
    print(result)
    # [('yo ♠', <CharacterCategory.LATIN: 5>), ('你好', <CharacterCategory.CHINESE: 2>), ('hello, ', <CharacterCategory.LATIN: 5>), ("人😊♠ 出自日本童谣'", <CharacterCategory.CHINESE: 2>), ('あわてん', <CharacterCategory.JAPANESE: 3>), ('坊', <CharacterCategory.CHINESE: 2>), ("のおつかい'", <CharacterCategory.JAPANESE: 3>)]