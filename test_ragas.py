def aggregate_ragas_results(results: list_c) -> dict:
    required_keys = {
        'faithfulness',
        'context_relevance',
        'answer_relevancy',
    }
    zero_result = dict.fromkeys(required_keys, 0.0)
    result_dict = zero_result.copy()
    if not results:
        return zero_result

    for d in results:
        if not required_keys.issubset(d):
            return zero_result
        result_dict["faithfulness"] += d['faithfulness']
        result_dict["context_relevance"] += d['context_relevance']
        result_dict["answer_relevancy"] += d['answer_relevancy']

    return {key: total / len(results) for key, total in result_dict.items()}


list_c = [{'faithfulness': 0.8,
         'context_relevance': 0.7,
         'answer_relevancy': 0.6}, {'faithfulness': 0.9,
                                    'context_relevance': 0.75,
                                    'answer_relevancy': 0.3}, {'faithfulness': 0.6,
                                                               'context_relevance': 0.1,
                                                               'answer_relevancy': 0.6, }]
print(aggregate_ragas_results(list_c))


def validate_ragas_dataset(samples: list) -> bool:
    required_keys = {
        'user_input',
        'response',
        'retrieved_contexts',
    }

    if not samples:
        return False
    for sample in samples:
        if not isinstance(sample, dict) or not required_keys.issubset(sample):
            return False
        if not isinstance(sample['user_input'], str) or sample['user_input'] == '':
            return False

        if not isinstance(sample['response'], str) or sample['response'] == '':
            return False

        if not isinstance(sample['retrieved_contexts'], list):
            return False

        for context in sample['retrieved_contexts']:
            if not isinstance(context, str):
                return False
    return True

dataset = [{'user_input': "Какой инструмент используется для миграций базы данных?",
            'response': "Для миграций базы данных используется Alembic.",
            'retrieved_contexts': ["Alembic используется для управления миграциями базы данных в SQLAlchemy."]
            },
           {'user_input': "Что такое FastAPI?",
            'response': "FastAPI — это современный Python-фреймворк для создания API.",
            'retrieved_contexts': ["FastAPI — это современный Python-фреймворк для создания API."]}
           ]

print(validate_ragas_dataset(dataset))