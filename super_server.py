##############################CONFUSION SET############################################

from gensim.models import Word2Vec
import nltk
w2v = Word2Vec.load('word2vec_300_5.model')
bangla_words = set()
extras = set()
remove_letters = []
letters = []
priority = 1
def is_sounds_same(word, candidate):
    try:
        return doublemetaphone_encode(word) == doublemetaphone_encode(candidate)
    except:
        return False
def score(similarity, word, candidate):
    ds = nltk.edit_distance(word_cutter(word), word_cutter(candidate))
    if is_sounds_same(word, candidate):
        return abs(5 * priority * similarity / (ds + 1));
#    if ds >= 3:
#        ds = 2
    return abs(priority * similarity / (ds + 1));

def word_cutter(word):
    return word
    _result_word = ''
    for letter in word:
        if letter not in remove_letters:
            _result_word += letter
    return _result_word

def valid_bengali_words_acc_to_dic(word):
    __word = word
    if __word in bangla_words:
        return True
    extra = ''
    while len(__word) != 0:
        extra = __word[-1] + extra
        __word = __word[:-1]
        if __word in bangla_words and extra in extras:
            return True
    return False
def is_true_word(word):
    if word in w2v.wv.vocab and w2v.wv.vocab[word].count > 100:
        return True

    return False
def valid_bengali_words(words):
    return [word for word in words if valid_bengali_words_acc_to_dic(word) == True]
            
def read_letters():
    bengali_letters = open('bengali_letters.txt', 'r', encoding='utf-8')
    return [letter.strip() for letter in bengali_letters]

def read_bangla_words():
    bangla_words = open('bangla_words.txt', 'r', encoding='utf-8')
    return set(word.strip() for word in bangla_words)

def read_extras():
    extras = open('extra.txt', 'r', encoding='utf-8')
    return set(word.strip() for word in extras)

def candidates(word):
    candidates = set(valid_words for valid_words in get_phonetic_similar_words(word) if is_true_word(valid_words) == True)
    return candidates.union(known([word])).union(known(edits1(word))).union(known(edits2(word)))
#    return candidates.union(known([word])).union(known(edits1(word)))
def known(words): 
    return set(w for w in words if is_true_word(w))

def known2(words, word):
    return set(w for w in words if w in w2v.wv.vocab and doublemetaphone_encode(word) == doublemetaphone_encode(w))


def edits1(word):
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def read_remove_letters():
    remove_letters = open('remove_letters.txt', 'r', encoding='utf-8')
    return [letter.strip() for letter in remove_letters]
    

letters = read_letters()
bangla_words = read_bangla_words()
extras = read_extras()
remove_letters = read_remove_letters()

##############################PHONETIC ENCODER############################################
encodes = {"অ" :"o",  "আ": "a", "া": "a",  "ই": "i", "ঈ": "i", "ি":"i", "ী" : "i", "উ" : "u", "ঊ": "u", "ু": "u", "ূ": "u", "এ": "e", "ে": "e", "ঐ": "oi", "ৈ": "oi", "ও": "o", "ঔ": "ou","ৌ": "ou", "ক": "k", "খ": "k", "গ": "g", "ঘ": "g", "ঙ": "ng", "ং": "ng", "চ": "c", "ছ": "c", "য": "j", "জ": "j", "ঝ": "j", "ঞ": "n", "ট": "T", "ঠ": "T", "ড": "D", "ঢ": "D", "ঋ": "ri", "র": "r", "ড়": "r", "ঢ়": "r", "ন": "n", "ণ": "n", "ত": "t", "থ": "t", "দ": "d", "ধ": "d", "প": "p", "ফ": "p", "ব": "b", "ভ": "b", "ম": "m", "য়": "y", "ল": "l", "শ": "s", "স": "s", "ষ": "s", "হ": "h", "ঃ" : "h", "ৎ": "t", 'ৃ': 'ri'}


letters_tobe_checked = {'ক', 'য', 'ঞ', 'ব', 'ম', 'হ','ঃ'}

def soundex_encode(word):
	encoded_word = ""
	for w in word:
		encoded_word += encodes.get(w, "")
	return encoded_word
    
def doublemetaphone_encode(word):
	encoded_word = ""
	i, l = 0, len(word)
	while i<l:
		if word[i] not in letters_tobe_checked:
			encoded_word += encodes.get(word[i], "")
		elif word[i] == "ক":
			if word[i:i+3] == "ক্ষ":
				if i == 0:
					encoded_word += "k"
				else:
					encoded_word += "kk"
				i += 2
			else:
				encoded_word += "k"
		elif word[i] == "য":
			if word[i:i+2] == 'য়':
				encoded_word += "y"
			elif i != 0 and word[i-1:i+1] == '্য':
				if i == 2:
					encoded_word += "e"
				elif i-3>-1 and word[i-3] == '\u09CD':
					pass
				elif word[i-2] == 'র':
					encoded_word += "j"
				else:
					encoded_word += encoded_word[-1]
			else:
				encoded_word += "j"
		elif word[i] == "ঞ":
			if i != 0 and word[i-1] == '\u09CD':
				if word[i-2] == "জ":
					if i == 2 and i+1 != l and word[i+1] == "া":
						encoded_word = encoded_word[:-1] + "ge"
						i += 1
					else:
						encoded_word = encoded_word[:-1] + "gg"
				else:
					encoded_word += "n"
			elif i+1 != l and word[i+1] in {"া","আ", "ই","ি","ঈ","ী"}:
				pass
			else:
				encoded_word += "n"
				
		elif word[i] == "ব":
			if i != 0 and word[i-1] == '\u09CD':
				if i == 2 or (i-3>-1 and word[i-3] == '\u09CD'):
					pass
				elif word[i-2] in {'গ','ম'} or word[i-3:i+1] == 'উদ্ব':
					encoded_word += "b"
					
				else: encoded_word += encoded_word[-1]
			
			else: encoded_word += "b"
		
		elif word[i] == "ম":
			if i != 0 and word[i-1] == '\u09CD':
				if i == 2 or (i-3>-1 and word[i-3] == '\u09CD'):
					pass
				elif word[i-2] in {'ক', 'গ', 'ঙ', 'ট', 'ন', 'ণ', 'ল', 'স', 'শ', 'ষ'}:
					encoded_word += "m"
