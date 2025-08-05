import random

class PassGent():
    def __init__(self, keyword=None, year=None, symbol=None, suffix=None):
        self.wordlist = set()
        self.keywords = keyword or ["admin", "dashboard", "login", "administrator", "manager"]
        self.years = year or ["2021", "2022", "2023", "2024", "2025"]
        self.symbols = symbol or ["#", "@", "_", "-", "+", "*", "%"]
        self.suffixes = suffix or ["pass", "123", "admin", "dashboard", "login", "web", "apps"]

    def generate_suffix(self):
        base_words = set()
        for word in self.keywords:
            base_words.add(word)
            base_words.add(word.capitalize())
            base_words.add(word.upper())

        for word1 in base_words:
            for word2 in base_words:
                if word1 != word2:
                    for year in self.years:
                        for sym in self.symbols:
                            for suffix in self.suffixes:
                                self.wordlist.add(f"{word1}{word2}{sym}{year}")
                                self.wordlist.add(f"{word1}{sym}{word2}{suffix}")
                                self.wordlist.add(f"{word1}{suffix}{sym}{year}")
                                self.wordlist.add(f"{word1}{word2}{suffix}")
                                self.wordlist.add(f"{word1}{sym}{suffix}")
                                self.wordlist.add(f"{word1}{year}")
                                self.wordlist.add(f"{word1}{suffix}")
        return self.wordlist

    def filtering(self, wordlist):
        leet = lambda w: w.replace("o", "0").replace("i", "1").replace("e", "3").replace("a", "4").replace("s", "5")
        leet_words = set()
        for w in list(wordlist):
            leet_words.add(leet(w))
        self.wordlist.update(leet_words)
        return self.wordlist

    def generate(self, num: int):
        suffixies = self.generate_suffix()
        wordlist = self.filtering(suffixies)
        final_list = list(wordlist)
        random.shuffle(final_list)
        sampled_wordlist = final_list[:num]
        return sampled_wordlist
