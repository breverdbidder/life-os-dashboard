# Claude Code Setup Guide for Ariel Shapira
## BrevardBidderAI & Life OS Development

**Created:** December 2, 2025  
**Purpose:** Enable proper development workflow with persistent filesystem, real git, and autonomous sessions

---

## What You'll Get

| Current (Claude.ai) | After (Claude Code) |
|---------------------|---------------------|
| Temp container resets | Persistent filesystem |
| REST API workarounds | Real `git clone/push` |
| Can't test code | Run tests, builds |
| Session timeouts | 7-hour autonomous sessions |
| No Claude Trace | Full monitoring |
| Push and pray | Run → fix → run → commit |

---

## Step 1: Check Your System

### Windows
Open **PowerShell** (as Administrator) and run:
```powershell
# Check Node.js
node --version   # Need v18+ 

# If not installed or old, install via:
winget install OpenJS.NodeJS.LTS
```

### Mac
Open **Terminal** and run:
```bash
# Check Node.js
node --version   # Need v18+

# If not installed, use:
brew install node@20
```

---

## Step 2: Install Claude Code

### Option A: Native Installer (Recommended)

**Windows (PowerShell):**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**Mac/Linux:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### Option B: npm (Alternative)

```bash
# DO NOT use sudo!
npm install -g @anthropic-ai/claude-code
```

If you get permission errors:
```bash
# Fix npm permissions
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Then retry
npm install -g @anthropic-ai/claude-code
```

---

## Step 3: Verify Installation

```bash
claude --version
```

Should output something like: `Claude Code v1.x.x`

---

## Step 4: Authentication

You have **two options** based on your Anthropic account:

### Option A: Claude Max/Pro Subscription (Recommended)
If you have Claude Pro or Max subscription on claude.ai:

```bash
claude
# Select "Log in with Claude.ai account" when prompted
# Follow OAuth flow in browser
```

**Benefits:** 
- Fixed monthly cost
- Higher usage limits
- Unified with your Claude.ai subscription

### Option B: API Key (Pay-per-use)
If you want separate billing:

1. Go to: https://console.anthropic.com/settings/keys
2. Create new API key
3. Set environment variable:

**Windows (PowerShell):**
```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-xxx", "User")
```

**Mac/Linux:**
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-xxx"' >> ~/.zshrc
source ~/.zshrc
```

---

## Step 5: Clone Your Repos

```bash
# Create workspace
mkdir -p ~/code
cd ~/code

# Clone BrevardBidderAI
git clone https://github.com/breverdbidder/brevard-bidder-scraper.git
cd brevard-bidder-scraper

# Start Claude Code
claude
```

For Life OS Dashboard:
```bash
cd ~/code
git clone https://github.com/breverdbidder/life-os-dashboard.git
cd life-os-dashboard
claude
```

---

## Step 6: Configure Git (One-time)

```bash
git config --global user.name "Ariel Shapira"
git config --global user.email "ariel@everestcapitalusa.com"

# Store credentials so you don't re-enter every time
git config --global credential.helper store
```

---

## Step 7: Install Claude Trace (For Monitoring)

```bash
npm install -g @mariozechner/claude-trace
```

Now run Claude Code with tracing:
```bash
cd ~/code/brevard-bidder-scraper
claude-trace
```

Logs will be saved to `~/.claude-trace/` as HTML files you can review.

---

## Step 8: Install Happy (Mobile Access)

```bash
npm install -g happy-coder
```

Run with mobile access:
```bash
cd ~/code/brevard-bidder-scraper
happy
# Scan QR code with Happy app on your Android
```

**Android App:** https://play.google.com/store/apps/details?id=com.ex3ndr.happy

---

## Your New Workflow

### Daily Development (Claude Code)

```bash
# Morning: Start work on BrevardBidderAI
cd ~/code/brevard-bidder-scraper
claude-trace   # With monitoring

# Example commands to Claude:
> "Look at the BECA scraper and tell me what it does"
> "Run the test suite"
> "Fix the bug in bcpao_scraper.py"
> "Create a new feature branch for lien-discovery-v2"
> "Push the changes and create a PR"
```

### Quick Questions (Claude.ai)
Continue using Claude.ai (this web interface) for:
- Research and web searches
- Quick questions
- Planning discussions
- Document generation
- When on mobile without Happy

---

## Project-Specific Setup

### BrevardBidderAI

```bash
cd ~/code/brevard-bidder-scraper

# Install Python dependencies
pip install -r requirements.txt

# Start Claude Code
claude

# First command - let it understand the project:
> "Analyze this codebase and create a CLAUDE.md summary"
```

### Life OS Dashboard

```bash
cd ~/code/life-os-dashboard

# Install Node dependencies
npm install

# Start Claude Code  
claude

# Test the build:
> "Run npm run build and fix any errors"

# Deploy to Vercel:
> "Deploy this to Vercel"
```

---

## Recommended Model Settings

For serious development, use Claude Sonnet 4.5 or Opus:

```bash
# In your shell config (~/.bashrc or ~/.zshrc):
export ANTHROPIC_MODEL="claude-sonnet-4-5-20250929"

# Or for complex architecture work:
export ANTHROPIC_MODEL="claude-opus-4-20250514"
```

---

## Cost Comparison

| Usage | API Pay-per-use | Claude Max |
|-------|-----------------|------------|
| Light (1hr/day) | ~$30-50/mo | $100/mo (fixed) |
| Medium (3hr/day) | ~$100-200/mo | $100/mo (fixed) |
| Heavy (7hr sessions) | ~$300-500/mo | $100/mo (fixed) |

**Recommendation:** Start with Claude Max if you plan to use it heavily.

---

## Troubleshooting

### "command not found: claude"
```bash
# Check installation path
which claude

# Add to PATH if needed (Mac/Linux):
export PATH="$HOME/.npm-global/bin:$PATH"

# Windows: Restart terminal
```

### "Permission denied" on npm install
```bash
# Never use sudo! Fix permissions instead:
npm config set prefix '~/.npm-global'
```

### Git authentication issues
```bash
# Use HTTPS with token:
git remote set-url origin https://ghp_YOUR_TOKEN@github.com/breverdbidder/brevard-bidder-scraper.git
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Start Claude Code | `claude` |
| With trace logging | `claude-trace` |
| With mobile access | `happy` |
| Check version | `claude --version` |
| Report bug | `/bug` (inside Claude Code) |
| Exit | `Ctrl+C` or type `exit` |

---

## Links

- **Claude Code Docs:** https://docs.anthropic.com/en/docs/claude-code/overview
- **GitHub Repo:** https://github.com/anthropics/claude-code
- **npm Package:** https://www.npmjs.com/package/@anthropic-ai/claude-code
- **Happy (Mobile):** https://play.google.com/store/apps/details?id=com.ex3ndr.happy
- **Anthropic Console:** https://console.anthropic.com

---

## After Setup: Tell Me "Claude Code ready"

Once you have Claude Code running on your machine, start a session in your repo and say:

```
"Claude Code ready - connected to brevard-bidder-scraper"
```

Then I (as Claude Code) will have:
- Full filesystem access
- Real git operations  
- Test execution
- Persistent context
- Autonomous capability

That's when the real development power unlocks.
