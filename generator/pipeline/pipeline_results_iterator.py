from generator.generated_name import GeneratedName


class PipelineResultsIterator:
    def __init__(self, suggestions: list[GeneratedName]):
        self.index = 0
        self.suggestions = suggestions

    def __len__(self):
        return len(self.suggestions)

    def next_suggestion(self):
        suggestion = self.suggestions[self.index]
        self.index += 1
        return suggestion

    def __iter__(self):
        return self

    def __next__(self) -> GeneratedName:
        # print('ResultsIterator', self.index,len(self.suggestions))
        if self.index < len(self.suggestions):
            suggestion = self.suggestions[self.index]
            self.index += 1
            return suggestion
        raise StopIteration