import argparse
import math
import os
import random
import sys
from collections import Counter
import concurrent.futures
import re

# Constants
ETAOIN = "etaoinshrdlcumwfgypbvkjxqz"
COMMON_WORDS = {
    'the','of','and','to','in','a','that','is','was','for','on','as','with','by','at','from','it','be','an','this',
    'are','or','have','has','not','were','which','but','they','he','she','we','you','their','its','more','about',
    'new','year','percent','two','three','first','last','after','before','between','during','against','over',
    'market','price','company','government','report','people','states','united','china','india','global','growth',
    'policy','economic','health','research','university','technology','international','security','police','court',
    'team','game','season','city','state','country','world','officials','president','minister','prime','election',
    'party','parliament','law','rights','trade','bank','investors','shares','billion','million','dollars','euro',
    'oil','energy','climate','change','cases','covid','vaccine','study','data','analysis','chief','director',
    'announce','statement','according','including','however','while','because','since','although','could','would',
    'should','may','might','will','can','said','says','told','added','include','make','made','under','into','out',
    'over','back','down','up','across','through','today','yesterday','monday','tuesday','wednesday','thursday',
    'friday','saturday','sunday'
}

# --- Pure Python N-gram Scoring Function ---
def _score_sequence_pure_python(seq_ints_list, key_map_list, bigram_data_list, trigram_data_list, quadgram_data_list, w_bigram, w_trigram, w_quadgram):
    """
    Pure Python function for N-gram scoring.
    Expects all sequence and key data as Python lists.
    This version includes quadgram scoring and is micro-optimized for pure Python.
    """
    n = len(seq_ints_list)
    if n < 2:
        return -1e9 # Too short for bigrams

    s2 = 0.0
    c2 = 0
    s3 = 0.0
    c3 = 0
    s4 = 0.0
    c4 = 0

    # Precompute powers of 26 once to avoid repeated multiplication
    p26 = 26
    p26_2 = 26 * 26
    p26_3 = 26 * 26 * 26

    # Initialize sliding window characters (indices 0-25)
    # These represent the *plaintext* characters after decryption
    # We will slide a window of up to 4 characters (q0, t0, b0, curr)
    p_q0 = -1 # Oldest for current quadgram (char at t-3)
    p_t0 = -1 # Oldest for current trigram (char at t-2), also 2nd for quadgram
    p_b0 = -1 # Oldest for current bigram (char at t-1), also 2nd for trigram, 3rd for quadgram
    p_curr = -1 # Current char

    # Process first character (index 0)
    p_b0 = key_map_list[seq_ints_list[0]] # This becomes the 'prev' char for the next bigram

    # Process second character (index 1) - forms first bigram
    if n >= 2:
        p_curr = key_map_list[seq_ints_list[1]]
        s2 += bigram_data_list[p_b0 * p26 + p_curr]
        c2 += 1
        
        # Shift window for next iteration
        p_t0 = p_b0 # Old p_b0 becomes oldest trigram char (at t-2 for next t)
        p_b0 = p_curr # Old p_curr becomes oldest bigram char (at t-1 for next t)

    # Process third character (index 2) - forms first trigram
    if n >= 3:
        p_curr = key_map_list[seq_ints_list[2]]
        s2 += bigram_data_list[p_b0 * p26 + p_curr] # Second bigram (char_idx 1, 2)
        c2 += 1
        s3 += trigram_data_list[p_t0 * p26_2 + p_b0 * p26 + p_curr] # First trigram (char_idx 0, 1, 2)
        c3 += 1
        
        # Shift window for next iteration
        p_q0 = p_t0 # Old p_t0 becomes oldest quadgram char (at t-3 for next t)
        p_t0 = p_b0 # Old p_b0 becomes oldest trigram char (at t-2 for next t)
        p_b0 = p_curr # Old p_curr becomes oldest bigram char (at t-1 for next t)

    # Process from fourth character (index 3) - forms first quadgram and subsequent n-grams
    for t_idx in range(3, n):
        p_curr = key_map_list[seq_ints_list[t_idx]]
        
        # Bigram (p_b0, p_curr)
        s2 += bigram_data_list[p_b0 * p26 + p_curr]
        c2 += 1
        
        # Trigram (p_t0, p_b0, p_curr)
        s3 += trigram_data_list[p_t0 * p26_2 + p_b0 * p26 + p_curr]
        c3 += 1
        
        # Quadgram (p_q0, p_t0, p_b0, p_curr)
        s4 += quadgram_data_list[p_q0 * p26_3 + p_t0 * p26_2 + p_b0 * p26 + p_curr]
        c4 += 1
        
        # Shift the window for the next iteration
        p_q0 = p_t0
        p_t0 = p_b0
        p_b0 = p_curr

    # Normalize scores
    if c2 > 0:
        s2 /= c2
    if c3 > 0:
        s3 /= c3
    if c4 > 0:
        s4 /= c4
    
    return w_bigram * s2 + w_trigram * s3 + w_quadgram * s4
