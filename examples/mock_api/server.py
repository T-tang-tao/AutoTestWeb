"""Self-contained Mock API for local AutoTestWeb demos."""

import os
import time

from flask import Flask, jsonify, request


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "autotestweb-mock-api"})

    @app.get("/api/products/<int:product_id>")
    def get_product(product_id: int):
        if product_id == 1:
            return jsonify({
                "code": "OK",
                "data": {
                    "id": 1,
                    "name": "Demo Product",
                    "price": 19.9,
                    "currency": "CNY",
                },
            })

        # Business-level errors intentionally use HTTP 200 so clients can
        # validate the application's error code independently of transport status.
        return jsonify({
            "code": "PRODUCT_NOT_FOUND",
            "message": f"商品 {product_id} 不存在",
            "data": None,
        })

    @app.post("/api/orders")
    def create_order():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}

        errors = {}
        product_id = payload.get("product_id")
        quantity = payload.get("quantity")

        if not isinstance(product_id, int) or isinstance(product_id, bool) or product_id <= 0:
            errors["product_id"] = "必须提供正整数 product_id"
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            errors["quantity"] = "必须提供正整数 quantity"

        if errors:
            return jsonify({
                "code": "VALIDATION_ERROR",
                "message": "请求参数校验失败",
                "errors": errors,
            }), 400

        return jsonify({
            "code": "ORDER_CREATED",
            "data": {
                "order_id": 10001,
                "product_id": product_id,
                "quantity": quantity,
            },
        }), 201

    @app.get("/api/delay")
    def delayed_response():
        try:
            delay_seconds = float(request.args.get("seconds", "0"))
        except (TypeError, ValueError):
            return jsonify({
                "code": "VALIDATION_ERROR",
                "message": "seconds 必须是 0 到 2 之间的数字",
            }), 400

        if not 0 <= delay_seconds <= 2:
            return jsonify({
                "code": "VALIDATION_ERROR",
                "message": "seconds 必须是 0 到 2 之间的数字",
            }), 400

        started_at = time.perf_counter()
        time.sleep(delay_seconds)
        actual_delay = time.perf_counter() - started_at
        return jsonify({
            "code": "OK",
            "requested_delay": delay_seconds,
            "actual_delay": round(actual_delay, 4),
        })

    return app


app = create_app()


if __name__ == "__main__":
    host = os.environ.get("MOCK_API_HOST", "127.0.0.1")
    port = int(os.environ.get("MOCK_API_PORT", "5010"))
    app.run(host=host, port=port)
