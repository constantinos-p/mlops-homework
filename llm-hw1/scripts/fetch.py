import requests
from elasticsearch import Elasticsearch, exceptions as es_exceptions
import tiktoken

docs_url = 'https://github.com/DataTalksClub/llm-zoomcamp/blob/main/01-intro/documents.json?raw=1'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()

documents = []

for course in documents_raw:
    course_name = course['course']

    for doc in course['documents']:
        doc['course'] = course_name
        documents.append(doc)

# print(documents[0])
es_client = Elasticsearch('http://elasticsearch:9200', timeout=120, max_retries=10, retry_on_timeout=True)

index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"} 
        }
    }
}

index_name = "course-questions-4"

def delete_index_if_exists(index_name):
    try:
        if es_client.indices.exists(index=index_name):
            es_client.indices.delete(index=index_name)
            print(f"Index '{index_name}' deleted successfully")
        else:
            print(f"Index '{index_name}' does not exist")
    except es_exceptions.ConnectionError as e:
        print(f"Failed to delete index: {e}")

index_name = "course-questions-4"
# delete_index_if_exists(index_name)

def create_index(index_name):
    try:
        if not es_client.indices.exists(index=index_name):
            es_client.indices.create(index=index_name, body=index_settings)
            print("Index created successfully")
            for doc in documents:
                print("indexing")
                es_client.index(index=index_name, document=doc)
        else:
            print("Index already exists")
    except es_exceptions.ConnectionError as e:
        print(f"Failed to create index: {e}")

create_index(index_name)

def searchQuery1(queryArg):
    return {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": queryArg,
                        "fields": ["question^4", "text"],
                        "type": "best_fields"
                    }
                }
            }
        }
    }

def searchQuery2(queryArg):
    return {
        "size": 3,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": queryArg,
                        "fields": ["question^4", "text"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "machine-learning-zoomcamp"
                    }
                }
            }
        }
    }


def elastic_search(search_query):

    response = es_client.search(index=index_name, body=search_query)
    print("response",response)
    
    result_docs = []    
    for hit in response['hits']['hits']:
        result_docs.append(hit['_source'])
    
    return result_docs
query = 'How do I execute a command in a running docker container?'
print("non filtered search",elastic_search(searchQuery1(queryArg=query)))
print("filtered search", elastic_search(searchQuery2(queryArg=query)))


context_template = """
Q: {question}
A: {text}
""".strip()

prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()


# Function to format the context using the template
def format_context(documents):
    context_template = """
Q: {question}
A: {text}
""".strip()
    context = "\n\n".join([context_template.format(question=doc['question'], text=doc['text']) for doc in documents])
    return context

def format_prompt(question,documents):
    context = format_context(documents)
    return prompt_template.format(question=question,context=context)

documents = elastic_search(searchQuery2(queryArg=query))
gptQuery = format_prompt(query,documents=documents)
print(len(gptQuery))
gpt4Encoder = tiktoken.encoding_for_model("gpt-4o")
print(len(gpt4Encoder.encode(gptQuery)))