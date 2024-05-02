import xml.etree.ElementTree as ET
import os


class VanillaLanguageModel:
    def __init__(self, directory):
        self.directory = directory
        self.text = self._parse_xml_files()

    def _parse_xml_files(self):
        xml_files = self._get_xml_files()
        text = ""
        for xml_file in xml_files:
            text += self._parse_xml(xml_file)
        return text

    def _get_xml_files(self):
        xml_files = []
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".xml"):
                    xml_files.append(os.path.join(root, file))
        return xml_files

    def _parse_xml(self, xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        text = ""
        for wtext in root.findall(".//wtext"):
            text += " ".join(w.text for w in wtext.findall(".//w") if w.text is not None)
        return text

    def _count_ngrams(self, text, n):
        ngrams = self._tokenize(text, n)
        ngram_counts = {}
        for gram in ngrams:
            if gram in ngram_counts:
                ngram_counts[gram] += 1
            else:
                ngram_counts[gram] = 1
        return ngram_counts

    def _tokenize(self, text, n):
        tokens = text.split()
        ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
        return ngrams

    def train(self):
        self.unigram_counts = self._count_ngrams(self.text, 1)
        self.bigram_counts = self._count_ngrams(self.text, 2)
        self.trigram_counts = self._count_ngrams(self.text, 3)

    def get_top_ngrams(self, ngram_type, top_n=10):
        if ngram_type == 'unigram':
            ngram_counts = self.unigram_counts
        elif ngram_type == 'bigram':
            ngram_counts = self.bigram_counts
        elif ngram_type == 'trigram':
            ngram_counts = self.trigram_counts
        else:
            raise ValueError("Invalid ngram_type. Choose from 'unigram', 'bigram', or 'trigram'.")

        return sorted(ngram_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]


model = VanillaLanguageModel(os.path.join("British National Corpus, Baby edition", "Texts"))
model.train()

print("Top 10 Unigrams:", model.get_top_ngrams('unigram'))
print("Top 10 Bigrams:", model.get_top_ngrams('bigram'))
print("Top 10 Trigrams:", model.get_top_ngrams('trigram'))


class LaplaceLanguageModel(VanillaLanguageModel):
    def __init__(self, directory, k=1):
        super().__init__(directory)
        self.k = k

    def _count_ngrams(self, text, n):
        ngrams = self._tokenize(text, n)
        ngram_counts = {}
        total_ngrams = len(ngrams)

        for gram in set(ngrams):
            ngram_counts[gram] = self.k

        for gram in ngrams:
            ngram_counts[gram] += 1

        vocab_size = len(set(ngrams))
        for gram in ngram_counts:
            ngram_counts[gram] /= (total_ngrams + self.k * vocab_size)

        return ngram_counts


laplace_model = LaplaceLanguageModel(os.path.join("British National Corpus, Baby edition", "Texts"), k=1)
laplace_model.train()

print("Top 10 Unigrams with Laplace Smoothing:", laplace_model.get_top_ngrams('unigram'))
print("Top 10 Bigrams with Laplace Smoothing:", laplace_model.get_top_ngrams('bigram'))
print("Top 10 Trigrams with Laplace Smoothing:", laplace_model.get_top_ngrams('trigram'))


class UNKLanguageModel(VanillaLanguageModel):
    def __init__(self, directory):
        super().__init__(directory)
        self.unk_threshold = 2

    def _count_words(self, text):
        word_counts = {}
        for word in text.split():
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
        return word_counts

    def _replace_rare_words(self, text, word_counts):
        replaced_text = ""
        for word in text.split():
            if word_counts[word] <= self.unk_threshold:
                replaced_text += "<UNK> "
            else:
                replaced_text += word + " "
        return replaced_text.strip()

    def train(self):
        self.text = self._parse_xml_files()
        word_counts = self._count_words(self.text)
        self.text = self._replace_rare_words(self.text, word_counts)
        super().train()


unk_model = UNKLanguageModel(os.path.join("British National Corpus, Baby edition", "Texts"))
unk_model.train()

print("Top 10 Unigrams after replacing rare words with <UNK>:", unk_model.get_top_ngrams('unigram'))
print("Top 10 Bigrams after replacing rare words with <UNK>:", unk_model.get_top_ngrams('bigram'))
print("Top 10 Trigrams after replacing rare words with <UNK>:", unk_model.get_top_ngrams('trigram'))

# Apply Laplace smoothing to the UNK Language Model
laplace_unk_model = LaplaceLanguageModel(os.path.join("British National Corpus, Baby edition", "Texts"), k=1)
laplace_unk_model.text = unk_model.text
laplace_unk_model.train()

print("Top 10 Unigrams with Laplace Smoothing after replacing rare words with <UNK>:", laplace_unk_model.get_top_ngrams('unigram'))
print("Top 10 Bigrams with Laplace Smoothing after replacing rare words with <UNK>:", laplace_unk_model.get_top_ngrams('bigram'))
print("Top 10 Trigrams with Laplace Smoothing after replacing rare words with <UNK>:", laplace_unk_model.get_top_ngrams('trigram'))