# --------------------------------------------------------


class NGramModel:
    """
    N-gram scorer with normalized log-likelihood.
    Uses bigram+trigram+quadgram weighted combination.
    """
    def __init__(self, bigram_logs=None, trigram_logs=None, quadgram_logs=None, 
                 bigram_floor=-10.0, trigram_floor=-12.0, quadgram_floor=-15.0,
                 w_bigram=0.2, w_trigram=0.5, w_quadgram=0.3): 
        
        self.bigram_floor = float(bigram_floor)
        self.trigram_floor = float(trigram_floor)
        self.quadgram_floor = float(quadgram_floor)
        
        self.wb = float(w_bigram)
        self.wt = float(w_trigram)
        self.wq = float(w_quadgram)

        # Default compact models if none provided
        if bigram_logs is None:
            bigram_logs = {
                'th': -1.94, 'he': -2.06, 'in': -2.36, 'er': -2.48, 'an': -2.52,
                're': -2.56, 'on': -2.62, 'at': -2.77, 'en': -2.81, 'nd': -2.88,
                'ti': -2.89, 'es': -2.89, 'or': -2.95, 'te': -3.02, 'of': -3.05,
                'ed': -3.05, 'is': -3.09, 'it': -3.11, 'al': -3.14, 'ar': -3.17,
                'st': -3.19, 'to': -3.20, 'nt': -3.20, 'ng': -3.29, 've': -3.32,
                'se': -3.32, 'ha': -3.32, 'as': -3.39, 'ou': -3.39, 'io': -3.44,
                'le': -3.46, 'co': -3.52, 'me': -3.54, 'de': -3.56, 'hi': -3.58,
                'ri': -3.60, 'ro': -3.62, 'ic': -3.64, 'ne': -3.66, 'ea': -3.68,
                'ra': -3.70, 'ce': -3.72, 'li': -3.74, 'ch': -3.76, 'om': -3.78,
                'll': -3.80, 'ma': -3.82, 'el': -3.84, 'ur': -3.86, 'ns': -3.88,
                'be': -3.90, 'il': -3.92, 'di': -3.94, 'ho': -3.96, 'pe': -3.98,
                'ec': -4.00, 'pr': -4.02, 'no': -4.04, 'ct': -4.06, 'us': -4.08,
                'ac': -4.10, 'ow': -4.12, 'ly': -4.14, 'id': -4.16, 'ot': -4.18,
                'ca': -4.20, 'ts': -4.22, 'so': -4.24, 'wa': -4.26, 'si': -4.28
            }
        if trigram_logs is None:
            trigram_logs = {
                'the': -2.56, 'and': -3.27, 'ing': -3.54, 'ion': -3.63, 'tio': -3.65,
                'ent': -3.67, 'ati': -3.69, 'for': -3.72, 'her': -3.80, 'ter': -3.83,
                'hat': -3.86, 'tha': -3.86, 'ere': -3.92, 'ate': -3.98, 'his': -4.00,
                'con': -4.04, 'res': -4.06, 'ver': -4.08, 'all': -4.12, 'ons': -4.14,
                'nce': -4.16, 'men': -4.18, 'ith': -4.20, 'ted': -4.22, 'ers': -4.24,
                'pro': -4.26, 'thi': -4.28, 'wit': -4.30, 'are': -4.32, 'ess': -4.34,
                'not': -4.36, 'ive': -4.38, 'was': -4.40, 'ect': -4.42, 'rea': -4.44,
                'com': -4.46, 'eve': -4.48, 'per': -4.50, 'int': -4.52, 'est': -4.54,
                'sta': -4.56, 'cti': -4.58, 'ica': -4.60, 'ist': -4.62, 'ear': -4.64,
                'ain': -4.66, 'one': -4.68, 'our': -4.70, 'iti': -4.72, 'rat': -4.74,
                'der': -4.76, 'man': -4.78, 'tiv': -4.80, 'ort': -4.82, 'ble': -4.84,
                'ave': -4.86, 'cal': -4.88, 'tin': -4.90, 'but': -4.92, 'out': -4.94,
                'ine': -4.96, 'par': -4.98, 'own': -5.00, 'can': -5.02, 'ant': -5.04
            }
        if quadgram_logs is None:
            quadgram_logs = {
                'tion': -3.00, 'atio': -3.20, 'that': -3.40, 'ever': -3.50, 'from': -3.60,
                'with': -3.70, 'have': -3.80, 'ment': -3.90, 'this': -4.00, 'ther': -4.10,
                'here': -4.20, 'ould': -4.30, 'ough': -4.40, 'ight': -4.50, 'over': -4.60,
                'pres': -4.70, 'stan': -4.80, 'comp': -4.90, 'were': -5.00, 'said': -5.10,
                'also': -5.20, 'when': -5.30, 'then': -5.40, 'they': -5.50, 'some': -5.60,
                'into': -5.70, 'make': -5.80, 'made': -5.90, 'good': -6.00, 'want': -6.10,
                'test': -4.00, 'text': -4.10, 'word': -4.20, 'what': -4.30, 'will': -4.40,
                'your': -4.50, 'such': -4.60, 'much': -4.70, 'even': -4.80, 'more': -4.90,
                'only': -5.00, 'well': -5.10, 'like': -5.20, 'just': -5.30, 'time': -5.40,
                'year': -5.50, 'been': -5.60, 'cont': -5.70, 'comm': -5.80, 'syst': -5.90,
                'anal': -6.00, 'requ': -3.50, 'show': -4.00, 'case': -4.10, 'clai': -4.20
            }


        # Use Python lists for N-gram data (filled with floats)
        self.bigram = [self.bigram_floor] * (26 * 26)
        for k, v in bigram_logs.items():
            i, j = ord(k[0]) - 97, ord(k[1]) - 97
            if 0 <= i < 26 and 0 <= j < 26:
                self.bigram[i * 26 + j] = float(v)

        self.trigram = [self.trigram_floor] * (26 * 26 * 26)
        for k, v in trigram_logs.items():
            i, j, l = ord(k[0]) - 97, ord(k[1]) - 97, ord(k[2]) - 97
            if 0 <= i < 26 and 0 <= j < 26 and 0 <= l < 26:
                self.trigram[i * 26 * 26 + j * 26 + l] = float(v)
        
        self.quadgram = [self.quadgram_floor] * (26 * 26 * 26 * 26)
        for k, v in quadgram_logs.items():
            i, j, l, m = ord(k[0]) - 97, ord(k[1]) - 97, ord(k[2]) - 97, ord(k[3]) - 97
            if all(0 <= x < 26 for x in [i, j, l, m]):
                self.quadgram[i * (26**3) + j * (26**2) + l * 26 + m] = float(v)


    def score_sequence(self, seq_ints_list, key_map_list):
        """
        Calls the Pure Python scoring function with appropriate Python list inputs.
        """
        return _score_sequence_pure_python(
            seq_ints_list, 
            key_map_list, 
            self.bigram, 
            self.trigram, 
            self.quadgram,
            self.wb, 
            self.wt,
            self.wq
        )


