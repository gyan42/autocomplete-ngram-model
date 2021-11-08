import json
from collections import Counter
from collections import defaultdict
import nltk 
from tqdm import tqdm

class AutoCorrectModel(object):
  def __init__(self, 
               unknown_token='<unk>',
               start_token='<s>',
               end_token='<e>',
               k=1):
    self._unknown_word = '<unk>'
    self._start_token = start_token
    self._end_token = end_token

    self._tokenized_sentences = None
    self._k = k # smoothing prameter

    self._word_frequency = Counter() # keys are the closed vocab

    self._ngram_word_frequency = defaultdict(lambda: 0)
    self._ngram_plus1_word_frequency = defaultdict(lambda: 0)

    self._no_match_threshold = 5

  def tokenize(self, sentences):
    # Tokenize the sentences
    self._tokenized_sentences = [nltk.word_tokenize(sentence.lower()) for sentence in tqdm(sentences, desc="Tokenize")]

  def train(self, minimum_freq=5, ngram=3):
    self._minimum_freq = minimum_freq
    self._ngram = ngram

    # Prepare word vocab through frequency counter
    self._calculate_word_frequency()
    self._vocab = list( self._word_frequency.keys()) + [self._unknown_word, "<e>"]
    
    #self._filter_low_freq_words() # TODO enable to simulate unknown words 

    # Normalize data i.e replace less frequent words with unknown tag
    self._tokenized_sentences = self._tokenize_n_normalize(self._tokenized_sentences)

    # Prepare ngram word frequency
    self._ngram_word_frequency = self._count_n_grams(self._tokenized_sentences, self._ngram)
    self._ngram_plus1_word_frequency = self._count_n_grams(self._tokenized_sentences, self._ngram+1)


  def _calculate_word_frequency(self):
    '''
    Counts word counts
    '''
    for tokenized_sentence in tqdm(self._tokenized_sentences, desc="Word Frequency"):
      self._word_frequency.update(tokenized_sentence)

  def _filter_low_freq_words(self):
    '''
    Filter words whose count are less than threshold
    '''
    words = self._word_frequency.keys()
    words_to_be_deleted = []

    for word in words:
      if self._word_frequency[word] < self._minimum_freq:
          words_to_be_deleted.append(word)
    
    for word in words_to_be_deleted:
      del self._word_frequency[word]

  def _tokenize_n_normalize(self, tokenized_sentences):
    '''
    Remove all words which not part of vocab and replace it with unknown tag
    '''
    new_sentences = []
    for sentence in tqdm(tokenized_sentences, desc="Normalize"):
      new_sentence = []
      for token in sentence:
        if self._word_frequency[token] != 0:
          new_sentence.append(token)
        else:
          new_sentence.append(self._unknown_word)
      new_sentences.append(new_sentence)
    return new_sentences

  def _count_n_grams(self, tokenized_sentences, ngram):
    '''
    Creates n-gram from tokenized sentence and counts the same
    '''
    freq = defaultdict(lambda: 0)
    for sentence in tqdm(tokenized_sentences, desc="NGrams"):
      sentence = [self._start_token] * ngram + sentence + [self._end_token]
      m = len(sentence) if ngram == 1 else len(sentence) - 1
      for i in range(m):
        ngram_token = sentence[i:i+ngram]
        #freq[tuple(ngram_token)] += 1
        # tuples can't be used as key in JSON
        freq[" ".join(ngram_token)] += 1
    return freq

  def _estimate_probability(self, word, previous_ngram):
    vocab_size = len(self._word_frequency)
    #previous_ngram = tuple(previous_ngram)
    if type(previous_ngram) != list:
      previous_ngram = [previous_ngram]
    previous_ngram = " ".join(previous_ngram)
    previous_ngram_count = self._ngram_word_frequency.get(previous_ngram, 0)
    if previous_ngram_count == 0:
      # print("Warning no match found for entered words!")
      return 0
    denominator = previous_ngram_count + self._k * len(self._vocab)
    n_plus1_gram = previous_ngram + " " + word
    n_plus1_gram_count =  self._ngram_plus1_word_frequency.get(n_plus1_gram, 0)
    numerator = n_plus1_gram_count + self._k
    probability = numerator / denominator
    return probability

  def _estimate_probabilities(self, previous_ngram):
    probabilities = {}
    # previous_n_gram = tuple(previous_n_gram)
    if type(previous_ngram) != list:
      previous_ngram = [previous_ngram]
    previous_ngram = " ".join(previous_ngram).lower()
    for word in self._vocab:
      probabilities[word] = self._estimate_probability(word, previous_ngram)
    return probabilities

  def suggestions(self, previous_tokens, num_suggestions=5, start_with=None):
    previous_ngram = previous_tokens[-self._ngram:]
    probabilities = self._estimate_probabilities(previous_ngram)
    probs = probabilities.items()
    probs = filter(lambda t: t[1]>0, probs)
    if start_with:
       probs = filter(lambda t: t[0].startswith(start_with), probs)
    probs = sorted(probs, key=lambda t: t[1], reverse=True)
    words = map(lambda t: t[0], probs)
    words = list(words)
    return words[:num_suggestions]


  def save_as_json(self, name):
    data = {}
    data["ngram_word_frequency"] = self._ngram_word_frequency #json.dumps(self._ngram_word_frequency, indent = 4)  
    data["ngram_plus1_word_frequency"] = self._ngram_plus1_word_frequency #json.dumps(self._ngram_plus1_word_frequency, indent = 4)  
    data["vocab"] = self._vocab
    data["ngram"] = self._ngram

    with open(name, "w", encoding='utf-8') as file:
      json.dump(data, file, ensure_ascii=False, indent=4)

  def load_from_json(self, file_path):
    data = json.load(open(file_path))
    self._ngram_word_frequency = data["ngram_word_frequency"]
    self._ngram_plus1_word_frequency =data["ngram_plus1_word_frequency"] 
    self._vocab = data["vocab"]
    self._ngram = data["ngram"]



