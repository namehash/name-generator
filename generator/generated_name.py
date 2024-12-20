from typing import Tuple, List, Optional, Any


class GeneratedName:
    __slots__ = ['tokens', 'pipeline_name', 'status', 'applied_strategies', 'collection_members_count',
                 'collection_title', 'collection_id', 'related_collections', 'interpretation', 'grouping_category']

    def __init__(self,
                 tokens: Tuple[str, ...],
                 grouping_category: Optional[str] = None,
                 pipeline_name: Optional[str] = None,
                 category: Optional[str] = None,
                 applied_strategies: Optional[List[List[str]]] = None,
                 collection_id: Optional[str] = None,
                 collection_title: Optional[str] = None,
                 collection_members_count: Optional[int] = None,
                 related_collections: Optional[list[dict[str, Any]]] = None,) -> None:

        self.tokens = tokens

        self.grouping_category = grouping_category
        self.pipeline_name = pipeline_name
        self.status = category
        self.applied_strategies = []  # history of applied strategies

        if applied_strategies is not None:
            self.add_strategies(applied_strategies)
        else:
            self.applied_strategies.append([])

        self.collection_id = collection_id
        self.collection_title = collection_title
        self.collection_members_count = collection_members_count
        self.related_collections = related_collections
        self.interpretation = None

    def __str__(self):
        return ''.join(self.tokens)

    def __repr__(self):
        return str(self.tokens)

    def __json__(self):
        return ''.join(self.tokens)

    def add_strategies(self, strategies: List[List[str]]) -> None:
        self.applied_strategies.extend(strategies)

    def append_strategy_point(self, point: str) -> None:
        # we do not need any duplicates checking, as adding same value to unique values keeps them unique
        for strategy in self.applied_strategies:
            strategy.append(point)

    def dict(self):
        return {
            'tokens': self.tokens,
            'grouping_category': self.grouping_category,
            'pipeline_name': self.pipeline_name,
            'category': self.status,
            'applied_strategies': self.applied_strategies,
            'interpretation': self.interpretation,
        }
