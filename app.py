#!/usr/bin/env python3
"""
APX - Luxury EC Site
"""

import os
import json
import smtplib
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify, request, send_from_directory, Response
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
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "apexthreadstokyo@outlook.jp")

# 管理画面パスワード
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "apex2026")

# 出荷ステータス管理（インメモリ）: { payment_intent_id: True }
SHIPPED_ORDERS = {}

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
        "image_gradient": "linear-gradient(135deg, #08080e 0%, #12122a 50%, #1a1a38 100%)",
        "stock": 10
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
        "image_gradient": "linear-gradient(135deg, #0a0a12 0%, #1c1c2e 50%, #24243a 100%)",
        "stock": 10
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
        "image_gradient": "linear-gradient(135deg, #0d0d14 0%, #18182a 50%, #222238 100%)",
        "stock": 10
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
        "image_gradient": "linear-gradient(135deg, #06060c 0%, #14142a 50%, #1e1e34 100%)",
        "stock": 10
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
        "image_gradient": "linear-gradient(135deg, #0c0c16 0%, #1a1a30 50%, #20203a 100%)",
        "stock": 10
    },
    {
        "id": 6,
        "name": "APX ESSENTIAL HOODIE",
        "price": 9800,
        "original_price": None,
        "category": "hoodies",
        "badge": "BEST SELLER",
        "description": "デイリーに着回せるエッセンシャルフーディ。シルクのような肌触りと軽量設計。",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Black", "White", "Grey"],
        "rating": 4.7,
        "reviews": 312,
        "image_gradient": "linear-gradient(135deg, #0e0e18 0%, #16162a 50%, #1c1c32 100%)",
        "stock": 10
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
        "image_gradient": "linear-gradient(135deg, #080810 0%, #101024 50%, #1a1a30 100%)",
        "stock": 10
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
        "image_gradient": "linear-gradient(135deg, #0a0a14 0%, #18182e 50%, #222240 100%)",
        "stock": 10
    },
    {
        "id": 9,
        "name": "APX LOGO HOODIE",
        "price": 10800,
        "original_price": 14800,
        "category": "hoodies",
        "badge": "NEW",
        "description": "フロントにAPXロゴを配したシグネチャーフーディ。裏起毛で暖かく、洗練されたストリートスタイル。",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "White"],
        "rating": 4.8,
        "reviews": 45,
        "image_gradient": "linear-gradient(135deg, #0b0b18 0%, #151530 50%, #1e1e3c 100%)",
        "stock": 10
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

    body = f"""【新規注文通知】APX

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


def send_customer_confirmation(session):
    """注文確認メールをお客様に送信"""
    if not SMTP_USER or not SMTP_PASS:
        print("[WARNING] SMTP credentials not set, skipping customer email")
        return

    customer_email = session.get("customer_details", {}).get("email")
    if not customer_email:
        print("[WARNING] No customer email, skipping confirmation")
        return

    customer_name = session.get("customer_details", {}).get("name", "お客")
    shipping = session.get("shipping_details", {}) or {}
    address = shipping.get("address", {})
    amount_total = session.get("amount_total", 0)

    shipping_addr = ""
    if address:
        shipping_addr = (
            f"〒{address.get('postal_code', '')}\n"
            f"  {address.get('state', '')}{address.get('city', '')}\n"
            f"  {address.get('line1', '')} {address.get('line2', '') or ''}"
        )

    line_items_data = stripe.checkout.Session.list_line_items(session["id"])
    items_text = ""
    for item in line_items_data.get("data", []):
        items_text += (
            f"  {item['description']}\n"
            f"    数量: {item['quantity']}  "
            f"金額: ¥{item['amount_total']:,}\n"
        )

    body = f"""{customer_name} 様

この度はAPXをご利用いただき、
誠にありがとうございます。

ご注文を承りましたので、内容をお知らせいたします。

━━━━━━━━━━━━━━━━━━━━
■ ご注文内容
━━━━━━━━━━━━━━━━━━━━
{items_text}
合計金額: ¥{amount_total:,}（税込）

━━━━━━━━━━━━━━━━━━━━
■ 配送先
━━━━━━━━━━━━━━━━━━━━
{customer_name} 様
{shipping_addr}

━━━━━━━━━━━━━━━━━━━━
■ 配送について
━━━━━━━━━━━━━━━━━━━━
お届けまで3〜5営業日を予定しております。
発送完了時に改めてご連絡いたします。

━━━━━━━━━━━━━━━━━━━━
■ お問い合わせ
━━━━━━━━━━━━━━━━━━━━
ご不明な点がございましたら、
下記までお気軽にお問い合わせください。

メール: apexthreadstokyo@outlook.jp
電話: 070-8337-4625（平日10:00-18:00）