class MonoalphabeticCracker:
    """
    Production-grade cracker:
    - Letter-only scoring pipeline
    - Frequency-based initialization
    - SA + HC with lateral moves
    - Multi-restart, optional word-list tie-break
    - Enhanced local refinement (post-SA/HC)
    """
    def __init__(self, scorer: NGramModel, seed=None):
        self.scorer = scorer
        if seed is not None:
            random.seed(seed)

        self.etaoin = list(ETAOIN)

    @staticmethod
    def preprocess_for_scoring(text):
        """
        Returns a Python list of integers (0-25) representing a-z lowercase characters.
        """
        seq = []
        for ch in text:
            o = ord(ch)
            if 65 <= o <= 90: # Uppercase A-Z
                o += 32
            if 97 <= o <= 122: # Lowercase a-z
                seq.append(o - 97)
        return seq # Return as a standard Python list


    @staticmethod
    def decrypt_string(ciphertext, key_map_list):
        """
        Decrypt only a–z and A-Z. All other chars (punctuation, digits) unchanged.
        key_map_list maps cipher letter index (0-25) to plaintext letter index.
        """
        lower_trans_table = str.maketrans(
            ''.join(chr(97 + i) for i in range(26)),
            ''.join(chr(97 + key_map_list[i]) for i in range(26))
        )
        upper_trans_table = str.maketrans(
            ''.join(chr(65 + i) for i in range(26)),
            ''.join(chr(65 + key_map_list[i]) for i in range(26))
        )
        
        decrypted_lower = ciphertext.translate(lower_trans_table)
        final_decrypted = decrypted_lower.translate(upper_trans_table)
        
        return final_decrypted


    def initial_key_by_frequency(self, seq_ints_list):
        """
        Map most frequent cipher letters to ETAOIN order. Returns a Python list.
        """
        # Calculate frequencies using Counter (standard library)
        counts = Counter(seq_ints_list)
        
        # Get all (char_index, count) pairs, including those with count 0
        all_char_counts = []
        for i in range(26):
            all_char_counts.append((i, counts.get(i, 0))) # (char_idx, count)

        # Sort by count descending, then by char_idx ascending for tie-breaking consistency
        all_char_counts.sort(key=lambda x: (-x[1], x[0])) 
        cipher_order_by_freq = [item[0] for item in all_char_counts] # List of cipher char indices, most freq first

        plain_etaoin_order = [ord(c) - 97 for c in self.etaoin] # List of plain char indices, ETAOIN order

        key = [-1] * 26 # key[cipher_char_idx] = plain_char_idx
        used_plain_letters = [False] * 26 

        etaoin_ptr = 0 # Pointer to the next ETAOIN letter to use

        # 1. Assign most frequent cipher letters to ETAOIN letters
        for ciph_idx in cipher_order_by_freq:
            if key[ciph_idx] != -1: # Already mapped, skip
                continue

            # Find the next available ETAOIN letter
            while etaoin_ptr < 26 and used_plain_letters[plain_etaoin_order[etaoin_ptr]]:
                etaoin_ptr += 1
            
            if etaoin_ptr < 26: # Found an available ETAOIN letter
                target_plain_idx = plain_etaoin_order[etaoin_ptr]
                key[ciph_idx] = target_plain_idx
                used_plain_letters[target_plain_idx] = True
                etaoin_ptr += 1
            else: # All ETAOIN letters used up, or something went wrong. Fallback to any unused.
                for p_idx in range(26):
                    if not used_plain_letters[p_idx]:
                        key[ciph_idx] = p_idx
                        used_plain_letters[p_idx] = True
                        break
        
        # 2. Assign any remaining unmapped cipher letters to any unused plain letters
        # (This handles cases where some less frequent cipher letters might not have been mapped yet)
        for ciph_idx in range(26):
            if key[ciph_idx] == -1:
                for p_idx in range(26):
                    if not used_plain_letters[p_idx]:
                        key[ciph_idx] = p_idx
                        used_plain_letters[p_idx] = True
                        break
        return key

    def random_perturb(self, key_map_list, swaps=8):
        """
        Applies random swaps to the key map. Operates on and returns Python list.
        """
        k = key_map_list[:] # Make a copy using slicing
        for _ in range(swaps):
            a, b = random.randrange(26), random.randrange(26)
            k[a], k[b] = k[b], k[a]
        return k

    def optimize(self, seq_ints_list, init_key_list, max_iter=25000, T0=2.0, alpha=0.9998, lateral=True, early_stall=8000):
        """
        Simulated Annealing + Hill Climb with lateral moves.
        Expects and returns Python lists for keys.
        """
        cur_key_list = self.random_perturb(init_key_list, swaps=15)
        cur_score = self.scorer.score_sequence(seq_ints_list, cur_key_list)
        best_key_list = cur_key_list[:] # Copy the list
        best_score = cur_score

        T = T0
        stall = 0
        
        rand = random.random
        exp = math.exp

        for it in range(max_iter):
            a = random.randrange(26)
            b = random.randrange(26)
            if a == b:
                continue
            
            cur_key_list[a], cur_key_list[b] = cur_key_list[b], cur_key_list[a]

            new_score = self.scorer.score_sequence(seq_ints_list, cur_key_list)
            delta = new_score - cur_score

            accept = False
            if delta > 0:
                accept = True
            elif lateral and abs(delta) < 1e-12:
                accept = True
            else:
                if T > 1e-12:
                    accept = (rand() < exp(delta / T))

            if accept:
                cur_score = new_score
                if new_score > best_score:
                    best_score = new_score
                    best_key_list = cur_key_list[:] # Copy the list
                    stall = 0
                else:
                    stall += 1
            else:
                cur_key_list[a], cur_key_list[b] = cur_key_list[b], cur_key_list[a]
                stall += 1

            T *= alpha

            if stall > early_stall:
                break

        return best_key_list, best_score

    def _refine_key_with_local_search(self, current_key_list, seq_ints_list):
        """
        Performs an exhaustive local search (all 2-letter swaps) around a given key
        to find tiny improvements.
        """
        best_local_key = current_key_list[:]
        best_local_score = self.scorer.score_sequence(seq_ints_list, current_key_list)
        
        improved = True
        while improved:
            improved = False
            for i in range(26):
                for j in range(i + 1, 26):
                    test_key = best_local_key[:]
                    test_key[i], test_key[j] = test_key[j], test_key[i]
                    
                    test_score = self.scorer.score_sequence(seq_ints_list, test_key)
                    
                    if test_score > best_local_score:
                        best_local_score = test_score
                        best_local_key = test_key[:]
                        improved = True
        return best_local_key, best_local_score


    @staticmethod
    def word_coverage_score(text, vocab=COMMON_WORDS):
        """
        Crude word-list coverage: fraction of tokens in vocab.
        Uses regex for more efficient tokenization.
        """
        words = re.findall(r'[a-zA-Z]+', text.lower())
        if not words:
            return 0.0
        hits = sum(1 for w in words if w in vocab)
        return hits / len(words)

    @staticmethod
    def format_key(key_map_list):
        pairs = []
        for c in range(26):
            pairs.append(f"{chr(97+c)}->{chr(97+key_map_list[c])}")
        return ", ".join(pairs)


