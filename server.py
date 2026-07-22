import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from fyers_apiv3 import fyersModel

app = Flask(__name__)
CORS(app)  # Cross-Origin Requests allow karne ke liye

# Fyers API Credentials
# (Production mein inhe Environment Variables mein rakhna zyada secure hota hai)
CLIENT_ID = os.getenv("FYERS_CLIENT_ID", "YOUR_FYERS_APP_ID")
ACCESS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN", "YOUR_GENERATED_ACCESS_TOKEN")

# Fyers Model Initialize karein
fyers = fyersModel.FyersModel(
    client_id=CLIENT_ID, token=ACCESS_TOKEN, log_path=""
)


@app.route("/", methods=["GET"])
def home():
  return jsonify({
      "status": "Online",
      "message": "Market Watch Fyers Backend is running!",
  })


@app.route("/api/quotes", methods=["GET"])
def get_quotes():
  try:
    # Fyers ke standard format ke mutabiq symbols yahan define karein
    symbols = [
        "NSE:NIFTY50-INDEX",
        "NSE:NIFTYBANK-INDEX",
        "NSE:RELIANCE-EQ",
        "NSE:TCS-EQ",
    ]

    # Fyers API se quotes fetch karein
    response = fyers.quotes({"symbols": ",".join(symbols)})

    if response.get("s") == "ok":
      formatted_data = []
      for item in response.get("d", []):
        v = item.get("v", {})
        # Symbol name clean karna (jaise NSE:RELIANCE-EQ se sirf RELIANCE banana)
        raw_symbol = item.get("symbol", "")
        clean_symbol = (
            raw_symbol.split(":")[-1]
            .replace("-EQ", "")
            .replace("-INDEX", "")
        )

        formatted_data.append({
            "symbol": clean_symbol,
            "ltp": v.get("lp", 0.0),
            "open": v.get("open_price", 0.0),
            "high": v.get("high_price", 0.0),
            "low": v.get("low_price", 0.0),
            "prevClose": v.get("prev_close_price", 0.0),
            "volume": v.get("volume", 0),
            "bidPrice": v.get("bid", 0.0),
            "askPrice": v.get("ask", 0.0),
            "bidQty": v.get("bid_size", 0),
            "askQty": v.get("ask_size", 0),
            "oi": v.get("oi", 0),
        })

      return jsonify({"ok": True, "data": formatted_data})
    else:
      return jsonify({
          "ok": False,
          "error": response.get("message", "Fyers API error"),
      }), 400

  except Exception as e:
    return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
  # Local testing ke liye port 5000 par run hoga
  app.run(host="0.0.0.0", port=5000, debug=True)
