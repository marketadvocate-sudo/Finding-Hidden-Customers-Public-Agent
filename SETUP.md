# Finding Hidden Customers Agent — Setup Guide

By Cannonball GTM. This agent identifies pain-based market segments from publicly available compliance data — the buyers your competitors can't see.

You'll run the agent on your own computer. It takes about ten minutes to set up the first time, then it's a single command to launch whenever you want it.

---

## What You Need

1. A computer (Mac or Windows)
2. An Anthropic API key (instructions below — about five minutes to get)
3. About $3 in API credits per brand analysis

---

## Step 1: Get Your Anthropic API Key

1. Go to https://console.anthropic.com
2. Sign up or log in
3. Click "Get API Keys" in the left menu
4. Click "Create Key"
5. Copy the key immediately — it starts with sk-ant- and you only see it once
6. Click "Billing" in the left menu and add credits (start with $20)

Keep that key somewhere safe. You'll paste it in a moment.

---

## Step 2: Install Python (if you don't have it)

**Mac:** Python is usually already installed. To check, open the Terminal app (press Cmd+Space, type "Terminal," hit Enter) and type:

```
python3 --version
```

If you see a version number (like Python 3.9 or higher), you're set. If not, download Python from https://www.python.org/downloads/ and install it.

**Windows:** Download Python from https://www.python.org/downloads/. During installation, CHECK THE BOX that says "Add Python to PATH." Then open Command Prompt (search "cmd" in the Start menu).

---

## Step 3: Install the Two Required Packages

In your Terminal (Mac) or Command Prompt (Windows), type:

```
pip3 install flask anthropic
```

Wait for it to finish. You'll see "Successfully installed" when it's done.

---

## Step 4: Set Your API Key

This tells the agent which Anthropic account to use.

**Mac** — in Terminal, type this (replace the placeholder with your actual key):

```
export ANTHROPIC_API_KEY=sk-ant-paste-your-key-here
```

**Windows** — in Command Prompt, type this (replace the placeholder with your actual key):

```
set ANTHROPIC_API_KEY=sk-ant-paste-your-key-here
```

Note: you'll need to do this each time you open a fresh Terminal window. (If you want it permanent, see the note at the bottom.)

---

## Step 5: Run the Agent

Navigate to the folder where cannonball.py lives. If you downloaded and unzipped the agent from GitHub, it's likely:

```
cd ~/Downloads/Finding-Hidden-Customers-Public-Agent-main
```

Then start the agent:

```
python3 cannonball.py
```

You'll see a banner that says CANNONBALL GTM. The agent is now running.

---

## Step 6: Open the Agent in Your Browser

Open your web browser and go to:

```
http://127.0.0.1:8000
```

You'll see the Finding Hidden Customers Agent. Enter the password (the default is cannonball2026 unless you change it), then start analyzing brands.

To stop the agent, go back to Terminal and press Ctrl+C.

---

## Using the Agent

1. Enter a brand name or URL
2. Confirm the brand profile and correct anything that's off
3. Provide context about the company
4. Walk through each stage — you can give feedback at every step
5. Generate a shareable report or a GTM engineer recipe

Each full analysis costs roughly $3 in API usage, billed to your Anthropic account.

---

## Optional: Make Your API Key Permanent (Mac)

So you don't have to set the key every time, run this once (replace with your real key):

```
echo 'export ANTHROPIC_API_KEY=sk-ant-paste-your-key-here' >> ~/.zshrc
```

Then close and reopen Terminal. The key will be set automatically from now on.

---

## Optional: Change the Password

The default password is cannonball2026. To set your own, before running the agent:

**Mac:**
```
export CANNONBALL_PASSWORD=your-password-here
```

**Windows:**
```
set CANNONBALL_PASSWORD=your-password-here
```

---

## Troubleshooting

**"command not found: python3"** — Install Python from python.org (Mac) or make sure you checked "Add Python to PATH" during install (Windows).

**"No module named flask"** — Run: pip3 install flask anthropic

**"Set your API key first"** — You need to run the export/set command from Step 4 in this Terminal window.

**Browser shows "can't connect"** — Make sure the agent is still running in Terminal (you should see the Cannonball banner). Use 127.0.0.1:8000, not localhost.

**An analysis fails partway** — Check that your Anthropic account has credits under Billing.

---

## Questions?

Reply to any Cannonball GTM newsletter or visit cannonballgtm.com.

This agent is in beta. Lab-tested across 70+ brands. Your feedback makes it better.
