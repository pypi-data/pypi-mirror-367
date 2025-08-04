__author__ = "Chris Steel"
__copyright__ = "Copyright 2025, Syntheticore Corporation"
__credits__ = ["Chris Steel"]
__date__ = "10/22/2023"
__license__ = "Syntheticore Confidential"
__version__ = "1.0"
__email__ = "csteel@syntheticore.com"
__status__ = "Production"

import sys
import uuid
import platform
import json
import base64
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


def get_machine_id():
    return str(uuid.getnode()) + platform.node()


def sign_license(machine_id: str, expires: str, private_key_path: str, output_path: str):
    # Generate decryption key for .so files
    decryption_key = Fernet.generate_key()

    # Create license content
    content = {
        "machine_id": machine_id,
        "expiry": expires,
        "decryption_key": base64.b64encode(decryption_key).decode()
    }

    # Serialize content to JSON for signing
    content_str = json.dumps(content, sort_keys=True).encode()

    # Load private key
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    # Sign content with PSS padding
    signature = private_key.sign(
        content_str,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Create JSON license file
    license_data = {
        "content": content,
        "signature": base64.b64encode(signature).decode()
    }

    with open(output_path, "w") as f:
        json.dump(license_data, f, indent=4)

# ----------------------------------------------------------------------
# OPTIONAL helper – generate a new RSA key-pair
# ----------------------------------------------------------------------
def generate_keypair(private_path="private.pem", public_path="agentfoundry.pem", bits=2048):
    """
    Generate a fresh RSA private/public key pair.
    The private key stays with you; the public key is shipped inside AIgent.
    """
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
    )
    public_key = private_key.public_key()

    # write private.pem
    with open(private_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            )
        )
    # write agentfoundry.pem
    with open(public_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
    print(f"✅  Wrote private key → {private_path}")
    print(f"✅  Wrote public  key → {public_path}")
    return private_path, public_path

def validate_license(license_file: str = None, public_key_file: str = None):
    license_file = license_file or os.path.join(os.path.dirname(__file__), '..', 'agentfoundry.lic')
    public_key_file = public_key_file or os.path.join(os.path.dirname(__file__), '..', 'agentfoundry.pem')
    if not os.path.exists(license_file) or not os.path.exists(public_key_file):
        print(f"License or key file not found: {license_file}, {public_key_file}")
        sys.exit(1)
    with open(license_file, 'r') as f:
        lic = json.load(f)
    content = lic.get('content') or {}
    sig = lic.get('signature')
    if not content or not sig:
        print(f"Invalid license format in {license_file}")
        sys.exit(1)
    signature = base64.b64decode(sig)
    with open(public_key_file, 'rb') as f:
        pub = serialization.load_pem_public_key(f.read(), backend=default_backend())
    try:
        pub.verify(
            signature,
            json.dumps(content, sort_keys=True).encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
    except Exception as e:
        print(f"Invalid license signature: {e}")
        sys.exit(1)
    expiry = content.get('expiry')
    try:
        exp_date = datetime.strptime(expiry, '%Y-%m-%d').date()
    except Exception:
        print(f"Invalid expiry date in license: {expiry}")
        sys.exit(1)
    print(f"License expiration date: {expiry}")
    if datetime.today().date() > exp_date:
        print("License has expired.")
        sys.exit(1)
    print("License is valid.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate or validate a signed license file for AIgent.")
    parser.add_argument("--validate", action="store_true", help="Validate an existing license and print its expiration date")
    parser.add_argument("--license-file", default=None, help="Path to license file for validation (default: shipped agentfoundry.lic)")
    parser.add_argument("--public-key", default=None, help="Path to public key file for validation (default: shipped agentfoundry.pem)")
    parser.add_argument("--expires", help="Expiration date in YYYY-MM-DD format (default: 90 days from now)")
    parser.add_argument("--days", type=int, help="Number of days the license is valid (e.g. 30). Takes precedence over --expires.")
    parser.add_argument("--private-key", default="private.pem", help="Path to private RSA key for signing")
    parser.add_argument("--output", default="agentfoundry.lic", help="Path to output license file")
    parser.add_argument("--gen-keys", action="store_true", help="Generate a new RSA key-pair before signing")

    args = parser.parse_args()
    if args.validate:
        validate_license(args.license_file, args.public_key)
        sys.exit(0)

    # ------------------------------------------------------------------ #
    # Key-pair bootstrap (optional)
    # ------------------------------------------------------------------ #
    if args.gen_keys:
        generate_keypair(private_path=args.private_key, public_path="agentfoundry.pem")

    # ------------------------------------------------------------------ #
    # Resolve expiration date
    # ------------------------------------------------------------------ #
    if args.days is not None:
        if args.days <= 0:
            print("❌ --days must be a positive integer.")
            sys.exit(1)
        expiration = (datetime.today() + timedelta(days=args.days)).strftime("%Y-%m-%d")

    elif args.expires:
        try:
            expiration = datetime.strptime(args.expires, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print("❌ Invalid --expires format. Use YYYY-MM-DD.")
            sys.exit(1)

    else:
        expiration = (datetime.today() + timedelta(days=90)).strftime("%Y-%m-%d")

    machine_id = get_machine_id()
    sign_license(machine_id, expiration, args.private_key, args.output)
    print(f"✅ License generated for machine ID {machine_id}, expires {expiration}")
