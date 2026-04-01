#!/usr/bin/env python3
"""
Apex Threads Tokyo - Luxury EC Site
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify, request, send_from_directory
import stripe

app = Flask(__name__, static_folder="static")

# Stripe設定
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# メール通知設定
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "kento.osaki@icloud.com")

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


def send_order_notification(session):
    """注文通知メールをオーナーに送信"""
    if not SMTP_USER or not SMTP_PASS:
        print("[WARNING] SMTP credentials not set, skipping email notification")
        return

    # 注文情報を取得
    customer_email = session.get("customer_details", {}).get("email", "不明")
    customer_name = session.get("customer_details", {}).get("name", "不明")
    shipping = session.get("shipping_details", {}) or {}
    address = shipping.get("address", {})
    amount_total = session.get("amount_total", 0)

    # 配送先を整形
    shipping_addr = ""
    if address:
        shipping_addr = (
            f"〒{address.get('postal_code', '')}\n"
            f"  {address.get('state', '')}{address.get('city', '')}\n"
            f"  {address.get('line1', '')} {address.get('line2', '') or ''}"
        )

    # line_itemsを取得
    line_items_data = stripe.checkout.Session.list_line_items(session["id"])
    items_text = ""
    for item in line_items_data.get("data", []):
        items_text += (
            f"  - {item['description']}\n"
            f"    数量: {item['quantity']}  "
            f"金額: ¥{item['amount_total']:,}\n"
        )

    body = f"""【新規注文通知】APEX THREADS TOKYO

注文日時: {session.get('created', '')}
決済ID: {session.get('payment_intent', '')}

━━━━━━━━━━━━━━━━━━━━
■ お客様情報
━━━━━━━━━━━━━━━━━━━━
氏名: {customer_name}
メール: {customer_email}

━━━━━━━━━━━━━━━━━━━━
■ 配送先
━━━━━━━━━━━━━━━━━━━━
{shipping_addr}

━━━━━━━━━━━━━━━━━━━━
■ 注文内容
━━━━━━━━━━━━━━━━━━━━
{items_text}
合計: ¥{amount_total:,}

━━━━━━━━━━━━━━━━━━━━
Stripeダッシュボードで詳細を確認:
https://dashboard.stripe.com/payments/{session.get('payment_intent', '')}
"""

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_EMAIL
    msg["Subject"] = f"【新規注文】¥{amount_total:,} - {customer_name}様"
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"[OK] Order notification sent to {NOTIFY_EMAIL}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")


@app.route("/api/webhook", methods=["POST"])
def stripe_webhook():
    """Stripe Webhookで注文完了を受け取る"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return jsonify({"error": "Invalid signature"}), 400
    else:
        event = stripe.Event.construct_from(
            request.get_json(), stripe.api_key
        )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"[ORDER] Payment received: {session.get('payment_intent')}")
        send_order_notification(session)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    print("\n  ⬛ APEX_THREADS_TOKYO")
    print("  http://localhost:5050\n")
    app.run(debug=True, port=5050)
