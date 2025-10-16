from flask import Flask, request
import random, time

app = Flask(__name__)

@app.route("/healthz")
def health():
    return "ok", 200

@app.route("/work")
def work():
    latency = int(request.args.get("latencyMs", 100))
    fail_rate = int(request.args.get("failRatePct", 0))
    time.sleep(latency / 1000)
    if random.randint(0, 100) < fail_rate:
        return "error", 500
    return "success", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
