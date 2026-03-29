# Abay Shield - Password Security Toolkit



```markdown
<div align="center">

```text
___    __                   _____ __    _      __    __
   /   |  / /_  ____ ___  __   / ___// /_  (_)__  / /___/ /
  / /| | / __ \/ __ `/ / / /   \__ \/ __ \/ / _ \/ / __  /
 / ___ |/ /_/ / /_/ / /_/ /   ___/ / / / / /  __/ / /_/ /
/_/  |_/_.___/\__,_/\__, /   /____/_/ /_/_/\___/_/\__,_/
                   /____/
```
      ~~~         ~~~
         ~~~   ~~~
            ~~~
    ╔══════════════════════════════════════════╗
    ║     አባይ ጋሻ  |  ABAY SHIELD  |  የአባይ ጋሻ    ║
    ║         Guardian of the Nile             ║
    ╚══════════════════════════════════════════╝

════════════════════════════════════════════════════════════
  🔐 Advanced Password Security Analyzer
  ⚡ Ethiopian Nile - Guardian of Digital Access
════════════════════════════════════════════════════════════

## Features

Password strength evaluation based on:
- Length analysis with graduated scoring
- Uppercase and lowercase letter detection
- Numeric digit inclusion and count
- Special character presence and quantity
- Common password dictionary check (50 most breached passwords)
- Pattern detection (repeated characters, sequential numbers, sequential letters)
- Keyboard pattern recognition (qwerty, asdfgh, etc.)

Advanced security metrics:
- True entropy calculation with pattern penalties
- Three realistic attack modes (online rate-limited, offline fast hash, offline slow hash)
- Human-readable crack time estimates
- JSON report export functionality

User experience:
- Color-coded terminal output
- Animated analysis feedback
- Professional ASCII banner
- Interactive attack mode selection


### Prerequisites

Python 3.7 or higher is required. Verify your installation:
#### python libraries
- pyfiglet
- colorama
```bash
python --versio
```
## Installation

1. Clone the repo:

```bash
git clone https://github.com/YourUsername/abay_shield.git
cd abay_shield
```
2. Install required packages:
```bash
# Install all requirements safely
pip install -r requirements.txt
# In case it crashs 
sudo pip install --break-system-packages pyfiglet colorama

```
3. Run the tool:
```bash
python3 abay_shield.py
```
