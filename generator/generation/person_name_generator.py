from typing import List, Tuple, Any

from .name_generator import NameGenerator
from ..input_name import InputName, Interpretation


class PersonNameGenerator(NameGenerator):
    """

    """

    def __init__(self, config):
        super().__init__(config)

    def generate(self, tokens: Tuple[str, ...]) -> List[Tuple[str, ...]]:
        return (
            tokens + ('👑',),  # crown
            tokens + ('💎',),  # gem stone
        )

    def generate2(self, name: InputName, interpretation: Interpretation) -> List[Tuple[str, ...]]:
        return self.generate(**self.prepare_arguments(name, interpretation))

    def prepare_arguments(self, name: InputName, interpretation: Interpretation):
        return {'tokens': (name.strip_eth_namehash_unicode_replace_invalid,)}