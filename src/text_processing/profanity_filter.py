import re

def process_text(text):
    word_replacements = {
        "fuck": "eff",
        "shit": "poop",
        "sexual experience": "intercourse",
        "sexual": "you know",
        "sexy": "tempting",
        "seggs": "lovemaking",
        "sex": "lovemaking",
        "blowjob": "oral",
        "blow job": "oral",
        "pussy": "vaj",
        "cock": "willie",
        "dick": "willie",
        "cumshot": "bust-shot",
        "cumming": "busting",
        "cum": "bust",
        "squirt": "flow",
        "porn": "lewd videos",
        "masturbation": "self-stimulation",
        "anal": "back",
        "fucking": "flippin",
        "|":"I",
        "masturbating":"playing with myself",
        "masturbate":"self-stimulate",
        '"':"'",
    }

    # Perform word replacement for profanity, case-insensitive
    for profane_word, replacement_word in word_replacements.items():
        text = re.sub(re.escape(profane_word), replacement_word, text, flags=re.IGNORECASE)

    return text