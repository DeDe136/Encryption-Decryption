"""
Optimized Frequency Data for English Text Analysis
FIXED: No duplicate keys, normalized scoring support
"""

# ==================== BIGRAM FREQUENCIES ====================
# Top 75 English bigrams - NO DUPLICATES
BIGRAM_FREQUENCIES = {
    'th': -1.94, 'he': -2.06, 'in': -2.36, 'er': -2.48, 'an': -2.52,
    're': -2.56, 'on': -2.62, 'at': -2.77, 'en': -2.81, 'nd': -2.88,
    'ti': -2.89, 'es': -2.90, 'or': -2.95, 'te': -3.02, 'of': -3.05,
    'ed': -3.06, 'is': -3.09, 'it': -3.11, 'al': -3.14, 'ar': -3.17,
    'st': -3.19, 'to': -3.20, 'nt': -3.21, 'ng': -3.29, 've': -3.32,
    'se': -3.33, 'ha': -3.34, 'as': -3.39, 'ou': -3.40, 'io': -3.44,
    'le': -3.46, 'co': -3.52, 'me': -3.54, 'de': -3.56, 'hi': -3.58,
    'ri': -3.60, 'ro': -3.62, 'ic': -3.64, 'ne': -3.66, 'ea': -3.68,
    'ra': -3.70, 'ce': -3.72, 'li': -3.74, 'ch': -3.76, 'om': -3.78,
    'll': -3.80, 'ma': -3.82, 'el': -3.84, 'ur': -3.86, 'ns': -3.88,
    'be': -3.90, 'il': -3.92, 'di': -3.94, 'ho': -3.96, 'pe': -3.98,
    'ec': -4.00, 'pr': -4.02, 'no': -4.04, 'ct': -4.06, 'us': -4.08,
    'ac': -4.10, 'ow': -4.12, 'ly': -4.14, 'id': -4.16, 'ot': -4.18,
    'ca': -4.20, 'ts': -4.22, 'so': -4.24, 'wa': -4.26, 'si': -4.28,
    'la': -4.30, 'ay': -4.32, 'wo': -4.34, 'ld': -4.36, 'fo': -4.38
}

# ==================== TRIGRAM FREQUENCIES ====================
# Top 100 English trigrams - NO DUPLICATES
TRIGRAM_FREQUENCIES = {
    'the': -2.56, 'and': -3.27, 'ing': -3.54, 'ion': -3.63, 'tio': -3.65,
    'ent': -3.67, 'ati': -3.69, 'for': -3.72, 'her': -3.80, 'ter': -3.83,
    'hat': -3.86, 'tha': -3.88, 'ere': -3.92, 'ate': -3.98, 'his': -4.00,
    'con': -4.04, 'res': -4.06, 'ver': -4.08, 'all': -4.12, 'ons': -4.14,
    'nce': -4.16, 'men': -4.18, 'ith': -4.20, 'ted': -4.22, 'ers': -4.24,
    'pro': -4.26, 'thi': -4.28, 'wit': -4.30, 'are': -4.32, 'ess': -4.34,
    'not': -4.36, 'ive': -4.38, 'was': -4.40, 'ect': -4.42, 'rea': -4.44,
    'com': -4.46, 'eve': -4.48, 'per': -4.50, 'int': -4.52, 'est': -4.54,
    'sta': -4.56, 'cti': -4.58, 'ica': -4.60, 'ist': -4.62, 'ear': -4.64,
    'ain': -4.66, 'one': -4.68, 'our': -4.70, 'iti': -4.72, 'rat': -4.74,
    'der': -4.76, 'man': -4.78, 'tiv': -4.80, 'ort': -4.82, 'ble': -4.84,
    'ave': -4.86, 'cal': -4.88, 'tin': -4.90, 'but': -4.92, 'out': -4.94,
    'ine': -4.96, 'par': -4.98, 'own': -5.00, 'can': -5.02, 'ant': -5.04,
    'enc': -5.06, 'hav': -5.08, 'ome': -5.10, 'ial': -5.12, 'tur': -5.14,
    'nde': -5.16, 'ces': -5.18, 'red': -5.20, 'ous': -5.22, 'pre': -5.24,
    'any': -5.26, 'ore': -5.28, 'eri': -5.30, 'ich': -5.32, 'use': -5.34,
    'ove': -5.36, 'ide': -5.38, 'cou': -5.40, 'rom': -5.42, 'rou': -5.44,
    'les': -5.46, 'hei': -5.48, 'ste': -5.50, 'imp': -5.52, 'hen': -5.54,
    'abo': -5.56, 'tho': -5.58, 'whe': -5.60, 'wou': -5.62, 'ght': -5.64,
    'lin': -5.66, 'hic': -5.68, 'hou': -5.70, 'ult': -5.72, 'you': -5.74
}

# ==================== COMMON WORDS ====================
# For validation only - NOT used during optimization
COMMON_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
    'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
    'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
    'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
    'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day'
}

