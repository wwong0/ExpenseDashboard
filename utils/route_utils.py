def pagination_to_response_data(pag, schema) -> dict:
    """Converts a Flask-SQLAlchemy Pagination object into a standardized dictionary format.

    Args:
        pag: The Pagination object returned by Flask-SQLAlchemy.
        schema: The Pydantic schema to use for serializing each item in the pagination.

    Returns:
        A dictionary containing the serialized items and pagination metadata.
    """
    item_data = [schema.model_validate(e).model_dump() for e in pag.items]

    response_data = {
        "items": item_data,
        "total": pag.total,
        "pages": pag.pages,
        "current_page": pag.page,
        "per_page": pag.per_page,
        "has_next": pag.has_next,
        "has_prev": pag.has_prev
    }

    return response_data