from argparse import ArgumentParser
from itertools import islice

from pprint import pprint
from typing import Iterable

import jsonlines
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from tqdm import tqdm

INDEX_NAME = 'collections12all'


def connect_to_elasticsearch(
        host: str,
        port: int,
        username: str,
        password: str,
):
    return Elasticsearch(
        hosts=[{
            'scheme': 'http',
            'host': host,
            'port': port
        }],
        http_auth=(username, password),
        timeout=60
    )


def initialize_index(es: Elasticsearch):
    # TODO https://github.com/deepset-ai/haystack/blob/main/haystack/document_stores/elasticsearch.py
    # TODO what do all those properties mean? xd https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html
    # mapping = {
    #     'mappings': {
    #         'properties': {
    #             'category':                 {'type': 'text'},
    #             'collection_description':   {'type': 'text'},
    #             'collection_image':         {'type': 'text', 'index': False},
    #             'collection_keywords':      {'type': 'keywords'},
    #             'collection_members':       {'type': 'keywords'},
    #             'collection_name':          {'type': 'text'},
    #             'curated':                  {'type': 'boolean', 'index': False},
    #             'datetime':                 {'type': 'date', 'index': False},
    #             'metadata': {
    #                 'properties': {
    #                     'collection_articles':          {'type': 'keywords'},
    #                     'collection_rank':              {'type': 'rank_feature', 'positive_score_impact': False},
    #                     'collection_type_wikidata_id':  {'type': 'text'},
    #                     'collection_wikidata_id':       {'type': 'text'},
    #                     'collection_wikipedia_link':    {'type': 'text'},
    #                 }
    #             },
    #             'owner':    {'type': 'text', 'index': False},
    #             'public':   {'type': 'boolean'},
    #             'type':     {'type': 'keywords', 'index': False},
    #             'version':  {'type': 'version'}
    #         }
    #     }
    # }
    mapping = None
    mapping = {
        "settings": {
            "number_of_shards": 1,
        },
        "mappings": {
            "properties": {
                "data.collection_name": {"type": "text", "similarity": "BM25"},
                "data.names.normalized_name": {"type": "text", "similarity": "BM25"},
                "data.names.tokenized_name": {"type": "text", "similarity": "BM25"},
                "data.collection_description": {"type": "text", "similarity": "BM25"},
                "data.collection_keywords": {"type": "text", "similarity": "BM25"},
                "template.collection_articles": {"type": "text", "similarity": "BM25"},  # TODO remove?
                "template.collection_rank": {"type": "rank_feature"},
            }
        },
    }

    # TODO handle errors
    if not es.indices.exists(INDEX_NAME):
        es.indices.create(INDEX_NAME, body=mapping)
    else:
        print('Warning: index already exists, no changes applied')


def insert_collection(es: Elasticsearch, collection: dict):
    # TODO handle errors? something else? batching?
    es.index(INDEX_NAME, body=collection)


def insert_collections(es: Elasticsearch, collections: Iterable[dict]):
    number_of_docs = 500000
    progress = tqdm(unit="docs", total=number_of_docs)
    successes = 0

    # create the ES index
    for ok, action in streaming_bulk(client=es,
                                     index=INDEX_NAME,
                                     actions=collections,
                                     max_chunk_bytes=1000000,  # 1MB
                                     # chunk_size=10,
                                     max_retries=1):
        progress.update(1)
        successes += ok
    print("Indexed %d documents" % (successes,))


def gen(path, limit):
    with jsonlines.open(path, 'r') as reader:
        for doc in islice(reader.iter(skip_empty=True, skip_invalid=True), limit):
            # rank_feature must be positive
            doc['template']['collection_rank'] = max(1, doc['template']['collection_rank'])
            yield {
                "_index": INDEX_NAME,
                "_type": '_doc',
                "_source": doc
            }


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('input', help='input JSONL file with the collections to insert into ES')
    parser.add_argument('--host', default='localhost', help='elasticsearch hostname')
    parser.add_argument('--port', default=9200, type=int, help='elasticsearch port')
    parser.add_argument('--username', default='elastic', help='elasticsearch username')
    parser.add_argument('--password', default='password', help='elasticsearch password')
    parser.add_argument('--limit', default=None, type=int, help='limit the number of collections to insert')
    args = parser.parse_args()

    es = connect_to_elasticsearch(args.host, args.port, args.username, args.password)

    initialize_index(es)

    insert_collections(es, gen(args.input, args.limit))

    search = es.search(index=INDEX_NAME, body={'query': {'bool': {}}})
    print(f'Documents overall in {INDEX_NAME} - {len(search["hits"]["hits"])}')