# Worker function for multiprocessing
def _crack_single_restart_worker(
    ciphertext_raw, n_gram_params, cracker_seed, restart_idx,
    max_iter, T0, alpha, lateral, early_stall, use_word_tiebreak, perform_local_refinement
):
    if cracker_seed is not None:
        random.seed(cracker_seed + restart_idx)
    else:
        random.seed(os.urandom(8)) 

    scorer = NGramModel(
        bigram_floor=n_gram_params.get("bigram_floor", -10.0),
        trigram_floor=n_gram_params.get("trigram_floor", -12.0),
        quadgram_floor=n_gram_params.get("quadgram_floor", -15.0),
        w_bigram=n_gram_params.get("w_bigram", 0.2),
        w_trigram=n_gram_params.get("w_trigram", 0.5),
        w_quadgram=n_gram_params.get("w_quadgram", 0.3)
    )
    cracker = MonoalphabeticCracker(scorer, seed=None)

    seq_ints_list = cracker.preprocess_for_scoring(ciphertext_raw)
    if len(seq_ints_list) < 100:
        raise ValueError(f"Ciphertext quá ngắn cho n-gram scoring (worker {restart_idx}).")

    init_key_list = cracker.initial_key_by_frequency(seq_ints_list)
    key_list, score = cracker.optimize(
        seq_ints_list, init_key_list, max_iter=max_iter, T0=T0, alpha=alpha, lateral=lateral, early_stall=early_stall
    )

    if perform_local_refinement:
        key_list, score = cracker._refine_key_with_local_search(key_list, seq_ints_list)

    plaintext = cracker.decrypt_string(ciphertext_raw, key_list)
    wc = cracker.word_coverage_score(plaintext) if use_word_tiebreak else 0.0

    return key_list, score, plaintext, wc


