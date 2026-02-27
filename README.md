# Ecommerce Search API

Django REST API for product creation, metadata update, and search with optional Meilisearch support (typo-tolerant search + intent-based sorting like `cheap`/`costly`).

## Requirements

- Python 3.11+
- pip
- Docker (only if using Meilisearch)

## Installation

```bash
cd /Users/infantricardo/Blowhorn/ecommerce-search
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## Run Project

```bash
cd /Users/infantricardo/Blowhorn/ecommerce-search
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

App URLs:
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/api/v1/...`

## API Endpoints

### 1) Create product (and optional metadata in same request)

`POST /api/v1/create/product`

Sample:

```json
{
  "title": "iPhone 15 (128GB, Blue)",
  "description": "Apple iPhone 15 with A16 Bionic chip",
  "price": 69999,
  "mrp": 79999,
  "stock": 25,
  "rating": 4.5,
  "total_reviews": 320,
  "units_sold": 1200,
  "return_rate": 1.8,
  "currency": "Rupee",
  "Metadata": {
    "ram": "8GB",
    "storage": "128GB",
    "screensize": "6.1 inch",
    "model": "iPhone 15",
    "brightness": "2000 nits",
    "color": "Blue",
    "category": "Smartphone"
  }
}
```

### 2) Update metadata

`PUT /api/v1/update/product`

Sample:

```json
{
  "productId": 1,
  "Metadata": {
    "color": "Black",
    "storage": "256GB"
  }
}
```

### 3) Search

`GET /api/v1/search/product?query=<text>`

Examples:
- `/api/v1/search/product?query=iphone`
- `/api/v1/search/product?query=ipone`
- `/api/v1/search/product?query=cheapest samsun phone`
- `/api/v1/search/product?query=costly iphone`

## Optional: Enable Meilisearch

Without Meilisearch, API uses DB fallback search. With Meilisearch enabled, you get typo tolerance and better relevance.

### Step 1: Start Meilisearch (Docker)

```bash
docker run --rm -it \
  -p 7700:7700 \
  -e MEILI_NO_ANALYTICS=true \
  getmeili/meilisearch:latest
```

### Step 2: Set environment variables

Run in the same terminal where Django is started:
2
```bash
export MEILI_ENABLED=true
export MEILI_HOST=http://127.0.0.1:7700
export MEILI_MASTER_KEY=
export MEILI_INDEX=products
```

Note: `MEILI_MASTER_KEY` can be empty in local development if Meilisearch is running without auth.

### Step 3: Reindex existing products

```bash
python manage.py reindex_products
```

### Step 4: Run Django

```bash
python manage.py runserver 0.0.0.0:8000
```

## Notes

- `cheap`, `cheapest`, `budget`, `sasta` sorts by lowest price.
- `costly`, `expensive`, `premium`, `costliest` sorts by highest price.
- Typos are handled better with Meilisearch, but very extreme misspellings may still fail.
