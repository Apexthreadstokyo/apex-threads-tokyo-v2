#!/usr/bin/env python3
"""
Apex Threads Tokyo - Luxury EC Site
"""

import os
from flask import Flask, jsonify, request, send_from_directory
import stripe

app = Flask(__name__, static_folder="static")

# Stripe設定
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", ""
)

# 商品データ
PRODUCTS = [
    {
        "id": 1,
        "name": "SHADOW OVERSIZED TEE",
        "price": 8900,
        "original_price": 12000,
        "category": "tops",
        "badge": "BEST SELLER",
        "description": "プレミアムコットン100%のオーバーサイズTシャツ。ミニマルなデザインと上質な素材感。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Charcoal"],
        "rating": 4.8,
        "reviews": 124,
        "image_gradient": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)"
    },
    {
        "id": 2,
        "name": "NOIR CARGO PANTS",
        "price": 14800,
        "original_price": 19800,
        "category": "bottoms",
        "badge": "NEW",
        "description": "テーパードシルエットのカーゴパンツ。機能性とスタイルの融合。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Dark Olive"],
        "rating": 4.9,
        "reviews": 89,
        "image_gradient": "linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 50%, #2d2d2d 100%)"
    },
    {
        "id": 3,
        "name": "ECLIPSE HOODIE",
        "price": 12800,
        "original_price": None,
        "category": "tops",
        "badge": None,
        "description": "ヘビーウェイトフレンチテリーのプルオーバーフーディ。極上の着心地。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Graphite", "Midnight"],
        "rating": 4.7,
        "reviews": 203,
        "image_gradient": "linear-gradient(135deg, #141414 0%, #1f1f1f 50%, #333333 100%)"
    },
    {
        "id": 4,
        "name": "PHANTOM TRACK JACKET",
        "price": 16800,
        "original_price": 22000,
        "category": "outerwear",
        "badge": "LIMITED",
        "description": "テクニカルファブリックのトラックジャケット。都市生活のための機能美。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Onyx"],
        "rating": 4.9,
        "reviews": 56,
        "image_gradient": "linear-gradient(135deg, #0a0a0a 0%, #1c1c1c 50%, #2a2a2a 100%)"
    },
    {
        "id": 5,
        "name": "OBSIDIAN SHORTS",
        "price": 7900,
        "original_price": 10800,
        "category": "bottoms",
        "badge": "BEST SELLER",
        "description": "軽量ストレッチ素材のショーツ。洗練されたストリートスタイル。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Slate"],
        "rating": 4.6,
        "reviews": 167,
        "image_gradient": "linear-gradient(135deg, #121212 0%, #1e1e1e 50%, #2c2c2c 100%)"
    },
    {
        "id": 6,
        "name": "APEX ESSENTIAL TEE",
        "price": 5900,
        "original_price": None,
        "category": "tops",
        "badge": None,
        "description": "デイリーに着回せるエッセンシャルTシャツ。シルクのような肌触り。",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Black", "White", "Grey"],
        "rating": 4.8,
        "reviews": 312,
        "image_gradient": "linear-gradient(135deg, #181818 0%, #222222 50%, #303030 100%)"
    },
    {
        "id": 7,
        "name": "VORTEX BOMBER JACKET",
        "price": 24800,
        "original_price": 32000,
        "category": "outerwear",
        "badge": "LIMITED",
        "description": "MA-1インスパイアのボンバージャケット。プレミアムナイロン使用。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black"],
        "rating": 5.0,
        "reviews": 34,
        "image_gradient": "linear-gradient(135deg, #0d0d0d 0%, #191919 50%, #262626 100%)"
    },
    {
        "id": 8,
        "name": "STEALTH JOGGERS",
        "price": 11800,
        "original_price": 15800,
        "category": "bottoms",
        "badge": "NEW",
        "description": "テーパードジョガーパンツ。快適さとスタイルを両立。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Dark Grey"],
        "rating": 4.7,
        "reviews": 145,
        "image_gradient": "linear-gradient(135deg, #101010 0%, #1b1b1b 50%, #282828 100%)"
    }
]


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/products")
def get_products():
    category = request.args.get("category", "all")
    sort_by = request.args.get("sort", "default")

    filtered = PRODUCTS if category == "all" else [p for p in PRODUCTS if p["category"] == category]

    if sort_by == "price_low":
        filtered = sorted(filtered, key=lambda x: x["price"])
    elif sort_by == "price_high":
        filtered = sorted(filtered, key=lambda x: x["price"], reverse=True)
    elif sort_by == "rating":
        filtered = sorted(filtered, key=lambda x: x["rating"], reverse=True)

    return jsonify(filtered)


@app.route("/api/product/<int:product_id>")
def get_product(product_id):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404


@app.route("/api/checkout", methods=["POST"])
def create_checkout():
    """Stripe Checkout Sessionを作成してURLを返す"""
    data = request.get_json()
    items = data.get("items", [])

    if not items:
        return jsonify({"error": "カートが空です"}), 400

    # Stripe用のline_itemsを組み立て
    line_items = []
    for item in items:
        product = next((p for p in PRODUCTS if p["id"] == item["id"]), None)
        if not product:
            continue
        line_items.append({
            "price_data": {
                "currency": "jpy",
                "product_data": {
                    "name": product["name"],
                    "description": f"Size: {item.get('size', '-')} / Color: {item.get('color', '-')}",
                },
                "unit_amount": product["price"],  # JPYは小数点なし
            },
            "quantity": item.get("qty", 1),
        })

    if not line_items:
        return jsonify({"error": "有効な商品がありません"}), 400

    try:
        # リクエストのホストからベースURLを生成
        base_url = request.host_url.rstrip("/")
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=base_url + "/?status=success",
            cancel_url=base_url + "/?status=cancel",
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stripe-key")
def stripe_key():
    """公開可能キーをフロントに渡す"""
    pk = os.environ.get(
        "STRIPE_PUBLIC_KEY",
        ""
    )
    return jsonify({"publicKey": pk})


if __name__ == "__main__":
    print("\n  ⬛ APEX_THREADS_TOKYO")
    print("  http://localhost:5050\n")
    app.run(debug=True, port=5050)