#				elif word[i-2] == 'ষ' and (i == l-1 or (i+1 == l-1 and word[i+1] in {"া","আ", "ই","ি","ঈ","ী"} ) ):
#					pass
				else: encoded_word += encoded_word[-1]
			else: 
				encoded_word += "m"
				
		elif word[i] == "হ":
			if word[i+1:i+2] == 'ৃ' or word[i+1:i+3] == '্র':
				pass
			elif word[i+1:i+3] == '্ণ' or word[i+1:i+3] == '্ন':
				encoded_word += "n"
			elif word[i+1:i+3] == '্ম':
				encoded_word += "m"
			elif word[i+1:i+3] == '্য':
				encoded_word += "j"
			elif word[i+1:i+3] == '্ল':
				encoded_word += "l"
			else:
				encoded_word += "h"
		
		elif word[i] == 'ঃ':
			if l<4 and i == l-1:
				encoded_word += "h"
			else:
				pass
		
		if i-1 > -1 and word[i-1] == 'ঃ':
			if i-1 != 0 and i-1 != l-1:
				encoded_word += encoded_word[-1]		 
		
		i += 1
	return encoded_word

similar_sounds = {}

def get_similar_sounds():
    for letter in encodes:
        if encodes[letter] not in similar_sounds:
            similar_sounds[encodes[letter]] = []
        similar_sounds[encodes[letter]].append(letter)
get_similar_sounds()

def generate_phonetic_similar_words(given_word, word, character_no, word_set):
    if character_no == len(given_word):
        word_set.add(word)
        return
    generate_phonetic_similar_words(given_word, word + given_word[character_no], character_no+ 1, word_set)
    
    try:
        for same in similar_sounds[encodes[given_word[character_no]]]:
            generate_phonetic_similar_words(given_word, word + same, character_no + 1, word_set)
    except:
        pass
        
def get_phonetic_similar_words(word):
    word_set = set()
    generate_phonetic_similar_words(word, '', 0, word_set)
    return word_set
##############################SERVER.PY############################################

from flask import Flask, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

def get_valid_context_words(context_words):
    return [valid_word for valid_word in context_words if valid_word in w2v.wv.vocab]


def get_suggestions(word, context_words):
    context_words = get_valid_context_words(context_words)
    suggestions = []
    for candidate in candidates(word):
        suggestions.append((score(w2v.wv.n_similarity([candidate], context_words), word, candidate), candidate))
    suggestions.sort(reverse = True)
#    top_five_score = [suggestion[0] for suggestion in suggestions[:5]]
    top_five_suggestions = [suggestion[1] for suggestion in suggestions[:100]]
    top_five_suggestions = valid_bengali_words(top_five_suggestions)
    top_five_suggestions = top_five_suggestions[:5]
#    print(top_five_score)
    print(top_five_suggestions)
    if word not in top_five_suggestions:
        return top_five_suggestions
    return top_five_suggestions;

def valid_bengali_letters(char):
    return ord(char) >= 2433 and ord(char) <= 2543

def get_replacement(char):
    if valid_bengali_letters(char):
        return char
    newlines = [10, 2404, 2405, 2551, 9576]
    if ord(char) in newlines:
        return '\n'
    return ' ';

def get_valid_lines(line):
    copy_line = ''
    for letter in line:
        copy_line += get_replacement(letter)
    return copy_line

def test():
    get_suggestions('স্কুলে', ['আমি' , 'যাই'])
    get_suggestions('ইস্কুলে',  ['আমি', ' যাই'] )
    get_suggestions('ইশকুলে', ['আমি',  'যাই'] )
    get_suggestions('পড়ে', ['সে',  'বই' ])
    get_suggestions('পরা', ['বই', 'উচিত'])


def temp(data):
    my_suggestions = []
    response = {}
#    try:
    my_suggestions = get_suggestions(data['word'], data['contexts'])
#    except:
#        response['status'] = 'fail'
#        response['suggestions'] = []
#        return response
    response['status'] = 'fail'
    response['suggestions'] = []
    if len(my_suggestions) == 0:
        return response
    response['status'] = 'fail'

    response['suggestions'] = my_suggestions
    print(response)
    return response

@app.route('/', methods=['POST'])
def calc():
    print('Got ', request.get_json())
    return temp(request.get_json())


if __name__ == '__main__':
    app.run(debug=False, threaded= False)

