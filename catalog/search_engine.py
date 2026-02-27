import re
from typing import Any

from django.conf import settings


INTENT_PRICE_ASC_KEYWORDS = {
    "cheap",
    "cheapest",
    "lowest",
    "affordable",
    "budget",
    "sasta",
    "sastha",
}

INTENT_PRICE_DESC_KEYWORDS = {
    "costly",
    "expensive",
    "premium",
    "highend",
    "high-end",
    "costliest",
}


def _search_enabled() -> bool:
    return bool(getattr(settings, "MEILI_ENABLED", False))


def _get_index():
    if not _search_enabled():
        return None

    try:
        import meilisearch
    except Exception:
        return None

    host = getattr(settings, "MEILI_HOST", "").strip()
    api_key = getattr(settings, "MEILI_MASTER_KEY", "").strip()
    index_uid = getattr(settings, "MEILI_INDEX", "products").strip()

    if not host:
        return None

    try:
        client = meilisearch.Client(host, api_key or None)
        index = client.index(index_uid)
        try:
            index.fetch_info()
        except Exception:
            try:
                client.create_index(index_uid, {"primaryKey": "id"})
            except TypeError:
                client.create_index(index_uid, primary_key="id")
            index = client.index(index_uid)

        index.update_settings(
            {
                "searchableAttributes": [
                    "title",
                    "description",
                    "category",
                    "model",
                    "color",
                    "ram",
                    "storage",
                    "screensize",
                ],
                "sortableAttributes": ["price", "mrp", "rating", "units_sold", "stock"],
                "filterableAttributes": ["category", "color", "currency"],
                "synonyms": {
                    "phone": ["mobile", "smartphone"],
                    "mobile": ["phone", "smartphone"],
                    "smartphone": ["phone", "mobile"],
                },
            }
        )
        return index
    except Exception:
        return None


def _parse_query_intent(query: str) -> dict[str, Any]:
    words = re.findall(r"\w+", query.lower())
    sort_price_asc = any(word in INTENT_PRICE_ASC_KEYWORDS for word in words)
    sort_price_desc = any(word in INTENT_PRICE_DESC_KEYWORDS for word in words)
    intent_words = INTENT_PRICE_ASC_KEYWORDS.union(INTENT_PRICE_DESC_KEYWORDS)
    cleaned_words = [word for word in words if word not in intent_words]
    cleaned_query = " ".join(cleaned_words).strip() or query
    return {
        "query": cleaned_query,
        "sort_price_asc": sort_price_asc,
        "sort_price_desc": sort_price_desc,
    }


def upsert_product_to_search(product) -> None:
    index = _get_index()
    if index is None:
        return

    metadata = getattr(product, "metadata", None)
    document = {
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "price": product.price,
        "mrp": product.mrp,
        "stock": product.stock,
        "rating": product.rating,
        "total_reviews": product.total_reviews,
        "units_sold": product.units_sold,
        "return_rate": product.return_rate,
        "currency": product.currency,
        "category": getattr(metadata, "category", None),
        "model": getattr(metadata, "model", None),
        "color": getattr(metadata, "color", None),
        "ram": getattr(metadata, "ram", None),
        "storage": getattr(metadata, "storage", None),
        "screensize": getattr(metadata, "screensize", None),
    }
    index.add_documents([document])


def search_product_ids(query: str, limit: int = 20) -> list[int]:
    index = _get_index()
    if index is None:
        return []

    intent = _parse_query_intent(query)
    search_query = intent["query"]
    params: dict[str, Any] = {"limit": limit}

    if intent["sort_price_asc"] and not intent["sort_price_desc"]:
        params["sort"] = ["price:asc"]
    elif intent["sort_price_desc"] and not intent["sort_price_asc"]:
        params["sort"] = ["price:desc"]

    try:
        result = index.search(search_query, params)
    except Exception:
        return []

    hits = result.get("hits", [])
    ids: list[int] = []
    for hit in hits:
        doc_id = hit.get("id")
        if isinstance(doc_id, int):
            ids.append(doc_id)
    return ids
