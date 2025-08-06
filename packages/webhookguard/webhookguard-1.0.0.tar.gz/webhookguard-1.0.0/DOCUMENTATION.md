# **WebhookGuard \- Full Technical Documentation**

This document provides a comprehensive guide to using the webhookguard library for Python, including detailed examples, API references, and security best practices.

## **Python Documentation**

### **Usage Examples**

#### **1\. Sender (Webhook Provider)**

On your server that sends webhooks, use the generate function to create the necessary security headers.
``` Python

# sender.py  
import json  
import requests  
from webhookguard import generate

# Load your private key securely (e.g., from a file or environment variable)  
with open('private\_key.pem', 'r') as f:  
    private_key = f.read()

# The raw body of your webhook request  
request_body = json.dumps({'event': 'payment.succeeded', 'data': {'amount': 1000}})

# Generate the security headers  
webhook_headers = generate(request_body, private_key)

print(f"Generated Headers: {webhook_headers}")

# Example: Send the request with these headers  
try:  
    response = requests.post(  
        'http://localhost:8000/webhook', # URL of the receiver's server  
        data=request_body.encode('utf-8'),  
        headers={**webhook_headers, 'Content-Type': 'application/json'}  
    )  
    response.raise_for_status()  
    print(f"Server Response: {response.text}")  
except requests.RequestException as e:  
    print(f"Request failed: {e}")
```

#### **2\. Receiver (Webhook Consumer)**

On your server that receives webhooks, use the verify function inside a try...except block.
``` Python

# receiver.py  
from http.server import BaseHTTPRequestHandler, HTTPServer  
from webhookguard import verify, WebhookGuardError

# Load the sender's public key  
with open('public\_key.pem', 'r') as f:  
    public_key = f.read()

# ⚠️ IMPORTANT: Implement a persistent nonce store for production\!  
nonce_store = set()  
def is_nonce_used(nonce, timestamp):  
    if nonce in nonce_store:  
        return True  # This nonce is a replay  
    # Add nonce to store and implement logic to evict old nonces  
    nonce_store.add(nonce)  
    return False

class WebhookHandler(BaseHTTPRequestHandler):  
    def do_POST(self):  
        if self.path == '/webhook':  
            try:  
                content_length = int(self.headers['Content-Length'])  
                body = self.rfile.read(content_length).decode('utf-8')  
                  
                # Create a request object with `headers` and `body` attributes  
                class Request:  
                    pass  
                request_obj = Request()  
                request_obj.headers = self.headers  
                request_obj.body = body

                # Verify the request  
                is_valid = verify(request_obj, public_key, options={'is\_nonce\_used': is_nonce_used})  
                  
                if is_valid:  
                    print("✅ Webhook verified successfully\!")  
                    self.send_response(200)  
                    self.end_headers()  
                    self.wfile.write(b'Webhook verified successfully\!')

            except WebhookGuardError as e:  
                # Handle specific verification errors  
                print(f"❌ Webhook verification failed: {e}")  
                self.send_response(400)  
                self.end_headers()  
                self.wfile.write(f'Webhook Error: {e}'.encode('utf-8'))  
            except Exception as e:  
                # Handle other unexpected errors  
                print(f"An internal server error occurred: {e}")  
                self.send_response(500)  
                self.end_headers()  
                self.wfile.write(b'Internal Server Error')  
        else:  
            self.send_response(404)  
            self.end_headers()

def run(server\_class=HTTPServer, handler\_class=WebhookHandler):  
    server_address = ('', 8000\)  
    httpd = server_class(server_address, handler_class)  
    print("Receiver server listening on http://localhost:8000")  
    httpd.serve_forever()

if __name__ == '__main__':  
    run()

```

### **API Reference (Python)**

#### **generate(request_body, private\_key\_pem)**

* request\_body (str): The raw request body. Can be an empty string.  
* private\_key\_pem (str): The RSA private key in PEM format.  
* **Returns** (dict): A dictionary containing the headers x-webhookguard-timestamp, x-webhookguard-nonce, and x-webhookguard-signature.

#### **verify(request, public\_key\_pem, options=None)**

* request (object): An object with headers (dict-like) and body (str) attributes.  
* public\_key\_pem (str): The RSA public key in PEM format.  
* options (dict, optional):  
  * tolerance (int): Allowed time difference in seconds. **Default:** 300\.  
  * is\_nonce\_used (Callable\[\[str, int\], bool\]): A function that checks if a nonce has been used. **Default:** A function that always returns False.  
* **Returns** (bool): True if the signature is valid.  
* **Raises** (WebhookGuardError): If verification fails for any reason.

## **Shared Security Considerations**

#### **Error Handling**

The verify function throws/raises a WebhookGuardError when verification fails. You can inspect the reason property/attribute to understand the cause.

| Reason | Description |
| :---- | :---- |
| INVALID\_PAYLOAD | A required x-webhookguard-\* header is missing or malformed. |
| TIMESTAMP\_EXPIRED | The webhook's timestamp is outside the allowed tolerance window. |
| NONCE\_REPLAYED | The nonce has already been processed (potential replay attack). |
| INVALID\_SIGNATURE | The signature does not match the expected value (message may be forged). |

#### **Nonce Store**

A nonce is a "number used once". To prevent replay attacks, you **must** store the nonces you've already processed. The examples use an in-memory Set/set, which is **not suitable for production**. In a real application, use a persistent, shared store like **Redis** or a database. You should also implement a cleanup mechanism to evict nonces that are older than your timestamp tolerance to prevent the store from growing indefinitely.

#### **Canonicalizing JSON in requestBody**

If the requestBody you are sending is itself a JSON object, you are responsible for ensuring it is stringified consistently before being passed to the generate function. An attacker could reorder keys in a JSON object, which would change the string representation and invalidate the signature.