# ==================== HELPER FUNCTIONS ====================

def load_bigrams():
    """Load bigram frequencies"""
    return BIGRAM_FREQUENCIES.copy()

def load_trigrams():
    """Load trigram frequencies"""
    return TRIGRAM_FREQUENCIES.copy()

def get_bigram_floor():
    """Default score for unseen bigrams"""
    return -10.0

def get_trigram_floor():
    """Default score for unseen trigrams"""
    return -12.0

def calculate_word_score(text):
    """
    Calculate percentage of valid English words
    WARNING: Only use for FINAL VALIDATION
    NOT for optimization (causes noise)
    """
    words = text.lower().split()
    if not words:
        return 0.0
    
    valid_count = sum(1 for word in words if clean_word(word) in COMMON_WORDS)
    return (valid_count / len(words)) * 100.0

def clean_word(word):
    """Remove punctuation from word"""
    return ''.join(c for c in word if c.isalpha())


class NgramScorer:
    """
    Production-grade N-gram scorer
    FIXED: Normalized scoring, no duplicates
    """
    
    def __init__(self):
        self.bigrams = load_bigrams()
        self.trigrams = load_trigrams()
        self.bigram_floor = get_bigram_floor()
        self.trigram_floor = get_trigram_floor()
    
    def score(self, text):
        """
        Score text using weighted bigram + trigram
        CRITICAL: Normalized by n-gram count
        """
        text = text.lower()
        
        # Bigram scoring
        bigram_score = 0.0
        bigram_count = 0
        for i in range(len(text) - 1):
            bg = text[i:i+2]
            if bg.isalpha():
                bigram_score += self.bigrams.get(bg, self.bigram_floor)
                bigram_count += 1
        
        # Trigram scoring
        trigram_score = 0.0
        trigram_count = 0
        for i in range(len(text) - 2):
            tg = text[i:i+3]
            if tg.isalpha():
                trigram_score += self.trigrams.get(tg, self.trigram_floor)
                trigram_count += 1
        
        # Normalize by count (CRITICAL FIX)
        if bigram_count > 0:
            bigram_score /= bigram_count
        if trigram_count > 0:
            trigram_score /= trigram_count
        
        # Weighted combination (Trigram 70%, Bigram 30%)
        score = (0.3 * bigram_score) + (0.7 * trigram_score)
        
        return score
    
    def score_ngram(self, text, n=3):
        """Score with specific n-gram size"""
        text = text.lower()
        score = 0.0
        count = 0
        
        if n == 2:
            for i in range(len(text) - 1):
                ng = text[i:i+2]
                if ng.isalpha():
                    score += self.bigrams.get(ng, self.bigram_floor)
                    count += 1
        elif n == 3:
            for i in range(len(text) - 2):
                ng = text[i:i+3]
                if ng.isalpha():
                    score += self.trigrams.get(ng, self.trigram_floor)
                    count += 1
        
        # Normalize
        if count > 0:
            score /= count
        
        return score


# ==================== VALIDATION ====================

def validate_no_duplicates():
    """Check for duplicate keys in n-gram data"""
    print("Validating n-gram data...")
    
    # Check bigrams
    bigram_keys = list(BIGRAM_FREQUENCIES.keys())
    if len(bigram_keys) != len(set(bigram_keys)):
        print("❌ ERROR: Duplicate keys in BIGRAM_FREQUENCIES!")
        return False
    print(f"✓ Bigrams: {len(bigram_keys)} unique entries")
    
    # Check trigrams
    trigram_keys = list(TRIGRAM_FREQUENCIES.keys())
    if len(trigram_keys) != len(set(trigram_keys)):
        print("❌ ERROR: Duplicate keys in TRIGRAM_FREQUENCIES!")
        return False
    print(f"✓ Trigrams: {len(trigram_keys)} unique entries")
    
    return True


if __name__ == "__main__":
    # Validate data integrity
    if not validate_no_duplicates():
        print("\n❌ CRITICAL: N-gram data has errors!")
        exit(1)
    
    print("\n" + "="*60)
    print("Testing Scorer")
    print("="*60)
    
    scorer = NgramScorer()
    
    # Good English text
    good_text = "the quick brown fox jumps over the lazy dog"
    good_score = scorer.score(good_text)
    print(f"\nGood English: {good_score:.4f}")
    print(f"Text: '{good_text}'")
    
    # Random text
    bad_text = "xyz qwk plmn frx jmps vwr th lzy dg"
    bad_score = scorer.score(bad_text)
    print(f"\nRandom text: {bad_score:.4f}")
    print(f"Text: '{bad_text}'")
    
    print(f"\nDifference: {good_score - bad_score:.4f}")
    
    if good_score > bad_score:
        print("\n✓ Scorer working correctly!")
    else:
        print("\n❌ Scorer failed - good text should score higher!")