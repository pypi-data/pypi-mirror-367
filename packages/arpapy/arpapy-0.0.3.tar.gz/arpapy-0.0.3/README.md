# arpapy

Multilingual text/IPA to ARPAbet G2P for text2speech generation.

## Installation
```bash
sudo apt install espeak-ng
pip install arpapy
```

## Quick Start

### Getting pronunciation

```python
from arpapy import get_arpa

s: str = '"Marron glacé is in my DNA." adiós'
print(get_arpa(s))
# ['M', 'AA1', 'R', 'AX0', 'N', '/', 'G', 'L', 'AA0', 'S', 'EY1', '/', 'IH0', 'Z', '/', 'IH0', 'N', '/', 'M', 'AY0', '/', 'D', 'IY2', 'EH2', 'N', 'EY1', '-', 'EY1', 'D', 'IH0', 'AX2', 'UH0', 'Z']

s: str = 'あわてんのおつかい'
print(get_arpa(s, lang=CharacterCategory.JAPANESE)) # ['AA2', 'W', 'AA0', 'T', 'EY2', 'N', 'N', 'OW0', 'OW0', 'T', 'S', 'UW0', 'V', 'K', 'AA1', 'IY0']
```

### Segmenting Languages

```python
from arpapy import segment_string, CharacterCategory

test_string = "😊yo ♠你好hello, 人😊♠ 出自日本童谣'あわてん坊のおつかい'"
result = segment_string(test_string, [CharacterCategory.LATIN, CharacterCategory.CHINESE, CharacterCategory.JAPANESE])
print(result)
# [('yo ♠', <CharacterCategory.LATIN: 5>), ('你好', <CharacterCategory.CHINESE: 2>), ('hello, ', <CharacterCategory.LATIN: 5>), ("人😊♠ 出自日本童谣'", <CharacterCategory.CHINESE: 2>), ('あわてん', <CharacterCategory.JAPANESE: 3>), ('坊', <CharacterCategory.CHINESE: 2>), ("のおつかい'", <CharacterCategory.JAPANESE: 3>)]
```

### Limitation
Some of the convertion from IPA to ARPA might be inaccurate or out of scope, which might result in `arpapy.excepts.PhonemeError: Unable to recognize the phoneme`. If this is the case, please submit a PR according to [IPA consonant chart with audio](https://en.wikipedia.org/wiki/IPA_consonant_chart_with_audio).

Language scope: (If there is any error within the scope, I'll fix it.)
- All standard English
- All Chinese
- All Japanese Hiragana, Katakana
- Some western languages (Spanish, German, etc...)
- Some korean (not tested)

Future:
- Support Japanese Kanji

## Citation

See [CREADITS.md](CREDITS.md) for all credits.

```
@misc{arpapy,
  title={arpapy: Multilingual text/IPA to ARPAbet G2P for text2speech generation.},
  author={Koke_Cacao},
  year={2025},
  howpublished={\url{https://github.com/KokeCacao/arpapy}},
  note={Open-source software}
}
```
