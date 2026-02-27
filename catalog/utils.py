import re

QUERY_NORMALIZATION = {
    "sastha": "cheap",
    "sasta": "cheap",
    "wala": "",
    "rupees": "",
    "rs": "",
    "under": "",
}

def normalize_query(query: str):
    query = query.lower().strip()

    words = query.split()
    normalized_words = []

    for word in words:
        word = QUERY_NORMALIZATION.get(word, word)
        if word:
            normalized_words.append(word)
    print(normalized_words)
    return " ".join(normalized_words)

import math

def rank_products(products, query):
    ranked = []

    for product in products:
        text_score = 1  # basic score (we’ll improve later)

        rating_score = product.rating / 5
        popularity_score = math.log(product.units_sold + 1)
        discount_score = (product.mrp - product.price) / product.mrp if product.mrp else 0
        stock_score = 1 if product.stock > 0 else 0

        price_score = 1 / product.price if product.price else 0

        final_score = (
            0.35 * text_score +
            0.20 * rating_score +
            0.15 * popularity_score +
            0.10 * discount_score +
            0.10 * price_score +
            0.10 * stock_score
        )

        ranked.append((final_score, product))

    ranked.sort(key=lambda x: x[0], reverse=True)

    return [item[1] for item in ranked]