━━━━━━━━━━━━━━━━━━━━
APX
https://apex-threads-tokyo-v2.onrender.com
"""

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = customer_email
    msg["Subject"] = f"【APX】ご注文ありがとうございます（¥{amount_total:,}）"
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"[OK] Customer confirmation sent to {customer_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send customer email: {e}")


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
        # 在庫を減らす
        try:
            line_items_data = stripe.checkout.Session.list_line_items(session["id"])
            for item in line_items_data.get("data", []):
                item_name = item.get("description", "")
                qty = item.get("quantity", 1)
                # 商品名でマッチング（descriptionには "商品名" が入る）
                for product in PRODUCTS:
                    if product["name"] in item_name or item_name.startswith(product["name"]):
                        product["stock"] = max(0, product["stock"] - qty)
                        print(f"[STOCK] {product['name']}: stock decreased by {qty}, now {product['stock']}")
                        break
        except Exception as e:
            print(f"[ERROR] Failed to update stock: {e}")
        send_order_notification(session)
        send_customer_confirmation(session)

    return jsonify({"status": "ok"}), 200


# ===== 管理画面認証 =====
def check_admin_auth():
    """リクエストヘッダーからAdmin認証を確認"""
    auth_header = request.headers.get("X-Admin-Password", "")
    return auth_header == ADMIN_PASSWORD


def require_admin(f):
    """管理画面APIの認証デコレータ"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_admin_auth():
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/admin")
def admin_page():
    return send_from_directory("static", "admin.html")


@app.route("/api/admin/orders")
@require_admin
def admin_orders():
    """Stripeから最近の注文を取得"""
    try:
        sessions = stripe.checkout.Session.list(
            limit=30,
            expand=["data.line_items", "data.customer_details"],
        )
        orders = []
        for s in sessions.get("data", []):
            if s.get("payment_status") != "paid":
                continue
            pi = s.get("payment_intent", "")
            # line_itemsを取得
            try:
                line_items = stripe.checkout.Session.list_line_items(s["id"])
                items = [
                    {
                        "name": li.get("description", ""),
                        "quantity": li.get("quantity", 1),
                        "amount": li.get("amount_total", 0),
                    }
                    for li in line_items.get("data", [])
                ]
            except Exception:
                items = []

            shipping = s.get("shipping_details") or {}
            address = shipping.get("address") or {}
            shipping_addr = ""
            if address:
                shipping_addr = (
                    f"\u3012{address.get('postal_code', '')} "
                    f"{address.get('state', '')}{address.get('city', '')}"
                    f"{address.get('line1', '')} {address.get('line2', '') or ''}"
                )

            customer = s.get("customer_details") or {}
            orders.append({
                "payment_intent": pi,
                "created": s.get("created", 0),
                "customer_name": customer.get("name", ""),
                "customer_email": customer.get("email", ""),
                "items": items,
                "amount_total": s.get("amount_total", 0),
                "shipping_address": shipping_addr,
                "status": s.get("payment_status", ""),
                "shipped": SHIPPED_ORDERS.get(pi, False),
            })
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/inventory")
@require_admin
def admin_inventory():
    """全商品の在庫情報を返す"""
    inventory = [
        {"id": p["id"], "name": p["name"], "price": p["price"], "stock": p["stock"]}
        for p in PRODUCTS
    ]
    return jsonify(inventory)


@app.route("/api/admin/inventory/<int:product_id>", methods=["POST"])
@require_admin
def admin_update_inventory(product_id):
    """商品の在庫数を更新"""
    data = request.get_json()
    new_stock = data.get("stock")
    if new_stock is None:
        return jsonify({"error": "stock is required"}), 400
    try:
        new_stock = int(new_stock)
    except (ValueError, TypeError):
        return jsonify({"error": "stock must be an integer"}), 400
    if new_stock < 0:
        return jsonify({"error": "stock must be >= 0"}), 400

    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    product["stock"] = new_stock
    return jsonify({"id": product["id"], "name": product["name"], "stock": product["stock"]})


@app.route("/api/admin/orders/<payment_intent>/ship", methods=["POST"])
@require_admin
def admin_ship_order(payment_intent):
    """注文を出荷済みにする"""
    SHIPPED_ORDERS[payment_intent] = True

    # オプション: 出荷通知メールを送信
    if SMTP_USER and SMTP_PASS:
        try:
            # payment_intentからセッション情報を取得
            sessions = stripe.checkout.Session.list(
                payment_intent=payment_intent, limit=1
            )
            if sessions.get("data"):
                s = sessions["data"][0]
                customer = s.get("customer_details") or {}
                customer_email = customer.get("email")
                customer_name = customer.get("name", "")
                if customer_email:
                    send_shipping_notification(customer_email, customer_name)
        except Exception as e:
            print(f"[ERROR] Failed to send shipping notification: {e}")

    return jsonify({"payment_intent": payment_intent, "shipped": True})


def send_shipping_notification(email, name):
    """出荷通知メールをお客様に送信"""
    body = f"""{name} 様

いつもAPXをご利用いただきありがとうございます。

ご注文の商品を発送いたしました。
お届けまで1〜3日程度お待ちください。

ご不明な点がございましたら、お気軽にお問い合わせください。

メール: apexthreadstokyo@outlook.jp
電話: 070-8337-4625

APX
"""
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = email
    msg["Subject"] = f"【APX】商品を発送しました"
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"[OK] Shipping notification sent to {email}")
    except Exception as e:
        print(f"[ERROR] Failed to send shipping notification email: {e}")


if __name__ == "__main__":
    print("\n  ⬛ APX")
    print("  http://localhost:5050\n")
    app.run(debug=True, port=5050)
