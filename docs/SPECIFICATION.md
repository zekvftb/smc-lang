# 📐 SMC (Saturday Morning Cartoons) Formal Language Specification
**Version:** 0.7.0 (The HexaPhase Edition)  
**Status:** Implementation-Ready Standard Reference  
**Maintainer:** Jason Rezek (`zekvftb@gmail.com`)  
**Runtime:** DexterVM Standalone Virtual Machine Engine  

---

## 1. Lexical Grammar & Codon Degeneracy

### 1.1 Codon Wobble Typo-Tolerance & Synonyms
SMC treats keywords as degenerate codons. Multiple synonym tokens resolve to the same internal opcode. Furthermore, if a token does not match exactly, the **Wobble Resolver** calculates the Levenshtein edit distance:
* For tokens of length $\le 4$: Allows edit distance $\le 1$.
* For tokens of length $\ge 5$: Allows edit distance $\le 2$ (with length $\le 6$ guarded to distance $\le 1$ to prevent keyword collisions like `report` $\rightarrow$ `import`).

#### Canonical Opcode & Synonym Map
| Canonical Opcode | Standard Keyword | Cartoon / Biological Synonyms | Grammar Description |
| :--- | :--- | :--- | :--- |
| `EXPERIMENT` | `experiment` | `program`, `module`, `secret_lab`, `dexter_lab_experiment`, `omnitrix_init` | Declares program module header |
| `SET_VAR` | `let` | `set`, `var`, `sugar`, `spice`, `everything_nice`, `chemical_x` | Variable assignment statement |
| `TTL_BOX` | `acme(ttl=N)` | `acme_anvil_box`, `acme_box`, `ephemeral`, `anvil_box`, `disposable_var` | Declares ephemeral TTL variable |
| `IF` | `if` | `when`, `check_gate`, `test` | Conditional branch |
| `ELSE` | `else` | `otherwise`, `default` | Alternative branch |
| `WHILE` | `while` | `loop`, `cycle`, `road_runner_loop` | Conditional loop |
| `FOR` | `for` | `each`, `for_each`, `iterate` | Collection iteration loop |
| `IN` | `in` | `inside`, `from` | Iterator separator |
| `FN` | `fn` | `function`, `def`, `subroutine`, `recipe`, `technique` | Function definition |
| `RETURN` | `return` | `yield`, `give`, `payload` | Return from function |
| `SUMMON` | `bind` | `summon`, `summon_planeteer`, `planet_power`, `captain_planet`, `ring_bind` | Content-addressable ring handler |
| `CALL_RING` | `dispatch` | `call`, `powers_combined`, `ring_call`, `invoke_ring`, `i_choose_you` | Ring dispatch call |
| `TRANSFORM` | `mpp` | `transform`, `moon_prism_power`, `differentiate`, `evolve`, `morph` | Cellular differentiation transform |
| `FALLBACK` | `fallback` | `tuxedo_mask`, `catch`, `default_handler`, `rose_throw` | Watchdog unrouted handler |
| `PRINT` | `print` | `emit`, `say`, `shout`, `kamehameha`, `hadouken`, `cowabunga_news` | Console output stream |
| `MUTATE` | `mutate` | `dee_dee_mutation`, `dee_dee_button`, `oops_mutation`, `radioactive_spider` | Fault-tolerance mutation block |
| `IMPORT` | `import` | `include`, `require`, `load_module`, `plasmid_inject`, `transfect` | Modular multi-file import |
| `PY_IMPORT` | `py_import` | `python_import`, `import_py`, `cyto_bridge`, `python` | Python ecosystem FFI import |
| `HEXAPHASE` | `hexaphase` | `hexa_phase`, `multiplex`, `polyphase`, `catdog`, `cat_dog` | 6-channel multi-frame execution |
| `SLIP` | `slip` | `frameshift`, `prf`, `ribo_slip`, `phase_shift` | Programmed ribosomal frameshift |
| `ATTENUATOR` | `attenuator` | `throttle`, `stem_loop`, `hairpin_gate`, `pause_gate` | Thermodynamic pause gate |
| `HALT` | `halt` | `exit`, `thats_all_folks`, `cowabunga`, `fin` | Clean execution termination |

