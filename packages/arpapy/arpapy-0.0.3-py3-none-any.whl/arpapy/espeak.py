# -*- coding: utf-8 -*-
import subprocess

from .excepts import MissingLibrary
from .util import remove_suprasegmental, remove_diacritics

from typing import List

# Pty Language       Age/Gender VoiceName          File                 Other Languages
#  5  af              --/M      Afrikaans          gmw/af               
#  5  am              --/M      Amharic            sem/am               
#  5  an              --/M      Aragonese          roa/an               
#  5  ar              --/M      Arabic             sem/ar               
#  5  as              --/M      Assamese           inc/as               
#  5  az              --/M      Azerbaijani        trk/az               
#  5  ba              --/M      Bashkir            trk/ba               
#  5  bg              --/M      Bulgarian          zls/bg               
#  5  bn              --/M      Bengali            inc/bn               
#  5  bpy             --/M      Bishnupriya_Manipuri inc/bpy              
#  5  bs              --/M      Bosnian            zls/bs               
#  5  ca              --/M      Catalan            roa/ca               
#  5  cmn             --/M      Chinese_(Mandarin) sit/cmn              (zh-cmn 5)(zh 5)
#  5  cs              --/M      Czech              zlw/cs               
#  5  cy              --/M      Welsh              cel/cy               
#  5  da              --/M      Danish             gmq/da               
#  5  de              --/M      German             gmw/de               
#  5  el              --/M      Greek              grk/el               
#  5  en-029          --/M      English_(Caribbean) gmw/en-029           (en 10)
#  2  en-gb           --/M      English_(Great_Britain) gmw/en               (en 2)
#  5  en-gb-scotland  --/M      English_(Scotland) gmw/en-GB-scotland   (en 4)
#  5  en-gb-x-gbclan  --/M      English_(Lancaster) gmw/en-GB-x-gbclan   (en-gb 3)(en 5)
#  5  en-gb-x-gbcwmd  --/M      English_(West_Midlands) gmw/en-GB-x-gbcwmd   (en-gb 9)(en 9)
#  5  en-gb-x-rp      --/M      English_(Received_Pronunciation) gmw/en-GB-x-rp       (en-gb 4)(en 5)
#  2  en-us           --/M      English_(America)  gmw/en-US            (en 3)
#  5  eo              --/M      Esperanto          art/eo               
#  5  es              --/M      Spanish_(Spain)    roa/es               
#  5  es-419          --/M      Spanish_(Latin_America) roa/es-419           (es-mx 6)(es 6)
#  5  et              --/M      Estonian           urj/et               
#  5  eu              --/M      Basque             eu                   
#  5  fa              --/M      Persian            ira/fa               
#  5  fa-latn         --/M      Persian_(Pinglish) ira/fa-Latn          
#  5  fi              --/M      Finnish            urj/fi               
#  5  fr-be           --/M      French_(Belgium)   roa/fr-BE            (fr 8)
#  5  fr-ch           --/M      French_(Switzerland) roa/fr-CH            (fr 8)
#  5  fr-fr           --/M      French_(France)    roa/fr               (fr 5)
#  5  ga              --/M      Gaelic_(Irish)     cel/ga               
#  5  gd              --/M      Gaelic_(Scottish)  cel/gd               
#  5  gn              --/M      Guarani            sai/gn               
#  5  grc             --/M      Greek_(Ancient)    grk/grc              
#  5  gu              --/M      Gujarati           inc/gu               
#  5  hak             --/M      Hakka_Chinese      sit/hak              
#  5  hi              --/M      Hindi              inc/hi               
#  5  hr              --/M      Croatian           zls/hr               (hbs 5)
#  5  ht              --/M      Haitian_Creole     roa/ht               
#  5  hu              --/M      Hungarian          urj/hu               
#  5  hy              --/M      Armenian_(East_Armenia) ine/hy               (hy-arevela 5)
#  5  hyw             --/M      Armenian_(West_Armenia) ine/hyw              (hy-arevmda 5)(hy 8)
#  5  ia              --/M      Interlingua        art/ia               
#  5  id              --/M      Indonesian         poz/id               
#  5  is              --/M      Icelandic          gmq/is               
#  5  it              --/M      Italian            roa/it               
#  5  ja              --/M      Japanese           jpx/ja               
#  5  jbo             --/M      Lojban             art/jbo              
#  5  ka              --/M      Georgian           ccs/ka               
#  5  kk              --/M      Kazakh             trk/kk               
#  5  kl              --/M      Greenlandic        esx/kl               
#  5  kn              --/M      Kannada            dra/kn               
#  5  ko              --/M      Korean             ko                   
#  5  kok             --/M      Konkani            inc/kok              
#  5  ku              --/M      Kurdish            ira/ku               
#  5  ky              --/M      Kyrgyz             trk/ky               
#  5  la              --/M      Latin              itc/la               
#  5  lfn             --/M      Lingua_Franca_Nova art/lfn              
#  5  lt              --/M      Lithuanian         bat/lt               
#  5  lv              --/M      Latvian            bat/lv               
#  5  mi              --/M      Māori             poz/mi               
#  5  mk              --/M      Macedonian         zls/mk               
#  5  ml              --/M      Malayalam          dra/ml               
#  5  mr              --/M      Marathi            inc/mr               
#  5  ms              --/M      Malay              poz/ms               
#  5  mt              --/M      Maltese            sem/mt               
#  5  my              --/M      Myanmar_(Burmese)  sit/my               
#  5  nb              --/M      Norwegian_Bokmål  gmq/nb               (no 5)
#  5  nci             --/M      Nahuatl_(Classical) azc/nci              
#  5  ne              --/M      Nepali             inc/ne               
#  5  nl              --/M      Dutch              gmw/nl               
#  5  om              --/M      Oromo              cus/om               
#  5  or              --/M      Oriya              inc/or               
#  5  pa              --/M      Punjabi            inc/pa               
#  5  pap             --/M      Papiamento         roa/pap              
#  5  pl              --/M      Polish             zlw/pl               
#  5  pt              --/M      Portuguese_(Portugal) roa/pt               (pt-pt 5)
#  5  pt-br           --/M      Portuguese_(Brazil) roa/pt-BR            (pt 6)
#  5  py              --/M      Pyash              art/py               
#  5  quc             --/M      K'iche'            myn/quc              
#  5  ro              --/M      Romanian           roa/ro               
#  5  ru              --/M      Russian            zle/ru               
#  2  ru-lv           --/M      Russian_(Latvia)   zle/ru-LV            
#  5  sd              --/M      Sindhi             inc/sd               
#  5  shn             --/M      Shan_(Tai_Yai)     tai/shn              
#  5  si              --/M      Sinhala            inc/si               
#  5  sk              --/M      Slovak             zlw/sk               
#  5  sl              --/M      Slovenian          zls/sl               
#  5  sq              --/M      Albanian           ine/sq               
#  5  sr              --/M      Serbian            zls/sr               
#  5  sv              --/M      Swedish            gmq/sv               
#  5  sw              --/M      Swahili            bnt/sw               
#  5  ta              --/M      Tamil              dra/ta               
#  5  te              --/M      Telugu             dra/te               
#  5  tn              --/M      Setswana           bnt/tn               
#  5  tr              --/M      Turkish            trk/tr               
#  5  tt              --/M      Tatar              trk/tt               
#  5  ur              --/M      Urdu               inc/ur               
#  5  uz              --/M      Uzbek              trk/uz               
#  5  vi              --/M      Vietnamese_(Northern) aav/vi               
#  5  vi-vn-x-central --/M      Vietnamese_(Central) aav/vi-VN-x-central  
#  5  vi-vn-x-south   --/M      Vietnamese_(Southern) aav/vi-VN-x-south    
#  5  yue             --/M      Chinese_(Cantonese) sit/yue              (zh-yue 5)(zh 8)

