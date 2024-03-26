import re
import emoji
from src.text_processing.profanity_filter import process_text

def reformat_text(extracted_text):
    # Format text
    # Define a pattern to match the series and part
    pattern = r'Confession #(\d+)'
    match = re.search(pattern, extracted_text)

    if match:
        # Extract the series and part
        series = "Confessions"
        part = match.group(1)

        # Remove leading and trailing spaces
        extracted_text = extracted_text.strip()

        # Remove newlines and extra spaces
        cleaned_text = ' '.join(extracted_text.split())

        # converting emoji symbols to names
        converted_text = emoji.emojize(cleaned_text)

        # Use regex to remove the \u201c in the beginning
        cleaned_text = re.sub(r'(\u201c)', '', converted_text)

        # Use regex to the final \u201d before the location into a full stop
        cleaned_text = re.sub(r'(\u201d)', '.', cleaned_text)

        # Use regex to the final \u201d before the location into a full stop
        cleaned_text = re.sub(r'(\u2019|\u2018)', "'", cleaned_text)

        # Use regex to the final \u201d before the location into a full stop
        cleaned_text = re.sub(r'(\u00ae|\u00a9)', ', crying emoji', cleaned_text)

        # Replace '|' with 'I'
        cleaned_text = cleaned_text.replace('|', 'I')

        # Filter profanity and perform word replacement
        cleaned_text = process_text(cleaned_text)

        # Split the text into words
        words = cleaned_text.split()

        # Delete the first 2 words (if there are at least 3 words)
        if len(words) >= 3:
            del words[:2]

        # Join the remaining words back into text
        cleaned_text = ' '.join(words)

        return {
            "series": series,
            "part": part,
            "outro": "Visit www.myconfessions.co.za to anonymously confess",
            "text": cleaned_text
        }
