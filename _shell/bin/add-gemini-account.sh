#!/bin/bash
# add-gemini-account.sh — drive ONE gemini auth login + save creds to pool.
# Per memory: user only clicks the browser; Claude does all CLI work.
set -e

ACCOUNTS_DIR="$HOME/.gemini/accounts"
mkdir -p "$ACCOUNTS_DIR"

echo "=== logging out current gemini session ==="
gemini auth logout 2>/dev/null || true

echo
echo "=== gemini auth login — browser will open. Click through Google login. ==="
echo
gemini auth login

if [ ! -f "$HOME/.gemini/oauth_creds.json" ]; then
    echo "ERROR: oauth_creds.json not written; auth must have failed"
    exit 1
fi

EMAIL=$(python3 -c "
import json, base64
d = json.load(open('$HOME/.gemini/oauth_creds.json'))
parts = d['id_token'].split('.')
pad = '=' * (4 - len(parts[1]) % 4)
print(json.loads(base64.urlsafe_b64decode(parts[1] + pad).decode())['email'])
")

DEST="$ACCOUNTS_DIR/${EMAIL}.json"
cp "$HOME/.gemini/oauth_creds.json" "$DEST"
echo
echo "=== saved: $EMAIL ==="
echo "    $DEST"
echo
echo "current accounts in pool:"
ls "$ACCOUNTS_DIR" | sed 's/^/  /'
echo
echo "total: $(ls $ACCOUNTS_DIR | wc -l | tr -d ' ')"