LANGS = set([
    "af",
    "am",
    "an",
    "ar",
    "as",
    "az",
    "ba",
    "bg",
    "bn",
    "bpy",
    "bs",
    "ca",
    "cmn",
    "cs",
    "cy",
    "da",
    "de",
    "el",
    "en-029",
    "en-gb",
    "en-gb-scotland",
    "en-gb-x-gbclan",
    "en-gb-x-gbcwmd",
    "en-gb-x-rp",
    "en-us",
    "eo",
    "es",
    "es-419",
    "et",
    "eu",
    "fa",
    "fa-latn",
    "fi",
    "fr-be",
    "fr-ch",
    "fr-fr",
    "ga",
    "gd",
    "gn",
    "grc",
    "gu",
    "hak",
    "hi",
    "hr",
    "ht",
    "hu",
    "hy",
    "hyw",
    "ia",
    "id",
    "is",
    "it",
    "ja",
    "jbo",
    "ka",
    "kk",
    "kl",
    "kn",
    "ko",
    "kok",
    "ku",
    "ky",
    "la",
    "lfn",
    "lt",
    "lv",
    "mi",
    "mk",
    "ml",
    "mr",
    "ms",
    "mt",
    "my",
    "nb",
    "nci",
    "ne",
    "nl",
    "om",
    "or",
    "pa",
    "pap",
    "pl",
    "pt",
    "pt-br",
    "py",
    "quc",
    "ro",
    "ru",
    "ru-lv",
    "sd",
    "shn",
    "si",
    "sk",
    "sl",
    "sq",
    "sr",
    "sv",
    "sw",
    "ta",
    "te",
    "tn",
    "tr",
    "tt",
    "ur",
    "uz",
    "vi",
    "vi-vn-x-central",
    "vi-vn-x-south",
    "yue",
])