def crack_cipher_parallel(ciphertext, restarts=10, max_iter=25000, use_word_tiebreak=True, seed=None, perform_local_refinement=True):
    if seed is not None:
        random.seed(seed)

    default_scorer = NGramModel() 
    n_gram_params = {
        "bigram_floor": default_scorer.bigram_floor, 
        "trigram_floor": default_scorer.trigram_floor,
        "quadgram_floor": default_scorer.quadgram_floor,
        "w_bigram": default_scorer.wb,
        "w_trigram": default_scorer.wt,
        "w_quadgram": default_scorer.wq,
    }

    all_results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for r_idx in range(restarts):
            worker_seed = seed if seed is None else seed + r_idx
            
            future = executor.submit(
                _crack_single_restart_worker,
                ciphertext,
                n_gram_params,
                worker_seed,
                r_idx,
                max_iter, 
                2.0,       # T0 (initial temperature)
                0.9998,    # alpha (cooling rate)
                True,      # lateral moves enabled
                8000,      # early_stall
                use_word_tiebreak,
                perform_local_refinement
            )
            futures.append(future)

        for r_idx, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                key_list, score, plaintext_worker, wc_worker = future.result()
                all_results.append((key_list, score, plaintext_worker, wc_worker))
                sys.stdout.write(f"Restart {r_idx+1:2d}/{restarts} | score={score:8.4f} | wordcov={wc_worker:5.3f}\n")
                sys.stdout.flush()
            except Exception as exc:
                sys.stderr.write(f'Restart {r_idx+1} generated an exception: {exc}\n')
                sys.stderr.flush()

    best_global_key_list = None
    best_score = -1e18
    best_plain = None
    best_wc = -1.0

    for key_list, score, plaintext_worker, wc_worker in all_results:
        improved = False
        if score > best_score + 1e-12:
            improved = True
        elif abs(score - best_score) <= 1e-12 and use_word_tiebreak and wc_worker > best_wc:
            improved = True

        if improved:
            best_score = score
            best_global_key_list = key_list[:]
            best_plain = plaintext_worker
            best_wc = wc_worker
    
    temp_cracker_for_format = MonoalphabeticCracker(NGramModel()) 

    return best_global_key_list, best_plain, best_score, temp_cracker_for_format.format_key(best_global_key_list)


