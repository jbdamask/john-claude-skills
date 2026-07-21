# Security Red Flags Reference

Comprehensive list of suspicious patterns to look for during repository security audits.

## Table of Contents
- [Install Script Red Flags](#install-script-red-flags)
- [Source Code Red Flags](#source-code-red-flags)
- [Dependency Red Flags](#dependency-red-flags)
- [Network Red Flags](#network-red-flags)
- [File System Red Flags](#file-system-red-flags)

## Install Script Red Flags

### Critical (Immediate concern)
- `curl URL | bash` or `wget URL | sh` from non-official sources
- `eval $(curl ...)` - executing remote code
- Download + chmod +x + execute pattern from unknown hosts
- Modifying `/etc/` system files
- Adding entries to crontab
- Modifying shell profiles (.bashrc, .zshrc, .profile) to inject persistent code
- Creating systemd services or launchd agents
- Disabling security features (SELinux, firewall rules)

### Suspicious (Investigate further)
- Environment variable harvesting (`$AWS_SECRET`, `$GITHUB_TOKEN`, etc.)
- Reading files outside installation scope
- Hidden file creation in unexpected locations
- Network requests during install (beyond downloading the binary)
- Compilation from source without showing the code
- Requesting sudo/root when not obviously needed

### Legitimate but verify
- Adding to PATH (common, but verify what's being added)
- Creating config directories in ~/.config or ~/.<appname>
- Installing dependencies via package managers

## Source Code Red Flags

### Critical
- Base64 encoded payloads that get decoded and executed
- `eval()`, `exec()`, `Function()` with dynamic strings
- Obfuscated code (meaningless variable names, packed JavaScript)
- Reading SSH keys (`~/.ssh/id_rsa`, `~/.ssh/known_hosts`)
- Reading credential files (`~/.aws/credentials`, `~/.netrc`, `~/.npmrc`)
- Reading browser data (cookies, history, saved passwords)
- Keylogger patterns (keyboard event listeners storing input)
- Screenshot or screen recording capabilities without clear purpose
- Clipboard monitoring

### Suspicious
- Hardcoded IP addresses (instead of domain names)
- Non-HTTPS URLs for data transmission
- Domains that aren't the official project domain
- Data serialization before network transmission
- Regular phone-home intervals (setInterval with HTTP calls)
- Machine fingerprinting (collecting OS, hardware, network info)
- Reading environment variables in bulk
- File system enumeration (walking directories to list files)

### Check for data exfiltration patterns
```
# Look for these patterns in code:
- HTTP POST/PUT to external URLs
- WebSocket connections
- DNS queries with encoded data (DNS tunneling)
- Writing to shared/cloud storage APIs
- Email sending capabilities
```

## Dependency Red Flags

### Package.json / npm
- `analytics`, `tracking`, `telemetry`, `metrics` packages
- Postinstall scripts that execute code
- Dependencies from GitHub URLs instead of npm registry
- Extremely new packages (created days ago)
- Packages with very few weekly downloads
- Typosquatted names (e.g., `lodahs` instead of `lodash`)

### Python (requirements.txt, setup.py, pyproject.toml)
- `pip install` from GitHub URLs
- Packages with `-` or `_` variations of popular names
- Dependencies not on PyPI
- Setup.py with install hooks

### Go (go.mod)
- Replace directives pointing to unusual forks
- Dependencies from personal GitHub accounts
- Packages with recent ownership transfers

### Ruby (Gemfile)
- Gems from git sources instead of RubyGems
- Gems with post-install hooks

### Common suspicious package names
- `event-stream` (historical malware)
- `flatmap-stream`
- Anything with `miner`, `crypto-` (unless expected)
- `debug-*`, `dev-*` with network capabilities

## Network Red Flags

### URLs to investigate
- Any non-GitHub/GitLab/Bitbucket URLs in install scripts
- Hardcoded IPs (especially in private ranges or unusual ports)
- URL shorteners (bit.ly, tinyurl)
- Dynamic DNS domains (*.ngrok.io, *.serveo.net)
- Recently registered domains
- Domains with unusual TLDs

### Legitimate network activity
- GitHub API (api.github.com) for updates/releases
- Package registries (npmjs.com, pypi.org, crates.io)
- CDNs for assets (unpkg.com, cdnjs.com, jsdelivr.net)
- Official project domains

### Suspicious network activity
- Analytics endpoints (google-analytics, mixpanel, segment, amplitude)
- Any POST requests with collected data
- WebSocket connections to unknown servers
- Multiple different external hosts contacted

## File System Red Flags

### Sensitive paths being accessed
```
~/.ssh/*                 # SSH keys
~/.aws/*                 # AWS credentials
~/.azure/*               # Azure credentials
~/.config/gcloud/*       # GCP credentials
~/.kube/config           # Kubernetes config
~/.docker/config.json    # Docker registry auth
~/.netrc                 # Network credentials
~/.npmrc                 # npm auth tokens
~/.pypirc                # PyPI auth tokens
~/.gitconfig             # Git credentials
~/.bash_history          # Command history
~/.zsh_history           # Command history
~/.*_history             # Various histories
/etc/passwd              # System users
/etc/shadow              # Password hashes
```

### Browser data paths
```
# Chrome
~/Library/Application Support/Google/Chrome/
~/.config/google-chrome/

# Firefox
~/Library/Application Support/Firefox/
~/.mozilla/firefox/

# Safari
~/Library/Safari/
```

### Legitimate file access
- Writing to ~/.config/<appname>/
- Writing to ~/.local/share/<appname>/
- Writing to ~/.cache/<appname>/
- Creating log files in expected locations
