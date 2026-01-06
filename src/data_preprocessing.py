import re
import unicodedata
from khmernltk import sentence_tokenize
from transformers import AutoTokenizer

class TextCleaning:
    def __init__(self, sp_model="khopilot/km-tokenizer-khmer"):
        """
        Initialize the TextCleaning class.

        Args:
            sp_model (str): The Hugging Face model identifier for a SentencePiece tokenizer.
                             Default points to khopilot/km-tokenizer-khmer.
        """
        # load SentencePiece tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(sp_model, use_fast=False)

    def clean_normalize(self, text: str) -> str:
        """
        Normalize Unicode, remove excess spaces, and replace noisy patterns
        like URLs, emails, phone numbers, emojis with placeholders.

        Args:
            text (str): Raw Khmer text

        Returns:
            str: Cleaned text
        """
        # Unicode normalization (NFC)
        text = unicodedata.normalize("NFC", text)

        # Replace URLs
        text = re.sub(r"https?://\S+", " <URL> ", text)

        # Replace email addresses
        text = re.sub(r"\S+@\S+\.\S+", " <EMAIL> ", text)

        # Replace phone numbers (Latin and Khmer)
        text = re.sub(r"[0-9០១២៣៤៥៦៧៨៩\-]{6,}", " <PHONE> ", text)

        # Remove emojis and non-printable characters
        text = re.sub(r"(?<!\d)(?:0[0-9០១២៣៤៥៦៧៨៩](?:[ \-]?[0-9០១២៣៤៥៦៧៨៩]){7,8}|(?:\+?855)(?:[ \-]?[0-9០១២៣៤៥៦៧៨៩]){8,9})(?!\d)"," <PHONE> ",text)

        # Collapse multiple spaces into one
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def sentence_segmentation(self, text: str) -> str:
        """
        Perform Khmer sentence segmentation using khmer-nltk.

        Args:
            text (str): Cleaned text

        Returns:
            str: Sentences separated by newline
        """
        # use khmer-nltk sentence_tokenize
        sentences = sentence_tokenize(text)

        # join with newline or space
        return "\n".join(sentences)

    def tokenization(self, text: str) -> str:
        """
        Perform subword tokenization using a pretrained SentencePiece tokenizer.

        Args:
            text (str): Khmer sentence

        Returns:
            str: A space-joined list of tokens
        """
        # use the tokenizer to tokenize
        tokens = self.tokenizer.tokenize(text)

        # join tokens by space
        return " ".join(tokens)

    def lowercasing_mixed_handling(self, text: str) -> str:
        """
        Handle lowercasing for mixed Khmer + English text.
        English tokens are lowercased, Khmer tokens remain unchanged.

        Args:
            text (str): Raw or tokenized text

        Returns:
            str: Text with English tokens lowercased
        """
        def process_token(tok):
            # if token contains Latin letters, lowercase it
            return tok.lower() if re.search(r"[A-Za-z]", tok) else tok

        # split on whitespace
        tokens = text.split()
        processed_tokens = [process_token(t) for t in tokens]

        return " ".join(processed_tokens)


# Example input and output result 
# input = "អ្នក ចេះ និយាយ English ទេ? www.example.com 😊"
# output = អ្នក ចេះ និយាយ english ទេ
