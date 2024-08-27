## Sqlite

The SQLite component in the Store module is used to store the text content of Document and build a corresponding inverted index based on Jieba's keyword extraction feature. During the retrieval phase, relevant documents are recalled through keywords, and the relevance between the query and the recalled texts is calculated using the BM25 algorithm, ultimately returning the most similar Top k documents.

### How to Configure the SQLite Component

You can use ChromaDB to store and query knowledge in the [Knowledge Components](2_2_4_Knowledge.md). You can create a storage component using SQLite with the following configuration:
```yaml
name: 'sqlite_store'
description: 'a store based on sqlite'
db_path: '../../DB/civil_law_sqlite.db'
k1: 1.5
b: 0.75
keyword_extractor: 'jieba_keyword_extractor'
similarity_top_k: 10
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.sqlite_store'
  class: 'SQLiteStore'
```
- db_path: The path to the SQLite database file, used for storing and managing text data.
- k1: The k1 parameter in the BM25 algorithm, which controls the influence of term frequency on the score.
- b: The b parameter in the BM25 algorithm, which controls the influence of document length on the score.
- keyword_extractor: The tool used for keyword extraction, specified here as jieba_keyword_extractor.
- similarity_top_k: Return top k similar documents based on bm25 score.

### Usage
[Knowledge_Define_And_Use](2_2_4_Knowledge_Define_And_Use.md)