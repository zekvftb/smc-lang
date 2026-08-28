# 📺 SMC Made Simple: The Absolute Beginner's Guide to Saturday Morning Cartoons Programming
**A Fun, Plain-English Guide to Writing Biological, Crash-Resistant Code**  
*Maintainer: Jason Rezek (`zekvftb@gmail.com`) — v0.7.0*

---

## 🌟 Welcome to SMC!

If regular programming languages like C, Java, or Python feel like strict, grumpy math teachers who scream `SyntaxError` every time you miss a semicolon... **welcome home.**

**SMC (Saturday Morning Cartoons)** is a programming language built on two simple ideas:
1. **DNA Never Crashes:** DNA has been running software inside living organisms for 3.8 billion years without a reboot. It uses clever biological tricks (synonyms, expiring messages, shape-matching) to ignore bugs and keep running.
2. **Programming Should Be Fun:** We wrapped those biological superpowers inside the nostalgic universe of 90s cartoons—**Dexter’s Lab, The Powerpuff Girls, Captain Planet, Sailor Moon, and Looney Tunes**.

Whether you're a complete novice who has never written a line of code in your life or a seasoned software engineer looking for a refreshing, fault-tolerant runtime, this guide is for you.

---

## 🧭 Icons Used in This Guide

* 💡 **Tip:** Helpful tricks to save time.
* 🧠 **Remember:** Core concepts to keep in mind.
* 🔬 **Technical Stuff:** What’s happening under the hood (skip if you just want to code!).
* ⚠️ **Watch Out:** Traps and gotchas to avoid.

---

## 🚀 Chapter 1: The 30-Second Quickstart

You don’t even need to install anything on your computer to start coding in SMC!

