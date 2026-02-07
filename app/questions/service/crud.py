from app.excuse.models import Input, Vector, Excuse


def get_data_by_identifier(identifier):
    excuse_queryset = Excuse.objects.filter(
        input__identifier=identifier
    ).select_related('vector')

    excuse_list = sorted(list(excuse_queryset), key=lambda excuse: excuse.created_at)
    vector_list = sorted([e.vector for e in excuse_list], key=lambda vector: vector.created_at)

    return excuse_list, vector_list

def get_context_by_identifier(identifier):
    context_queryset = Input.objects.filter(identifier=identifier).first()
    return context_queryset

def get_excuse_by_content(identifier, content):
    excuse_queryset = Excuse.objects.filter(input__identifier=identifier).filter(text=content)
    return excuse_queryset