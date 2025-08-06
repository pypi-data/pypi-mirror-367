import json
import time
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import base64
from .errors import WebhookGuardError

def generate(request_body, private_key_pem):
    if not isinstance(request_body, str):
        raise WebhookGuardError('request_body must be a string.', 'TYPE_ERROR')

    timestamp = int(time.time())
    nonce = secrets.token_hex(16)
    signing_string = f"{timestamp}.{nonce}.{request_body}".encode('utf-8')

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
    )

    signature = private_key.sign(
        signing_string,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return {
        'x-webhookguard-timestamp': str(timestamp),
        'x-webhookguard-nonce': nonce,
        'x-webhookguard-signature': base64.b64encode(signature).decode('utf-8'),
    }

def verify(request, public_key_pem, options=None):
    options = options or {}
    tolerance = options.get('tolerance', 300)
    is_nonce_used = options.get('is_nonce_used', lambda nonce, timestamp: False)

    if not hasattr(request, 'headers') or not hasattr(request, 'body'):
        raise WebhookGuardError('Request object is missing headers or body.', 'INVALID_PAYLOAD')

    signature_b64 = request.headers.get('x-webhookguard-signature')
    timestamp_header = request.headers.get('x-webhookguard-timestamp')
    nonce = request.headers.get('x-webhookguard-nonce')

    if not signature_b64 or not timestamp_header or not nonce:
        raise WebhookGuardError('Missing one or more required headers.', 'INVALID_PAYLOAD')

    try:
        timestamp = int(timestamp_header)
    except (ValueError, TypeError):
        raise WebhookGuardError('Invalid timestamp format.', 'TIMESTAMP_EXPIRED')

    if abs(time.time() - timestamp) > tolerance:
        raise WebhookGuardError('Timestamp is outside the tolerance window.', 'TIMESTAMP_EXPIRED')

    if is_nonce_used(nonce, timestamp):
        raise WebhookGuardError('Nonce has already been processed.', 'NONCE_REPLAYED')

    signing_string = f"{timestamp}.{nonce}.{request.body}".encode('utf-8')
    
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8'),
    )

    try:
        public_key.verify(
            base64.b64decode(signature_b64),
            signing_string,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except Exception:
        raise WebhookGuardError('Signature does not match the expected value.', 'INVALID_SIGNATURE')

    return True
