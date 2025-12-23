from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

<title>Secure Encryptor</title>

<style>
body {
    background: #1e1e1e;
    color: white;
    font-family: system-ui;
    padding: 20px;
}
textarea, input {
    width: 100%;
    background: #2b2b2b;
    color: white;
    border: none;
    padding: 10px;
    margin-top: 8px;
    border-radius: 6px;
}
button {
    margin-top: 10px;
    padding: 12px;
    width: 100%;
    background: #3a3a3a;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
}
.small {
    font-size: 14px;
    opacity: 0.8;
}
</style>
</head>

<body>
<h2>🔐 Secure Encryptor</h2>

<!-- NO FORM TAG = no save-password prompts -->

<label>Message / Encrypted Text</label>
<textarea id="text" rows="5" autocomplete="off" autocorrect="off" spellcheck="false"></textarea>

<label>Secret Key</label>
<input
    type="password"
    id="secret"
    autocomplete="new-password"
    autocorrect="off"
    autocapitalize="off"
    spellcheck="false"
/>

<button onclick="togglePassword()">👁 Show / Hide Key</button>

<button onclick="encrypt()">Encrypt</button>
<button onclick="decrypt()">Decrypt</button>

<h3>Result</h3>
<textarea id="result" rows="5" readonly></textarea>
<button onclick="copyResult()">📋 Copy to Clipboard</button>

<p class="small">Encryption runs locally. No data is sent or stored.</p>

<script>
// ---------- CRYPTO (CLIENT SIDE) ----------

async function deriveKey(password, salt) {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
        "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
    );
    return crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 100000,
            hash: "SHA-256"
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        false,
        ["encrypt", "decrypt"]
    );
}

async function encrypt() {
    const text = document.getElementById("text").value;
    const password = document.getElementById("secret").value;
    if (!text || !password) return alert("Missing text or key");

    const enc = new TextEncoder();
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const key = await deriveKey(password, salt);

    const encrypted = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        enc.encode(text)
    );

    const combined = new Uint8Array([
        ...salt, ...iv, ...new Uint8Array(encrypted)
    ]);

    document.getElementById("result").value =
        btoa(String.fromChar
