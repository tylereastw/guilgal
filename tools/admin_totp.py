#!/usr/bin/env python3
"""Create the authenticator secret for the Guilgal International admin panel.

    python3 tools/admin_totp.py

Prints a new secret and writes admin-totp-qr.svg to the current folder. Scan the
QR code with an authenticator app (Google Authenticator, Microsoft Authenticator,
1Password ...), then set ADMIN_TOTP_SECRET in Netlify to the printed secret.
Delete the SVG afterwards and never commit it.
"""
import base64, secrets, sys, urllib.parse
secret = base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")
uri = "otpauth://totp/" + urllib.parse.quote("Guilgal International:admin") + "?" + urllib.parse.urlencode(
    {"secret": secret, "issuer": "Guilgal International", "digits": 6, "period": 30})
print("ADMIN_TOTP_SECRET =", secret)
print("Authenticator URI:", uri)
try:
    import segno
    segno.make(uri, error="m").save("admin-totp-qr.svg", scale=8)
    print("QR code written to admin-totp-qr.svg (delete it after scanning)")
except ImportError:
    print("Install segno (pip install segno) for a QR code, or type the secret into the app.", file=sys.stderr)
