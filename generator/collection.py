from __future__ import annotations

from typing import Any, Union, Iterable
import logging

import elastic_transport
import elasticsearch
from omegaconf import DictConfig

from generator.tokenization import WordNinjaTokenizer
from generator.utils.elastic import connect_to_elasticsearch, index_exists
from generator.utils import Singleton


logger = logging.getLogger('generator')


class Collection:
    def __init__(
            self,
            title: str,
            names: list[str],
            tokenized_names: list[tuple[str]],
            rank: float,
            score: float
            # TODO do we need those above? and do we need anything else?
    ):
        self.title = title
        self.names = names
        self.tokenized_names = tokenized_names
        self.rank = rank
        self.score = score

    @classmethod
    def from_elasticsearch_hit(cls, hit: dict[str, Any]) -> Collection:
        return cls(
            title=hit['_source']['data']['collection_name'],
            names=[x['normalized_name'] for x in hit['_source']['data']['names']],
            tokenized_names=[tuple(x['tokenized_name']) for x in hit['_source']['data']['names']],
            rank=hit['_source']['template']['collection_rank'],
            score=hit['_score']
        )


class CollectionMatcher(metaclass=Singleton):
    def __init__(self, config: DictConfig):
        self.config = config
        self.tokenizer = WordNinjaTokenizer(config)
        self.index_name = config.elasticsearch.index

        try:
            self.elastic = connect_to_elasticsearch(
                config.elasticsearch.host,
                config.elasticsearch.port,
                config.elasticsearch.username,
                config.elasticsearch.password
            )

            self.active = index_exists(self.elastic, self.index_name)
            if not self.active:  # TODO should we raise Exception instead?
                logger.warning(f'Elasticsearch index {self.index_name} does not exist')

        except elasticsearch.ConnectionError as ex:
            logger.warning('Elasticsearch service is unavailable: ' + str(ex))
            self.active = False
        except elasticsearch.exceptions.AuthenticationException as ex:
            logger.warning('Elasticsearch authentication failed: ' + str(ex))
            self.active = False
        except elastic_transport.ConnectionTimeout as ex:
            logger.warning('Elasticsearch connection timed out: ' + str(ex))
            self.active = False
        except Exception as ex:
            logger.warning('Elasticsearch connection failed: ' + str(ex))
            self.active = False

    def _search(self, query: str, limit: int) -> list[Collection]:
        response = self.elastic.search(
            index=self.index_name,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": [
                                        "data.collection_name^3",
                                        "data.collection_name.exact^3",
                                        "data.collection_description^2",
                                        "data.collection_keywords^2",
                                        "data.names.normalized_name",
                                        "data.names.tokenized_name",
                                    ],
                                    "type": "cross_fields",
                                }
                            }
                        ],
                        "should": [
                            {
                                "rank_feature": {
                                    "field": "template.collection_rank",
                                    "boost": 100,
                                    # "log": {
                                    #     "scaling_factor": 4
                                    # }
                                }
                            },
                            {
                                "rank_feature": {
                                    "field": "metadata.members_count",
                                }
                            }
                        ]
                    }

                },
                "size": limit,
            },
        )

        hits = response["hits"]["hits"]
        return [Collection.from_elasticsearch_hit(hit) for hit in hits]

    def search(self, query: Union[str, Iterable[str]], tokenized: bool = False, limit: int = 3) -> list[Collection]:
        if not self.active:
            return []

        if tokenized and not isinstance(query, str):
            query = ' '.join(query)

        query = query if tokenized else ' '.join(self.tokenizer.tokenize(query)[0])
        return self._search(query, limit)