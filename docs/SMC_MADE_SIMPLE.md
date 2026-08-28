# 📺 SMC Made Simple: A Friendly Beginner's Guide to Saturday Morning Programming
**The Playful, Biological, Crash-Resistant Language for Everyone**  
*Maintainer: Jason Rezek (`zekvftb@gmail.com`) — v0.7.0*

---

## 🥣 Welcome to Saturday Morning Code!

Remember pouring a giant bowl of sugary cereal in your pajamas on Saturday morning and watching animated heroes save the day? 

**SMC (Saturday Morning Cartoons)** brings that same fun, vibrant energy into modern programming, powered by the incredible information engineering of **DNA and RNA**:

1. **DNA Never Crashes:** Living systems have run software inside biology for 3.8 billion years without a reboot. Biology uses built-in synonyms, self-dissolving messages, and shape-matching locks to keep running even when errors happen.
2. **Coding Should Be Joyful:** We paired those biological superpowers with subtle, nostalgic nods to 90s animation tropes—secret underground labs, magical transformations, falling anvils, and elemental summonings.

Whether you are writing your very first script or building a real-world web application, this guide walks you through every step in plain English.

---

## 🧭 Reader's Guide Icons

* 💡 **Tip:** Handy shortcuts to make coding easier.
* 🧠 **Remember:** Core principles worth remembering.
* 🔬 **Under the Hood:** A peek at the biological computer science (feel free to skim!).
* ⚠️ **Note:** Key details to keep in mind.

---

## 🚀 Chapter 1: The 30-Second Quickstart

You don't need complex compilers or heavy setups to start experimenting with SMC!