### Option A: The Zero-Install Web Playground
1. Open your browser and go to: **[https://zekvftb.github.io/smc-lang/](https://zekvftb.github.io/smc-lang/)**
2. Click **"Run Code"**.
3. You are now running SMC directly in your web browser!

### Option B: Install on Your PC (Windows, Mac, or Linux)
If you have Python 3.11 or newer installed:
```powershell
pip install smc-lang
```

Launch the interactive laboratory shell (the REPL):
```powershell
smc repl
```

---

## ✍️ Chapter 2: Writing Your First Program ("Hello Toon!")

Every SMC program starts with an **`experiment`** name and ends with **`halt`** (or `THATS_ALL_FOLKS`):

```smc
experiment "My_First_Toon"

# Output a friendly message to the screen
print "Hello, Saturday Morning!"

# Cleanly stop the program
halt
```

### 🧠 Remember: Comments Start with `#`
Any line starting with `#` is a **comment**. The computer ignores it—it's just a note for humans reading the code.

---

## 🧪 Chapter 3: Variables (Storing Information in Dexter's Lab)

A **variable** is just a labeled box where you store numbers, text, or lists.

```smc
experiment "Chemical_Variables"

# Create some variables using 'let'
let player_name = "Dexter"
let player_level = 1
let health_points = 100
let has_magic_shield = true

# Print them out
print "Player: " + player_name
print `Current HP: ${health_points}`

halt
```

### 💡 Tip: You Can Use Cartoon Synonyms!
SMC understands that humans make typos and love fun keywords. All of these mean the exact same thing:
* `let score = 10`
* `set score = 10`
* `var score = 10`
* `SUGAR score = 10`
* `SPICE score = 10`
* `EVERYTHING_NICE score = 10`

---

## 🦸 Chapter 4: The 5 Cartoon Superpowers

Here is where SMC does things no other programming language can do!

### 💥 Superpower 1: Typo-Tolerance (Wobble Codon Repair)
* **The Problem:** In Python or C, if you accidentally type `prnt "hi"` or `whle (x < 5)`, your program immediately crashes with a `SyntaxError`.
* **The SMC Solution:** Just like DNA tolerates small mutations in genetic codons, SMC's compiler uses **Wobble Tolerance**. It automatically fixes minor typos without stopping:

```smc
experiment "Typo_Magic"

# Notice the typos? 'prnt' and 'ltt' still work!
let score = 50
prnt `Your score is: ${score}`

halt
```

---

### 📦 Superpower 2: Acme Anvil Ephemeral Memory (Self-Destructing RAM)
* **The Problem:** In regular languages, if you create thousands of temporary variables (like session tokens or cache items), they sit in RAM forever until a "Garbage Collector" freezes your CPU to clean them up.
* **The SMC Solution:** In biology, mRNA transcripts naturally dissolve after a few minutes. In SMC, you can attach an **Acme Anvil** with a Time-To-Live (`ttl=N`):

```smc
experiment "Acme_Demo"

let persistent_player = "Dexter"

# This variable will ONLY live for 2 execution steps!
acme(ttl=2) temporary_passcode = "SECRET_999"

print `Active Passcode: ${temporary_passcode}`
print "Step 1: Doing some work..."
print "Step 2: Doing more work..."

# *ANVIL DROPS* -> temporary_passcode auto-vaporizes from RAM with zero memory leaks!
halt
```

---

### 🌙 Superpower 3: Sailor Moon Transformations (`mpp`)
* **The Concept:** In biology, a stem cell transforms into a bone cell or heart cell. In Sailor Moon, Usagi shouts *"Moon Prism Power!"* to evolve into Sailor Moon.
* **In SMC:** Use the **`mpp`** (Moon Prism Power) keyword to evolve state:

```smc
experiment "Transformation_Demo"

let hero = "Usagi"

# Evolve the hero into Princess Serenity!
mpp hero = "Princess_Serenity" {
    print "State transformed to royal tier!"
}

print `Current Hero Status: ${hero}`

halt
```

---

### 💍 Superpower 4: Captain Planet Ring Dispatch (No IP Addresses Needed!)
* **The Problem:** In standard coding, you have to remember complex function pointers (`0x7FFF`) or hard-coded URLs.
* **The SMC Solution:** Functions bind to **elemental rings** (`EARTH`, `FIRE`, `WIND`, `WATER`, `HEART`). Anyone can shout an element to trigger the matching power:

```smc
experiment "Planeteers_Assemble"

# 1. Teach the computer what happens when 'FIRE' is called
bind(ring="FIRE") {
    print "Wheeler shoots a burst of fire!"
}

# 2. Teach the computer what happens when 'WIND' is called
bind(ring="WIND") {
    print "Linka summons a whirlwind!"
}

# 3. Trigger them by name! (Case doesn't even matter)
dispatch "fire"
dispatch "wind"

halt
```

### 🌹 Tuxedo Mask Fallback Checkpoint
What if someone dispatches an element that hasn't been created yet? Instead of crashing, **Tuxedo Mask** gracefully steps in:

```smc
fallback {
    print "Tuxedo Mask throws a red rose! (Graceful backup executed)"
}

# This ring doesn't exist, but Tuxedo Mask catches it!
dispatch "UNKNOWN_PLANET"
```

---

### 🧬 Superpower 5: HexaPhase 6-Track Multiplexing
* **The Biological Principle:** DNA encodes multiple genes on overlapping reading tracks (+0, +1, +2, -0, -1, -2).
* **In SMC:** You can slice a single string of data into 6 independent channels at the exact same time:

```smc
experiment "HexaPhase_Demo"

# Slices the sequence across all 6 reading phases
hexaphase "ATGCGATCGATC" {
    let forward_track_0 = hexaphase_channels["+0"]
    let forward_track_1 = hexaphase_channels["+1"]
    let reverse_track_0 = hexaphase_channels["-0"]

    print `Forward 0: ${forward_track_0}`
    print `Forward 1: ${forward_track_1}`
}

halt
```

---

## 🛠️ Chapter 5: Collections (Lists & Dictionaries)

### Lists (Arrays of Items)
Lists hold multiple items in order (starting at index 0):
```smc
let cartoons = ["Dexter", "Powerpuff Girls", "Johnny Bravo", "Courage"]

print cartoons[0]   # "Dexter"
print cartoons[1]   # "Powerpuff Girls"
print cartoons[-1]  # "Courage" (negative index grabs from the end!)
```

### Dictionaries (Key-Value Pairs)
Dictionaries let you store information with descriptive keys:
```smc
let hero_stats = {
    "name": "Buttercup",
    "power": 900,
    "speed": 750
}

print hero_stats["name"]    # "Buttercup"
hero_stats["power"] += 50   # Boost power to 950!
```

---

## 🔁 Chapter 6: Control Flow (Loops & If/Else)

### If / Else Decisions
```smc
let enemy_hp = 0

if (enemy_hp <= 0) {
    print "Victory! The villain was defeated!"
} else {
    print "Keep fighting!"
}
```

### While Loops (Repeating Until Done)
```smc
let count = 1
while (count <= 3) {
    print `Countdown: ${count}`
    count += 1
}
print "Blast off!"
```

### For-In Loops (Iterating Over Lists)
```smc
let ingredients = ["Sugar", "Spice", "Chemical X"]

for item in ingredients {
    print "Adding: " + item
}
```

---

## 🌐 Chapter 7: Mini-Project: A 10-Line Web Server!

SMC comes with a built-in web server! You can launch a real HTTP website in seconds:

```smc
experiment "My_First_Website"

fn my_web_handler(req) {
    let path = req["path"]
    
    if (path == "/about") {
        return "<h1>About Dexter's Secret Lab</h1><p>Built with 100% SMC code!</p>"
    }
    
    return "<h1>Welcome to Saturday Morning Cartoons!</h1><a href='/about'>Go to About</a>"
}

# Start listening on port 8080!
print "Visit http://localhost:8080 in your browser!"
serve_http(8080, "my_web_handler")

halt
```

---

## 📋 Chapter 8: The SMC Cheat Sheet

| Task | How to write it in SMC |
| :--- | :--- |
| **Start a program** | `experiment "Name"` |
| **End a program** | `halt` |
| **Create a variable** | `let x = 10` (or `SUGAR x = 10`) |
| **Self-destruct variable** | `acme(ttl=3) temp = "Value"` |
| **Print to screen** | `print "Hello"` (or `KAMEHAMEHA "Hello"`) |
| **Format a template string** | `` `Score: ${points}` `` |
| **Make a function** | `fn add(a, b) { return a + b }` |
| **Make a list** | `let items = [1, 2, 3]` |
| **Make a dictionary** | `let user = { "name": "Dexter", "age": 10 }` |
| **If / Else** | `if (x > 5) { ... } else { ... }` |
| **Loop over a list** | `for item in items { print item }` |
| **Planeteer Ring Dispatch** | `bind(ring="FIRE") { ... }` followed by `dispatch "FIRE"` |
| **HexaPhase 6-Track Slice**| `hexaphase "ATGC" { let f0 = hexaphase_channels["+0"] }` |
| **Call Python Code** | `let root = py_call("math.sqrt", 64)` |

---

## 🏆 The Top 10 Rules of SMC
1. **Case-Insensitive Keywords:** `LET`, `let`, and `Let` all work identically.
2. **Case-Sensitive Variables:** `speed` and `Speed` are two different variables.
3. **No Semicolons Required:** Just hit Enter and keep typing.
4. **Zero-Crash Division:** `10 / 0` evaluates safely to `0` with a warning instead of crashing.
5. **Zero-Crash Missing Variables:** Reading an unassigned variable gives you `0` or `""` safely.
6. **Negative List Indexing:** `list[-1]` grabs the last element.
7. **Acme TTL Cleanups:** Ephemeral memory cleans itself up without Garbage Collector freezes.
8. **Shape-Matching Routing:** Use `bind` and `dispatch` instead of hard-coded memory pointers.
9. **Zero Dependencies:** SMC runs completely standalone with 0 external packages.
10. **Have Fun!** Saturday Morning Cartoons is designed to put the joy back into programming!

---

*Igu.aa yáx x'wán — Have courage, stand strong, and happy hacking!*
