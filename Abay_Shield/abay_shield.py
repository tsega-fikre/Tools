#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           ABAY SHIELD - Password Security Toolkit              ║
║                         Ethiopian Nile - Guardian of Access                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Author: [Your Name]
Version: 2.0
Description: Advanced password strength analyzer with realistic crack time
             estimation, dictionary attack simulation, and professional UI.
"""

import re
import math
import time
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

try:
    from pyfiglet import Figlet
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("Please install required packages: pip install pyfiglet colorama")
    sys.exit(1)

# ==============================================================================
# ASCII ART & BANNERS
# ==============================================================================

NILE_ASCII = r"""
      ~~~         ~~~
         ~~~   ~~~
            ~~~
    ╔══════════════════════════════════════════╗
    ║     አባይ ጋሻ  |  ABAY SHIELD  |  የአባይ ጋሻ    ║
    ║         Guardian of the Nile             ║
    ╚══════════════════════════════════════════╝
"""

# Common password list (top 50 most common passwords)
COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "abc123", "password123",
    "admin", "letmein", "welcome", "monkey", "dragon", "master", "sunshine",
    "passw0rd", "shadow", "superman", "fuckyou", "baseball", "football",
    "trustno1", "iloveyou", "starwars", "whatever", "nicole", "jessica",
    "michael", "ashley", "mustang", "pepper", "buster", "bailey", "charlie",
    "soccer", "hockey", "batman", "andrew", "thomas", "robert", "jordan",
    "hunter", "ranger", "thunder", "harley", "ginger", "princess", "samantha",
    "jasmine", "london", "paris", "canada"
}

# ==============================================================================
# CRACK TIME MODELS
# ==============================================================================

ATTACK_MODES = {
    "online": {
        "name": "🌐 Online Attack (rate-limited)",
        "guesses_per_second": 100,
        "description": "Attacking a live website with rate limiting"
    },
    "offline_fast": {
        "name": "⚡ Offline Fast Hash (MD5/SHA1)",
        "guesses_per_second": 1_000_000_000,  # 1 billion/sec
        "description": "Cracking weak hashes on modern GPU cluster"
    },
    "offline_slow": {
        "name": "🐢 Offline Slow Hash (bcrypt/Argon2)",
        "guesses_per_second": 100_000,  # 100k/sec
        "description": "Cracking properly salted slow hashes"
    }
}

# ==============================================================================
# MAIN CHECKER CLASS
# ==============================================================================

class AbayShield:
    """
    Advanced Password Strength Checker with realistic security analysis.
    Named after the Blue Nile (Abay) - symbolizing the flow of security.
    """
    
    def __init__(self, password: str, attack_mode: str = "offline_fast"):
        self.password = password
        self.attack_mode = attack_mode
        self.score = 0
        self.max_score = 8  # Increased max score for more granularity
        self.feedback = []
        self.warnings = []
        self.successes = []
        
    def animate_analysis(self):
        """Show animated loading effect"""
        print(f"\n{Fore.CYAN}🔍 Analyzing password security", end="")
        for _ in range(4):
            time.sleep(0.2)
            print(".", end="", flush=True)
        print(f" {Fore.GREEN}✓{Style.RESET_ALL}\n")
    
    def check_length(self) -> int:
        """Check password length with advanced scoring"""
        length = len(self.password)
        
        if length < 6:
            self.feedback.append(f"❌ Length {length} chars - Too short! Minimum 8 required")
            self.warnings.append("Extremely short password")
        elif length < 8:
            self.feedback.append(f"⚠️ Length {length} chars - Weak, needs at least 8")
            self.warnings.append("Short password")
            self.score += 0.5
        elif length < 12:
            self.feedback.append(f"✅ Length {length} chars - Acceptable")
            self.score += 1
        elif length < 16:
            self.feedback.append(f"✅ Length {length} chars - Good")
            self.score += 1.5
        else:
            self.feedback.append(f"✅ Length {length} chars - Excellent!")
            self.score += 2
            
        return length
    
    def check_case_variety(self) -> Tuple[bool, bool]:
        """Check uppercase and lowercase usage"""
        has_upper = any(c.isupper() for c in self.password)
        has_lower = any(c.islower() for c in self.password)
        
        if has_upper and has_lower:
            self.feedback.append("✅ Contains both uppercase & lowercase letters")
            self.score += 1.5
            self.successes.append("Mixed case detected")
        elif has_upper or has_lower:
            self.feedback.append("⚠️ Use BOTH uppercase and lowercase letters")
            self.warnings.append("Missing case variety")
        else:
            self.feedback.append("❌ No letters detected - Very weak!")
            self.warnings.append("No alphabetic characters")
            
        return has_upper, has_lower
    
    def check_numbers(self) -> bool:
        """Check for numeric digits"""
        has_digit = any(c.isdigit() for c in self.password)
        
        # Count digits for bonus
        digit_count = sum(1 for c in self.password if c.isdigit())
        
        if has_digit:
            if digit_count >= 3:
                self.feedback.append(f"✅ Good - {digit_count} numbers found")
                self.score += 1
            else:
                self.feedback.append("✅ Contains numbers")
                self.score += 0.5
            self.successes.append("Numbers included")
        else:
            self.feedback.append("⚠️ Add numbers to increase strength")
            self.warnings.append("No numeric digits")
            
        return has_digit
    
    def check_special_chars(self) -> bool:
        """Check for special characters"""
        special_pattern = r'[!@#$%^&*(),.?":{}|<>~`_\-+=;\/\[\]]'
        specials = re.findall(special_pattern, self.password)
        has_special = len(specials) > 0
        
        if has_special:
            if len(specials) >= 2:
                self.feedback.append(f"✅ Great - {len(specials)} special characters")
                self.score += 1.5
            else:
                self.feedback.append("✅ Contains special characters")
                self.score += 0.5
            self.successes.append("Special characters included")
        else:
            self.feedback.append("⚠️ Add special characters (!@#$% etc)")
            self.warnings.append("No special characters")
            
        return has_special
    
    def check_common_password(self) -> bool:
        """Check against common password dictionary"""
        password_lower = self.password.lower()
        
        if password_lower in COMMON_PASSWORDS:
            self.feedback.append(f"❌ CRITICAL: '{self.password}' is a known common password!")
            self.warnings.append("Password appears in breach databases")
            self.score -= 2
            return True
        return False
    
    def check_patterns(self) -> None:
        """Detect common weak patterns"""
        patterns_found = []
        
        # Repeated characters (e.g., aaaa, 1111)
        if re.search(r'(.)\1{3,}', self.password):
            patterns_found.append("repeated characters (aaaa)")
            self.score -= 1
            
        # Sequential numbers (1234, 5678)
        if re.search(r'(012|123|234|345|456|567|678|789|890)', self.password):
            patterns_found.append("sequential numbers")
            self.score -= 0.5
            
        # Sequential letters (abcd, qwerty)
        if re.search(r'(abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)', 
                    self.password.lower()):
            patterns_found.append("sequential letters")
            self.score -= 0.5
            
        # Keyboard patterns
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', '1qaz', 'qazwsx', 'wsxedc']
        for pattern in keyboard_patterns:
            if pattern in self.password.lower():
                patterns_found.append("keyboard pattern detected")
                self.score -= 1
                break
                
        if patterns_found:
            self.feedback.append(f"⚠️ Pattern detected: {', '.join(patterns_found)}")
            self.warnings.append(f"Weak patterns: {', '.join(patterns_found)}")
    
    def calculate_entropy(self) -> Tuple[float, int]:
        """Calculate true password entropy"""
        char_set_size = 0
        if any(c.islower() for c in self.password):
            char_set_size += 26
        if any(c.isupper() for c in self.password):
            char_set_size += 26
        if any(c.isdigit() for c in self.password):
            char_set_size += 10
        special_chars = r'!@#$%^&*(),.?":{}|<>~`_\-+=;\/\[\]]'
        if any(c in special_chars for c in self.password):
            char_set_size += len(special_chars)
            
        # Apply pattern penalty (reduces effective entropy)
        pattern_penalty = 1.0
        if self.check_common_password():
            pattern_penalty = 0.3
        elif any(c.isdigit() for c in self.password) and len(self.password) < 12:
            pattern_penalty = 0.7
            
        entropy = len(self.password) * math.log2(char_set_size) * pattern_penalty if char_set_size > 0 else 0
        return max(0, entropy), char_set_size
    
    def estimate_crack_time(self) -> Dict:
        """Realistic crack time estimation based on attack mode"""
        entropy, char_set_size = self.calculate_entropy()
        
        if char_set_size == 0 or entropy == 0:
            return {
                "time": "Impossible to estimate",
                "seconds": float('inf'),
                "mode": ATTACK_MODES[self.attack_mode]["name"]
            }
            
        combinations = char_set_size ** len(self.password)
        gps = ATTACK_MODES[self.attack_mode]["guesses_per_second"]
        seconds = combinations / gps
        
        # Human readable format
        if seconds < 1:
            time_str = f"{seconds*1000:.0f} milliseconds"
        elif seconds < 60:
            time_str = f"{seconds:.1f} seconds"
        elif seconds < 3600:
            time_str = f"{seconds/60:.1f} minutes"
        elif seconds < 86400:
            time_str = f"{seconds/3600:.1f} hours"
        elif seconds < 31536000:
            time_str = f"{seconds/86400:.1f} days"
        elif seconds < 315360000:  # 10 years
            time_str = f"{seconds/31536000:.1f} years"
        else:
            time_str = f"{seconds/31536000:.0f}+ years"
            
        return {
            "time": time_str,
            "seconds": seconds,
            "mode": ATTACK_MODES[self.attack_mode]["name"],
            "description": ATTACK_MODES[self.attack_mode]["description"]
        }
    
    def get_strength_label(self) -> Tuple[str, str]:
        """Get strength label with color code"""
        score_normalized = min(self.score / self.max_score, 1.0)
        
        if score_normalized < 0.25:
            return "CRITICAL", Fore.RED
        elif score_normalized < 0.5:
            return "WEAK", Fore.YELLOW
        elif score_normalized < 0.7:
            return "MODERATE", Fore.CYAN
        elif score_normalized < 0.85:
            return "STRONG", Fore.GREEN
        else:
            return "VERY STRONG", Fore.LIGHTGREEN_EX
    
    def generate_report(self) -> Dict:
        """Generate complete analysis report"""
        self.animate_analysis()
        
        # Run all checks
        length = self.check_length()
        self.check_case_variety()
        self.check_numbers()
        self.check_special_chars()
        self.check_common_password()
        self.check_patterns()
        
        # Ensure score doesn't go negative
        self.score = max(0, min(self.score, self.max_score))
        
        entropy, char_set = self.calculate_entropy()
        crack_info = self.estimate_crack_time()
        strength_label, strength_color = self.get_strength_label()
        
        return {
            "password_masked": "*" * len(self.password),
            "length": length,
            "score": round(self.score, 1),
            "max_score": self.max_score,
            "strength": strength_label,
            "strength_color": strength_color,
            "entropy_bits": round(entropy, 2),
            "character_set_size": char_set,
            "crack_time": crack_info,
            "feedback": self.feedback,
            "warnings": self.warnings,
            "successes": self.successes,
            "timestamp": datetime.now().isoformat()
        }


# ==============================================================================
# UI FUNCTIONS
# ==============================================================================

def print_banner():
    """Display professional banner"""
    f = Figlet(font='slant')
    print(Fore.CYAN + Style.BRIGHT + f.renderText('Abay Shield') + Style.RESET_ALL)
    print(Fore.YELLOW + NILE_ASCII + Style.RESET_ALL)
    print(Fore.LIGHTBLUE_EX + "═" * 60)
    print(Fore.WHITE + "  🔐 Advanced Password Security Analyzer")
    print(Fore.WHITE + "  ⚡ Ethiopian Nile - Guardian of Digital Access")
    print(Fore.LIGHTBLUE_EX + "═" * 60 + "\n")


def print_progress_bar(seconds: float, width: int = 30):
    """Display a progress bar simulation"""
    print(f"{Fore.CYAN}⏱️  Estimating crack time", end=" ")
    for i in range(width):
        time.sleep(seconds / (width * 10))
        sys.stdout.write(f"{Fore.GREEN}█" if i < width//2 else f"{Fore.YELLOW}█")
        sys.stdout.flush()
    print(f"{Style.RESET_ALL} ✓\n")


def export_report(report: Dict, filename: str = "abay_shield_report.json"):
    """Export analysis to JSON file"""
    export_data = {
        "tool": "Abay Shield",
        "version": "2.0",
        "report": report
    }
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"{Fore.GREEN}📄 Report exported to {filename}{Style.RESET_ALL}")


def print_results(report: Dict):
    """Display formatted results"""
    strength_color = report['strength_color']
    
    print(Fore.LIGHTBLUE_EX + "╔" + "═" * 58 + "╗")
    print(Fore.LIGHTBLUE_EX + "║" + " 📊 ANALYSIS RESULTS ".center(58) + Fore.LIGHTBLUE_EX + "║")
    print(Fore.LIGHTBLUE_EX + "╚" + "═" * 58 + "╝\n")
    
    # Basic info
    print(f"{Fore.WHITE}📝 Password:{Style.RESET_ALL} {report['password_masked']}")
    print(f"{Fore.WHITE}📏 Length:{Style.RESET_ALL} {report['length']} characters")
    print(f"{Fore.WHITE}🎯 Score:{Style.RESET_ALL} {report['score']}/{report['max_score']}")
    
    # Strength with color
    print(f"{Fore.WHITE}⚡ Strength:{Style.RESET_ALL} {strength_color}{report['strength']}{Style.RESET_ALL}")
    
    # Entropy
    entropy_color = Fore.GREEN if report['entropy_bits'] > 60 else (Fore.YELLOW if report['entropy_bits'] > 40 else Fore.RED)
    print(f"{Fore.WHITE}🔢 Entropy:{Style.RESET_ALL} {entropy_color}{report['entropy_bits']} bits{Style.RESET_ALL}")
    
    # Crack time
    print(f"\n{Fore.LIGHTBLUE_EX}⏱️  CRACK TIME ESTIMATE{Style.RESET_ALL}")
    print(f"   Mode: {report['crack_time']['mode']}")
    print(f"   {report['crack_time']['description']}")
    print(f"   {Fore.CYAN}→ {report['crack_time']['time']}{Style.RESET_ALL}")
    
    # Feedback
    if report['feedback']:
        print(f"\n{Fore.LIGHTBLUE_EX}📋 DETAILED FEEDBACK{Style.RESET_ALL}")
        for item in report['feedback']:
            if "❌" in item:
                print(f"  {Fore.RED}{item}{Style.RESET_ALL}")
            elif "⚠️" in item:
                print(f"  {Fore.YELLOW}{item}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.GREEN}{item}{Style.RESET_ALL}")
    
    # Warnings summary
    if report['warnings']:
        print(f"\n{Fore.RED}⚠️ SECURITY WARNINGS{Style.RESET_ALL}")
        for warning in report['warnings']:
            print(f"  • {warning}")
    
    # Successes
    if report['successes']:
        print(f"\n{Fore.GREEN}✓ GOOD PRACTICES{Style.RESET_ALL}")
        for success in report['successes']:
            print(f"  • {success}")
    
    print("\n" + Fore.LIGHTBLUE_EX + "═" * 60 + Style.RESET_ALL)


def interactive_mode():
    """Main interactive CLI"""
    print_banner()
    
    while True:
        print(f"\n{Fore.CYAN}Available attack modes:{Style.RESET_ALL}")
        for key, mode in ATTACK_MODES.items():
            print(f"  [{key}] {mode['name']}")
        
        attack_mode = input(f"\n{Fore.YELLOW}Select attack mode [offline_fast]: {Style.RESET_ALL}").strip().lower()
        if attack_mode not in ATTACK_MODES:
            attack_mode = "offline_fast"
            print(f"{Fore.CYAN}Using default: {ATTACK_MODES[attack_mode]['name']}{Style.RESET_ALL}")
        
        password = input(f"\n{Fore.YELLOW}Enter password to analyze (or 'quit' to exit): {Style.RESET_ALL}").strip()
        
        if password.lower() in ['quit', 'exit', 'q']:
            print(f"\n{Fore.GREEN}🔒 Stay secure! Abay Shield protects the Nile and your data.{Style.RESET_ALL}\n")
            break
        
        if not password:
            print(f"{Fore.RED}⚠️ Password cannot be empty.{Style.RESET_ALL}")
            continue
        
        # Analyze
        analyzer = AbayShield(password, attack_mode)
        report = analyzer.generate_report()
        
        # Show progress simulation
        if report['crack_time']['seconds'] != float('inf'):
            print_progress_bar(min(2, report['crack_time']['seconds'] / 1e6), 40)
        
        # Display results
        print_results(report)
        
        # Ask for export
        export_choice = input(f"\n{Fore.YELLOW}Export report to JSON? (y/n): {Style.RESET_ALL}").strip().lower()
        if export_choice == 'y':
            export_report(report)


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️ Interrupted. Stay secure!{Style.RESET_ALL}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