---

## 2. Operator Precedence & Associativity

Expressions in SMC are evaluated according to standard Pratt parsing rules:

| Level | Operators | Description | Associativity |
| :---: | :--- | :--- | :---: |
| **7 (Highest)** | `()`, `[]`, `.` | Grouping, Indexing, Member Access | Left-to-right |
| **6** | `!`, `not`, `-` (unary) | Logical NOT, Arithmetic Negation | Right-to-left |
| **5** | `*`, `/`, `%` | Multiplication, Division, Modulo | Left-to-right |
| **4** | `+`, `-` | Addition, String Concatenation, Subtraction | Left-to-right |
| **3** | `<`, `<=`, `>`, `>=` | Relational Comparisons | Left-to-right |
| **2** | `==`, `!=` | Equality and Inequality | Left-to-right |
| **1** | `&&`, `and` | Short-circuiting Logical AND | Left-to-right |
| **0 (Lowest)** | `\|\|`, `or` | Short-circuiting Logical OR | Left-to-right |

---

## 3. Types, Data Structures & Semantics

### 3.1 Primitive Types
* **Number:** 64-bit IEEE 754 floating-point or integer.
* **String:** UTF-8 character sequences. Supports escape sequences (`\n`, `\t`, `\"`, `\'`, `\\`) and backtick template string interpolation (`` `Hello ${name}` ``).
* **Boolean:** `true` and `false`.
* **Null:** `null`.

### 3.2 Collection Types
* **List:** Ordered dynamic array `[1, "two", [3, 4]]`. Supports safe negative indexing (`arr[-1]`).
* **Dictionary:** Key-value hash map `{"name": "Blossom", "hp": 100}`.

### 3.3 Compound Assignment
Supports `+=`, `-=`, `*=`, `/=` for variables and indexed targets (`player["hp"] -= 10`, `scores[0] += 5`).

---

## 4. Execution Model & Scoping Rules

### 4.1 Variable Resolution & Scoping Hierarchy
1. **Local Stack Frame:** When executing inside a function `fn`, variables are resolved in the top call stack frame.
2. **Ephemeral TTL Memory:** If not found in local frame, checks active `ttl_memory` (if unexpired).
3. **Global Scope:** If not found, checks the global `variables` dictionary.
4. **Undefined Fallback:** Accessing an unassigned variable evaluates safely to `0` (or `null` in boolean context) without throwing a fatal crash.

### 4.2 Acme Anvil Ephemeral Memory (mRNA Half-Life Decay)
* Syntax: `acme(ttl=N) var_name = <expression>`
* **Lifecycle Rule:** Every execution step (`self.execution_steps += 1`, including statement execution or incoming HTTP requests) decrements all active TTL timers by $1$.
* When $\text{TTL} \le 0$, the variable vaporizes from memory, emitting an `[ACME_ANVIL_DROP]` event in stdout.

### 4.3 Content-Addressable Ring Dispatch (Captain Planet / Senshi)
* Functions bind to categorical string/ring keys:
  ```smc
  bind(ring="FIRE") {
      print "Fire attack triggered!"
  }
  ```
* Dispatch invokes all handlers registered to that ring: `dispatch "FIRE"`.
* **Watchdog Fallback:** If `dispatch` targets an unbound ring, the runtime invokes the `fallback { ... }` block (Tuxedo Mask Watchdog) if defined.

### 4.4 Cellular Differentiation (`mpp` / `transform`)
```smc
let guardian = "Usagi"
mpp guardian = "Princess_Serenity" {
    print "Transformed state active: " + guardian
}
# guardian reverts or retains post-transformation state
```

---

## 5. HexaPhase v0.7.0 Biological Primitives

### 5.1 HexaPhase Multiplexing Block
```smc
hexaphase "ABCDEF" {
    let p0 = hexaphase_channels["+0"] # "AD"
    let p1 = hexaphase_channels["+1"] # "BE"
    let p2 = hexaphase_channels["+2"] # "CF"
    let m0 = hexaphase_channels["-0"] # Reverse phase 0
}
```

