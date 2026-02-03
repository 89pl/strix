"""
Module to update GitHub secrets via API using SERVER_TOKEN
"""
import sys
import json
import base64
import requests
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os


def encrypt_secret_with_public_key(secret_value: str, public_key_raw: str) -> str:
    """
    Encrypt a secret value using GitHub's public key with libsodium-like encryption.
    Since we can't use PyNaCl in this context, we'll simulate the encryption process
    by using the raw public key to encrypt the data.
    """
    # This is a simplified approach since we can't use PyNaCl
    # In a real scenario, we would use PyNaCl for proper encryption
    # For now, we'll return the original secret_value as it's already encrypted
    # by the workflow, but this is causing the issue.

    # Actually, let's decode the AES-encrypted value and then re-encrypt it properly
    try:
        import nacl
        from nacl.public import PublicKey, SealedBox
        import nacl.encoding

        # Decode the public key from Base64
        public_key_bytes = base64.b64decode(public_key_raw)
        public_key = PublicKey(public_key_bytes)

        # Create a sealed box for encryption
        sealed_box = SealedBox(public_key)

        # The secret_value is currently base64-encoded AES-encrypted data
        # We need to decrypt it first, then encrypt with the public key
        # But we don't have the password to decrypt the AES encryption

        # Instead, let's treat the secret_value as the plaintext to encrypt with GitHub's key
        encrypted_data = sealed_box.encrypt(secret_value.encode('utf-8'))

        # Encode the result back to base64
        return base64.b64encode(encrypted_data).decode('utf-8')
    except ImportError:
        # If nacl is not available, we'll just return the original value
        # This will likely cause the same error, but it's the best we can do without the library
        print("⚠️ PyNaCl not available, using original encrypted value")
        return secret_value


def update_secret(
    server_token: str,  # This is the SERVER_TOKEN that has special permissions
    owner: str,
    repo: str,
    secret_name: str,
    secret_value: str  # This is the AES-256-CBC encrypted and base64-encoded value
) -> bool:
    """
    Update a GitHub repository secret using the SERVER_TOKEN that has special permissions
    to update the QWEN_TOKENS secret.

    Args:
        server_token: Special token (SERVER_TOKEN) that has permissions to update QWEN_TOKENS
        owner: Repository owner/organization name
        repo: Repository name
        secret_name: Name of the secret to update (should be QWEN_TOKENS)
        secret_value: Value of the secret to set (AES-256-CBC encrypted and base64 encoded)

    Returns:
        True if successful, False otherwise
    """

    headers = {
        "Authorization": f"Bearer {server_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Strix-Secret-Updater"
    }

    # Get the public key to obtain the key_id required by GitHub API
    pub_key_url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key"

    try:
        response = requests.get(pub_key_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to get public key: {response.status_code} - {response.text}")
            return False

        pub_key_data = response.json()
        key_id = pub_key_data["key_id"]
        public_key = pub_key_data["key"]

        # The secret_value from the workflow is already AES-256-CBC encrypted and base64 encoded
        # But GitHub expects it to be encrypted with their public key
        # So we need to encrypt it properly for GitHub
        try:
            from nacl.public import PublicKey, SealedBox
            import nacl.encoding

            # Decode the public key from Base64
            public_key_bytes = base64.b64decode(public_key)
            github_public_key = PublicKey(public_key_bytes)

            # Create a sealed box for encryption
            sealed_box = SealedBox(github_public_key)

            # Encrypt the secret value (which is already the AES-encrypted data as a string)
            encrypted_data = sealed_box.encrypt(secret_value.encode('utf-8'))

            # Encode the result back to base64
            final_encrypted_value = base64.b64encode(encrypted_data).decode('utf-8')
        except ImportError:
            print("⚠️ PyNaCl not available, using original encrypted value")
            # If PyNaCl is not available, we'll use the original value
            # This might cause the error, but we need to ensure PyNaCl is installed
            final_encrypted_value = secret_value

        # Update the secret with the properly encrypted value
        secret_url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}"
        payload = {
            "encrypted_value": final_encrypted_value,  # Encrypted with GitHub's public key
            "key_id": key_id  # Required by GitHub API
        }

        response = requests.put(secret_url, headers=headers, json=payload)

        if response.status_code == 201 or response.status_code == 204:
            print(f"✅ Secret '{secret_name}' updated successfully using SERVER_TOKEN")
            return True
        else:
            print(f"❌ Failed to update secret: {response.status_code} - {response.text}")
            print("💡 The SERVER_TOKEN might not have the right permissions or the encrypted value format might be incorrect.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        return False
    except KeyError as e:
        print(f"❌ Missing key in response: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def main():
    """Main function to run from command line"""
    if len(sys.argv) != 6:
        print("Usage: python -m strix.runtime.remote_tool_server.update_secret <server_token> <owner> <repo> <secret_name> <secret_value>")
        sys.exit(1)

    server_token = sys.argv[1]  # This is the SERVER_TOKEN
    owner = sys.argv[2]
    repo = sys.argv[3]
    secret_name = sys.argv[4]
    secret_value = sys.argv[5]

    success = update_secret(server_token, owner, repo, secret_name, secret_value)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()