KAKASI = None
def get_kakasi():
    global KAKASI
    if KAKASI is None:
        import pykakasi
        KAKASI = pykakasi.kakasi()
        return KAKASI
    else:
        return KAKASI

def to_hiragana(text: str) -> str:
    """
    Converts a given text to Hiragana using Kakasi.
    
    Args:
        text (str): The input text to convert.
    
    Returns:
        str: The converted Hiragana text.
    """
    kakasi = get_kakasi()
    assert kakasi is not None
    result = kakasi.convert(text)
    return "".join([item["hira"] for item in result]) # type: ignore[no-untyped-call]

def get_ipa_transcriptions(
    phrases: List[str],
    preserve_suprasegmental=False,
    preserve_diacritics=False,
    lang: str = "en-us",
) -> List[str]:
    """
    Converts a list of phrases into their IPA transcriptions using espeak-ng.
    
    Args:
        phrases (List[str]): A list of phrases to transcribe into IPA.
        preserve_suprasegmental (bool, optional): Whether to preserve suprasegmental features in the IPA transcriptions. Defaults to False.
        preserve_diacritics (bool, optional): Whether to preserve diacritics in the IPA transcriptions. Defaults to False.
    
    Returns:
        List[str]: A list of IPA transcriptions for each phrase.
    """
    ipa_transcriptions: List[str] = []
    if lang not in LANGS:
        raise ValueError(f"Language '{lang}' is not supported by espeak-ng. Please choose a language from the following list: {LANGS}")

    for phrase in phrases:
        if lang == "ja":
            # Convert Japanese text to Hiragana before passing it to espeak-ng
            phrase = to_hiragana(phrase)
        
        try:
            # Execute espeak-ng with the specified options
            result: subprocess.CompletedProcess = subprocess.run(
                ["espeak-ng", f"-v{lang}", "-x", phrase, "--ipa=3", "--sep=", "-q"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
            )
            if result.returncode != 0:
                raise RuntimeError(f"Subprocess failed with {result.stderr}")
            # Capture the IPA transcription from stdout
            ipa_transcriptions.append(result.stdout.strip())
        except Exception:
            # testing if espeak-ng is installed
            result: subprocess.CompletedProcess = subprocess.run(
                ["espeak-ng", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
            )
            if "espeak" not in result.stdout.lower():
                raise MissingLibrary("espeak-ng is not installed.")
            else:
                raise

    if not preserve_suprasegmental:
        ipa_transcriptions = [
            remove_suprasegmental(ipa)
            for ipa in ipa_transcriptions
        ]
    
    if not preserve_diacritics:
        ipa_transcriptions = [
            remove_diacritics(ipa)
            for ipa in ipa_transcriptions
        ]

    return ipa_transcriptions