### 5.2 Programmed Ribosomal Frameshifting (`slip`)
* `slip(offset)`: Adjusts the virtual machine's `current_phase_offset = (current_phase_offset + offset) % 3` and updates `current_phase`.

### 5.3 Attenuator Pause Gate (`attenuator`)
* `attenuator(threshold=X) { ... }`: Evaluates thermodynamic drag threshold and rate-limits nested statement execution.

---

## 6. Built-in Standard Library Function Reference

| Function | Signature | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `len` | `len(target: list\|str\|dict)` | `int` | Returns element count or string length |
| `push` | `push(list: list, item: any)` | `list` | Appends item to list |
| `pop` | `pop(list: list)` | `any` | Removes and returns last item |
| `str` | `str(val: any)` | `str` | Converts value to string representation |
| `int` | `int(val: any)` | `int` | Converts value to integer (safe fallback to `0`) |
| `type` | `type(val: any)` | `str` | Returns `"list"`, `"dict"`, `"bool"`, `"number"`, or `"str"` |
| `read_file` | `read_file(path: str)` | `str` | Reads UTF-8 file contents from disk |
| `write_file` | `write_file(path: str, data: str)` | `bool` | Writes UTF-8 data to disk |
| `serve_file` | `serve_file(path: str, mime: str)` | `dict` | Prepares HTTP response payload with file content |
| `to_json` | `to_json(val: any)` | `str` | Serializes data structure to formatted JSON string |
| `from_json` | `from_json(json_str: str)` | `any` | Parses JSON string into dictionary or list |
| `range` | `range(start, end, step)` | `list` | Generates integer sequence list |
| `split` | `split(str: str, sep: str)` | `list` | Splits string by delimiter |
| `join` | `join(list: list, sep: str)` | `str` | Joins list elements with separator |
| `keys` | `keys(dict: dict)` | `list` | Returns list of dictionary keys |
| `values` | `values(dict: dict)` | `list` | Returns list of dictionary values |
| `contains` | `contains(container, item)` | `bool` | Tests membership in list, string, or dictionary |
| `hexaphase_compile` | `hexaphase_compile(s1, s2)` | `str` | Interleaves two strings into multiplexed locus |
| `hexaphase_channels` | `hexaphase_channels(s: str)` | `dict` | Decomposes stream into 6 channels (`+0..-2`) |
| `phase_slip` | `phase_slip(s: str, offset: int)` | `str` | Phase-shifts string by index offset |
| `py_call` | `py_call(func_str, *args)` | `any` | Invokes Python standard library or imported module |
| `py_eval` | `py_eval(expr_str: str)` | `any` | Evaluates Python expression in sandboxed scope |
| `py_import` | `py_import(mod_name, alias)` | `bool` | Bridges Python module into SMC runtime |
| `serve_http` | `serve_http(port, handler_fn)` | `bool` | Starts embedded multi-threaded HTTP web server |

---

## 7. Edge Case & Fault-Tolerance Policy

| Condition | DexterVM Runtime Behavior |
| :--- | :--- |
| **Division by Zero (`x / 0`)** | Emits `[ZERO_DIV_GUARD]`, returns `0`, execution continues safely. |
| **Missing List Index (`arr[99]`)** | Returns `0` (or `null`), never raises `IndexError`. |
| **Negative List Index (`arr[-1]`)** | Wraps around safely to end of collection (`arr[len + index]`). |
| **Missing Dict Key (`dict["missing"]`)** | Returns `0`, never raises `KeyError`. |
| **Infinite Recursion** | Capped at depth 100; emits `[RECURSION_GUARD]` and returns gracefully. |
| **Syntax Typo (`prnt "Hi"`)** | Automatically corrected via Levenshtein Wobble matching. |
| **Cyclic Module Imports** | Detected and skipped to prevent infinite import loops. |
| **Bit-Flip Mutations (`mutate`)** | Stochastic token mutator runs safely inside supervised sandbox. |
