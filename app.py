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
        "name": "ECLIPSE HOODIE",
        "price": 12800,
        "original_price": None,
        "category": "hoodies",
        "badge": "BEST SELLER",
        "description": "ヘビーウェイトフレンチテリーのプルオーバーフーディ。極上の着心地。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Graphite", "Midnight"],
        "rating": 4.8,
        "reviews": 203,
        "image_gradient": "linear-gradient(135deg, #08080e 0%, #12122a 50%, #1a1a38 100%)"
    },
    {
        "id": 2,
        "name": "PHANTOM HOODIE",
        "price": 14800,
        "original_price": 19800,
        "category": "hoodies",
        "badge": "NEW",
        "description": "オーバーサイズシルエットのジップアップフーディ。ダブルジップ仕様で都市生活に最適。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Onyx"],
        "rating": 4.9,
        "reviews": 89,
        "image_gradient": "linear-gradient(135deg, #0a0a12 0%, #1c1c2e 50%, #24243a 100%)"
    },
    {
        "id": 3,
        "name": "SHADOW PULLOVER",
        "price": 11800,
        "original_price": 15800,
        "category": "hoodies",
        "badge": None,
        "description": "プレミアムコットンブレンドのプルオーバーフーディ。ミニマルなデザインと上質な素材感。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Charcoal"],
        "rating": 4.7,
        "reviews": 156,
        "image_gradient": "linear-gradient(135deg, #0d0d14 0%, #18182a 50%, #222238 100%)"
    },
    {
        "id": 4,
        "name": "VORTEX ZIP HOODIE",
        "price": 16800,
        "original_price": 22000,
        "category": "hoodies",
        "badge": "LIMITED",
        "description": "テクニカルファブリックのフルジップフーディ。撥水加工と通気性を両立。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black"],
        "rating": 4.9,
        "reviews": 42,
        "image_gradient": "linear-gradient(135deg, #06060c 0%, #14142a 50%, #1e1e34 100%)"
    },
    {
        "id": 5,
        "name": "OBSIDIAN HEAVYWEIGHT",
        "price": 18800,
        "original_price": None,
        "category": "hoodies",
        "badge": None,
        "description": "500GSMヘビーウェイト生地のラグジュアリーフーディ。圧倒的な重厚感。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Slate"],
        "rating": 4.8,
        "reviews": 98,
        "image_gradient": "linear-gradient(135deg, #0c0c16 0%, #1a1a30 50%, #20203a 100%)"
    },
    {
        "id": 6,
        "name": "APEX ESSENTIAL HOODIE",
        "price": 9800,
        "original_price": None,
        "category": "hoodies",
        "badge": "BEST SELLER",
        "description": "デイリーに着回せるエッセンシャルフーディ。シルクのような肌触りと軽量設計。",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Black", "White", "Grey"],
        "rating": 4.7,
        "reviews": 312,
        "image_gradient": "linear-gradient(135deg, #0e0e18 0%, #16162a 50%, #1c1c32 100%)"
    },
    {
        "id": 7,
        "name": "NOIR CROPPED HOODIE",
        "price": 13800,
        "original_price": 17800,
        "category": "hoodies",
        "badge": "NEW",
        "description": "クロップド丈のモダンフーディ。ストリートとモードの融合。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Dark Grey"],
        "rating": 4.6,
        "reviews": 67,
        "image_gradient": "linear-gradient(135deg, #080810 0%, #101024 50%, #1a1a30 100%)"
    },
    {
        "id": 8,
        "name": "STEALTH TECH HOODIE",
        "price": 21800,
        "original_price": 28000,
        "category": "hoodies",
        "badge": "LIMITED",
        "description": "最先端素材を使用したテックフーディ。蓄熱保温と軽量性を実現。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Midnight"],
        "rating": 5.0,
        "reviews": 34,
        "image_gradient": "linear-gradient(135deg, #0a0a14 0%, #18182e 50%, #222240 100%)"
    },
    {
        "id": 9,
        "name": "APEX LOGO HOODIE",
        "price": 10800,
        "original_price": 14800,
        "category": "hoodies",
        "badge": "NEW",
        "description": "フロントにAPEXロゴを配したシグネチャーフーディ。裏起毛で暖かく、洗練されたストリートスタイル。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "White"],
        "rating": 4.8,
        "reviews": 45,
        "image_gradient": "linear-gradient(135deg, #0b0b18 0%, #151530 50%, #1e1e3c 100%)"
    }
]


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/tokushoho")
def tokushoho():
    return send_from_directory("static", "tokushoho.html")


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
        # 送料計算: 合計10,000円以上で送料無料、未満は800円
        subtotal = sum(
            item_data["price_data"]["unit_amount"] * item_data["quantity"]
            for item_data in line_items
        )
        shipping_options = []
        if subtotal >= 10000:
            shipping_options.append({
                "shipping_rate_data": {
                    "type": "fixed_amount",
                    "fixed_amount": {"amount": 0, "currency": "jpy"},
                    "display_name": "送料無料",
                    "delivery_estimate": {
                        "minimum": {"unit": "business_day", "value": 3},
                        "maximum": {"unit": "business_day", "value": 5},
                    },
                },
            })
        else:
            shipping_options.append({
                "shipping_rate_data": {
                    "type": "fixed_amount",
                    "fixed_amount": {"amount": 800, "currency": "jpy"},
                    "display_name": "全国一律送料",
                    "delivery_estimate": {
                        "minimum": {"unit": "business_day", "value": 3},
                        "maximum": {"unit": "business_day", "value": 5},
                    },
                },
            })

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            shipping_address_collection={
                "allowed_countries": ["JP"],
            },
            shipping_options=shipping_options,
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
