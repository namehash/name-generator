import itertools, collections
from typing import List, Dict, Tuple
from . import NameGenerator

class CategoriesGenerator(NameGenerator):
    """
    Replace tokens using categories.
    """

    def __init__(self, categories: Dict[str,List[str]]):
        super().__init__()
        self.categories = categories
        self.inverted_categories = collections.defaultdict(list)
        for category, tokens in categories.items():
            for token in tokens:
                self.inverted_categories[token].append(category)

    def generate(self, tokens: List[str]) -> List[Tuple[str]]:
        tokens_synsets = [self.get_similar(token) for token in tokens]

        names = []
        for asc in itertools.product(*[lemmas.items() for lemmas in tokens_synsets]):
            names.append((tuple([token[0] for token in asc]), sum([token[1] for token in asc])))

        return [x[0] for x in sorted(names, key=lambda x: x[1], reverse=True)]

    def get_similar(self, token: str) -> Dict[str, int]:
        stats = collections.defaultdict(int)
        stats[token] += 1
        for category in self.inverted_categories[token]:
            for token in self.categories[category]:
                stats[token]+=1
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
