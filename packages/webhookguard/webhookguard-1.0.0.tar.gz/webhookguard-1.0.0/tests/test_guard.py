import unittest
import json
import time
from webhookguard import generate, verify, WebhookGuardError
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class MockRequest:
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body

class TestGuard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_key = private_key.public_key()
        cls.public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def test_generate_and_verify_success(self):
        request_body = '{"data": "test"}'
        headers = generate(request_body, self.private_key_pem)
        mock_request = MockRequest(headers=headers, body=request_body)
        self.assertTrue(verify(mock_request, self.public_key_pem))

    def test_verify_tampered_body(self):
        request_body = 'original_body'
        headers = generate(request_body, self.private_key_pem)
        mock_request = MockRequest(headers=headers, body='tampered_body')
        with self.assertRaises(WebhookGuardError) as cm:
            verify(mock_request, self.public_key_pem)
        self.assertEqual(cm.exception.reason, 'INVALID_SIGNATURE')

    def test_verify_invalid_signature(self):
        request_body = 'test'
        headers = generate(request_body, self.private_key_pem)
        headers['x-webhookguard-signature'] = 'invalidsignature'
        mock_request = MockRequest(headers=headers, body=request_body)
        with self.assertRaises(WebhookGuardError) as cm:
            verify(mock_request, self.public_key_pem)
        self.assertEqual(cm.exception.reason, 'INVALID_SIGNATURE')

    def test_verify_timestamp_expired(self):
        request_body = 'test'
        headers = generate(request_body, self.private_key_pem)
        headers['x-webhookguard-timestamp'] = str(int(time.time()) - 400)
        mock_request = MockRequest(headers=headers, body=request_body)
        with self.assertRaises(WebhookGuardError) as cm:
            verify(mock_request, self.public_key_pem, options={'tolerance': 300})
        self.assertEqual(cm.exception.reason, 'TIMESTAMP_EXPIRED')

    def test_verify_nonce_replayed(self):
        request_body = 'test'
        headers = generate(request_body, self.private_key_pem)
        mock_request = MockRequest(headers=headers, body=request_body)
        is_nonce_used = lambda nonce, timestamp: True
        with self.assertRaises(WebhookGuardError) as cm:
            verify(mock_request, self.public_key_pem, options={'is_nonce_used': is_nonce_used})
        self.assertEqual(cm.exception.reason, 'NONCE_REPLAYED')

if __name__ == '__main__':
    unittest.main()
