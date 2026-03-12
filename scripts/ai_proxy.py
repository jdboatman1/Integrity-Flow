#!/usr/bin/env python3
"""
Boatman AI™ Proxy — Integrity Flow Powered by Boatman Systems™
Handles:
  POST /api/ai/chat   → Ollama (native) on Linode A (port 11434)
  POST /api/lead      → ERPNext Lead creation (erp.aaairrigationservice.com)
Runs on Linode A at 0.0.0.0:11436. NPM proxies /api/ai/chat here.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

OLLAMA_URL  = "http://127.0.0.1:11434/api/chat"
MODEL       = "tinyllama:latest"
PORT        = 11436

ERP_URL     = "http://127.0.0.1:8080"
ERP_TOKEN   = "token e0ae503ee6740cb:1b32f975f1c58f1"
ERP_HOST    = "erp.aaairrigationservice.com"

SYSTEM_PROMPT = (
    "You are Boatman AI™, the expert virtual assistant for AAA Irrigation Service LLC "
    "in Plano, TX. Help customers with irrigation troubleshooting, scheduling, backflow "
    "compliance questions, and general service inquiries. Be concise and professional. "
    "If a customer wants to schedule a service or request an appointment, direct them to "
    "call 469-751-3567 or visit https://setup.aaairrigationservice.com/#contact to fill "
    "out the request form."
)


class ProxyHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._set_headers(200)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/ai/chat":
            self._handle_chat()
        elif self.path == "/api/lead":
            self._handle_lead()
        else:
            self._set_headers(404)
            self.end_headers()

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length)

    def _handle_chat(self):
        try:
            data = json.loads(self._read_body())
            message = data.get("message", "").strip()
        except (json.JSONDecodeError, AttributeError):
            self._set_headers(400)
            self.end_headers()
            self.wfile.write(b'{"error":"Invalid JSON"}')
            return

        if not message:
            self._set_headers(400)
            self.end_headers()
            self.wfile.write(b'{"error":"Empty message"}')
            return

        payload = json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": message},
            ],
            "stream": False,
        }).encode()

        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
            reply = result["message"]["content"]
        except urllib.error.URLError as e:
            self._set_headers(502)
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Ollama unreachable: {e.reason}"}).encode())
            return
        except Exception as e:
            self._set_headers(502)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        self._set_headers(200)
        self.end_headers()
        self.wfile.write(json.dumps({"response": reply}).encode())

    def _handle_lead(self):
        try:
            data = json.loads(self._read_body())
        except (json.JSONDecodeError, AttributeError):
            self._set_headers(400)
            self.end_headers()
            self.wfile.write(b'{"error":"Invalid JSON"}')
            return

        full_name    = data.get("full_name", "").strip()
        phone        = data.get("phone", "").strip()
        email        = data.get("email", "").strip()
        service_type = data.get("service_type", "")
        referral     = data.get("referral", "")
        message      = data.get("message", "")

        if not full_name or not phone:
            self._set_headers(400)
            self.end_headers()
            self.wfile.write(b'{"error":"full_name and phone are required"}')
            return

        lead_doc = {
            "doctype":                     "Lead",
            "lead_name":                   full_name,
            "mobile_no":                   phone,
            "email_id":                    email,
            "source":                      referral or "Website",
            "custom_service_description":  f"Service: {service_type}\n\n{message}",
            "status":                      "Lead",
        }

        payload = json.dumps(lead_doc).encode()
        try:
            req = urllib.request.Request(
                f"{ERP_URL}/api/resource/Lead",
                data=payload,
                headers={
                    "Content-Type":  "application/json",
                    "Authorization": ERP_TOKEN,
                    "Host":          ERP_HOST,
                },
                method="POST",
            )
            req.add_unredirected_header("Expect", "")
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
            lead_name = result.get("data", {}).get("name", "")
        except Exception as e:
            self._set_headers(502)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        self._set_headers(200)
        self.end_headers()
        self.wfile.write(json.dumps({"success": True, "lead": lead_name}).encode())

    def _set_headers(self, code):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, fmt, *args):
        pass  # logging handled by journald via systemd unit


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), ProxyHandler)
    print(f"Boatman AI™ proxy listening on port {PORT}")
    server.serve_forever()