def crack_from_file(input_file, output_file, restarts=10, max_iter=25000, seed=None, use_word_tiebreak=True, perform_local_refinement=True):
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Không tìm thấy file: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        ciphertext = f.read()

    print("=" * 64)
    print("CRACKING MONOALPHABETIC SUBSTITUTION (a–z, A-Z)")
    print("=" * 64)
    print(f"Text length (raw): {len(ciphertext)} characters\n")

    key_list, plaintext, score, formatted_key = crack_cipher_parallel(
        ciphertext,
        restarts=restarts,
        max_iter=max_iter,
        use_word_tiebreak=use_word_tiebreak,
        seed=seed,
        perform_local_refinement=perform_local_refinement
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"{score:.4f}\n")
        f.write(formatted_key + "\n")
        f.write(plaintext)

    print("\n" + "=" * 64)
    print(f"BEST SCORE: {score:.4f}")
    print(f"BEST KEY: {formatted_key}")
    print("=" * 64)
    print(f"✓ Đã lưu kết quả vào: {output_file}")

    return key_list, plaintext, score


def main():
    parser = argparse.ArgumentParser(description="Optimized Monoalphabetic Substitution Cipher Cracker (a–z, A-Z only).")
    parser.add_argument("-i", "--input", type=str, help="Đường dẫn file ciphertext", required="--input" in sys.argv)
    parser.add_argument("-o", "--output", type=str, help="Đường dẫn file output", required="--output" in sys.argv)
    parser.add_argument("--restarts", type=int, default=10, help="Số lần restart")
    parser.add_argument("--iter", type=int, default=25000, help="Số bước tối ưu mỗi restart")
    parser.add_argument("--seed", type=int, default=None, help="Seed cho PRNG (tùy chọn, để tái lập)")
    parser.add_argument("--no-word-tie", action="store_true", help="Tắt tie-break theo word-list")
    parser.add_argument("--no-refine", action="store_true", help="Tắt giai đoạn tinh chỉnh cục bộ cuối cùng")
    args = parser.parse_args()

    if args.input and not args.output:
        parser.error("--output là bắt buộc khi sử dụng --input")
    if args.output and not args.input:
        parser.error("--input là bắt buộc khi sử dụng --output")

    if args.input and args.output:
        crack_from_file(
            args.input,
            args.output,
            restarts=args.restarts,
            max_iter=args.iter,
            seed=args.seed,
            use_word_tiebreak=not args.no_word_tie,
            perform_local_refinement=not args.no_refine
        )
    else:
        sample = """Gsv hxrvmxv lu xibkgltizksb rh zmxrvmg, yfg rgh nlwvim
        zkkorxzgrlmh ziv dswvob fhvw rm wrtrgzo xllnfmrxzgrlmh. 
        This is an example text to show how the cracker works with both
        lowercase and Uppercase letters. Hopefully it will produce a good result."""
        
        print("\n" + "=" * 64)
        print("DEMO MODE (Using sample text)")
        print("=" * 64)
        print("Ciphertext:\n" + sample)

        key_list, plaintext, score, formatted_key = crack_cipher_parallel(
            sample, 
            restarts=10, 
            max_iter=30000, 
            seed=args.seed,
            perform_local_refinement=not args.no_refine
        )
        print("\n" + "=" * 64)
        print("RESULT")
        print("=" * 64)
        print(f"Score: {score:.4f}")
        print("Mapping:", formatted_key)
        print("\nPlaintext:\n" + plaintext)


if __name__ == "__main__":
    if sys.platform.startswith('win'):
        concurrent.futures.process.set_start_method('spawn', force=True)
    main()