### Option A: The Live Web Playground (Zero Install)
1. Open your browser to: **[https://zekvftb.github.io/smc-lang/](https://zekvftb.github.io/smc-lang/)**
2. Click **"Run Code"**.
3. You are now running SMC directly inside your browser!

### Option B: Local Command Line (PC / Mac / Linux)
If you have Python 3.11+ installed:
```powershell
pip install smc-lang
```

Launch the interactive lab shell:
```powershell
smc repl
```

---

## ✍️ Chapter 2: Writing Your First Program ("Hello Toon!")

Every SMC program begins with an **`experiment`** declaration and concludes with **`halt`**:

```smc
experiment "My_First_Adventure"

# Output a message to the console
print "Hello, Saturday Morning!"

# Cleanly stop execution
halt
```

### 🧠 Remember: Comments Start with `#`
Any line beginning with `#` is a **comment**. The computer ignores it—it is just a note for humans reading the code.

---

## 🧪 Chapter 3: Variables (Storing Data in Your Lab)

A **variable** is a labeled container for holding numbers, text, or lists:

```smc
experiment "Laboratory_State"

# Declare variables using 'let'
let player_name = "Hero"
let energy_level = 100
let has_shield = true

# Print formatted messages with template strings
print `Player: ${player_name}`
print `Current Energy: ${energy_level}`

halt
```

### 💡 Tip: Friendly Synonym Aliases
SMC recognizes that programmers appreciate flexible, expressive keywords. You can use standard keywords or playful lab synonyms interchangeably:
* `let speed = 10`
* `set speed = 10`
* `var speed = 10`
* `SUGAR speed = 10`
* `SPICE speed = 10`

---

## 🦸 Chapter 4: The 5 Biological Cartoon Superpowers

Here is where SMC does things traditional languages cannot!

### 💥 Superpower 1: Typo-Tolerance (Wobble Codon Repair)
* **The Problem:** In rigid languages, a single misspelled keyword (`prnt` instead of `print`) crashes the program immediately.
* **The Biological Fix:** Just as ribosomes tolerate small genetic wobble mutations in DNA codons, the SMC compiler automatically repairs minor typing slips without halting:

```smc
experiment "Wobble_Repair_Demo"

let power = 50
# Notice the minor slip? 'prnt' is smoothly repaired!
prnt `Power output: ${power}`

halt
```

---

### 📦 Superpower 2: The Anvil Ephemeral Memory (Self-Cleaning RAM)
* **The Problem:** Temporary items like session tokens clutter memory until a heavy garbage collector pauses the CPU to clean them up.
* **The Biological Fix:** In cells, messenger RNA naturally dissolves after being read. In SMC, you can attach an ephemeral timer (`ttl=N` steps):

```smc
experiment "Ephemeral_Memory"

let permanent_user = "Lead_Scientist"

# This variable will only live for 2 execution cycles!
acme(ttl=2) one_time_passcode = "TEMP_98234"

print `Active Passcode: ${one_time_passcode}`
print "Cycle 1: Working..."
print "Cycle 2: Working..."

# The temporary passcode gently vaporizes from RAM with zero memory leaks!
halt
```

---

### 🌙 Superpower 3: Magical State Evolution (`mpp`)
* **The Concept:** Cells differentiate from stem cells into specialized tissues. In animated lore, characters undergo dramatic transformations to evolve their abilities.
* **In SMC:** Use the **`mpp`** (Magical Power Progression) block to evolve state:

```smc
experiment "Evolution_Demo"

let hero_status = "Apprentice"

# Evolve the hero into a Champion!
mpp hero_status = "Champion" {
    print "State evolved to elite tier!"
}

print `Status: ${hero_status}`
halt
```

---

### 💍 Superpower 4: Elemental Ring Dispatch (Shape-Matching Routing)
* **The Problem:** Traditional programming relies on fragile memory addresses and hardcoded URLs.
* **The Biological Fix:** Proteins find targets through physical lock-and-key shapes. In SMC, routines bind to elemental rings (`EARTH`, `FIRE`, `WIND`, `WATER`, `HEART`):

```smc
experiment "Elemental_Rings"

# 1. Bind routines to elemental shapes
bind(ring="FIRE") {
    print "Flame burst activated!"
}
bind(ring="WIND") {
    print "Whirlwind vortex engaged!"
}

# 2. Dispatch events by shape name (case-coerced automatically)
dispatch "fire"
dispatch "wind"

halt
```

### 🌹 The Tuxedo Watchdog Fallback
If code dispatches to an unbound ring, the fallback checkpoint gracefully catches it:
```smc
fallback {
    print "A mysterious ally steps in! (Graceful backup executed)"
}

# Unbound ring is caught safely without crashing!
dispatch "UNKNOWN_ELEMENT"
```

---

### 🧬 Superpower 5: HexaPhase 6-Track Multiplexing
* **The Biological Principle:** Viral genomes pack multiple overlapping genes onto 6 reading phases within the same sequence.
* **In SMC:** You can multiplex any stream into 6 concurrent channels:

```smc
experiment "HexaPhase_Channels"

# Slices the sequence across all 6 reading phases (+0, +1, +2, -0, -1, -2)
hexaphase "ATGCGATCGATC" {
    let track_0 = hexaphase_channels["+0"]
    let track_1 = hexaphase_channels["+1"]
    let reverse_0 = hexaphase_channels["-0"]

    print `Forward Track 0: ${track_0}`
    print `Forward Track 1: ${track_1}`
}

halt
```

---

## 🛠️ Chapter 5: Collections (Lists & Dictionaries)

### Lists (Ordered Sequences)
Lists store multiple items in order (0-indexed, with safe negative indexing from the end):
```smc
let squad = ["Leader", "Technician", "Pilot", "Scout"]

print squad[0]   # "Leader"
print squad[-1]  # "Scout" (grabs the last item)
```

### Dictionaries (Key-Value Records)
Dictionaries store data with descriptive property labels:
```smc
let bot = {
    "name": "Sparky",
    "battery": 100,
    "speed": 85
}

print bot["name"]     # "Sparky"
bot["battery"] -= 15  # Compound update to 85
```

---

## 🔁 Chapter 6: Control Flow (Decisions & Loops)

### If / Else Conditions
```smc
let shield_integrity = 25

if (shield_integrity > 50) {
    print "Defenses holding strong."
} else {
    print "Shield energy critical!"
}
```

### While Loops (Countdown Timers)
```smc
let timer = 3
while (timer > 0) {
    print `Launch in: ${timer}`
    timer -= 1
}
print "Liftoff!"
```

### For-In Loops (Iterating Collections)
```smc
let supplies = ["Energy Cell", "Scanner", "Toolkit"]

for item in supplies {
    print "Equipped: " + item
}
```

---

## 🌐 Chapter 7: Mini-Project: A 10-Line Web Server!

SMC includes a native HTTP server engine so you can spin up responsive web applications in seconds:

```smc
experiment "Mini_Web_Service"

fn route_handler(req) {
    let path = req["path"]

    if (path == "/status") {
        return "<h1>Lab Status: 100% Optimal</h1><p>Running on SMC v0.7.0</p>"
    }

    return "<h1>Welcome to the Secret Lab!</h1><a href='/status'>Check Status</a>"
}

# Start server listening on port 8080
print "Lab Web Server listening on http://localhost:8080"
serve_http(8080, "route_handler")

halt
```

---

## 📋 Chapter 8: The SMC Quick Reference Card

| Task | How to write it in SMC |
| :--- | :--- |
| **Start program** | `experiment "Name"` |
| **End program** | `halt` |
| **Declare variable** | `let x = 10` (or `SUGAR x = 10`) |
| **Self-destruct variable** | `acme(ttl=3) temp = "Value"` |
| **Print text** | `print "Hello"` |
| **Template string** | `` `Value: ${val}` `` |
| **Define function** | `fn add(a, b) { return a + b }` |
| **Create list** | `let items = [1, 2, 3]` |
| **Create dictionary** | `let user = { "name": "Alex", "level": 5 }` |
| **If / Else** | `if (x > 5) { ... } else { ... }` |
| **Loop list** | `for item in items { print item }` |
| **Elemental Ring Dispatch** | `bind(ring="FIRE") { ... }` followed by `dispatch "FIRE"` |
| **HexaPhase 6-Track Slicing**| `hexaphase "STREAM" { let p0 = hexaphase_channels["+0"] }` |
| **Call Python Code** | `let root = py_call("math.sqrt", 64)` |

---

## 🏆 The 10 Golden Guidelines of SMC
1. **Case-Insensitive Keywords:** `LET`, `let`, and `Let` are identical.
2. **Case-Sensitive Identifiers:** `power` and `Power` are distinct variable names.
3. **No Semicolon Traps:** Freeform formatting without semicolon syntax crashes.
4. **Zero-Crash Arithmetic:** `10 / 0` evaluates safely to `0` with a diagnostic warning.
5. **Zero-Crash Lookups:** Reading unassigned variables yields `0` or `""` safely.
6. **Negative List Indexing:** `items[-1]` grabs the final element.
7. **Self-Cleaning RAM:** Ephemeral variables dissolve on TTL expiration without CPU pauses.
8. **Shape-Based Routing:** Dispatch by categorical shape instead of brittle pointers.
9. **Zero Dependencies:** Runs standalone on any standard computer with 0 extra packages.
10. **Joyful Productivity:** Saturday Morning Cartoons makes software development fun again!

---

*Igu.aa yáx x'wán — Have courage, stand strong, and happy coding!*
