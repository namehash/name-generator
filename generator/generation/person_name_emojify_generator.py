from typing import Optional
import json

from .person_name_generator import PersonNameGenerator


class PersonNameEmojifyGenerator(PersonNameGenerator):
    """
    Person name generator that uses emoji affixes.
    """

    def __init__(self, config):
        super().__init__(config)
        self.affixes = json.load(open(config.generation.person_name_emojify_affixes_path))
        self._prepare_affixes(self.affixes)

    def get_grouping_category(self, output_name: Optional[str] = None):
        return self._grouping_category