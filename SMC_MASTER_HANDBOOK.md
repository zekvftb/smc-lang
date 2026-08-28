# 📐 SMC Language Formal Specification & Runtime Reference
**Specification Version:** 0.7.0  
**Target Runtime:** DexterVM Execution Engine  
**Author:** Jason Rezek (`zekvftb@gmail.com`)  
**Repository:** `https://github.com/zekvftb/smc-lang`  

---

## 1. Language Overview & Execution Model

SMC is a dynamically typed, procedural, and fault-tolerant interpreted programming language. Source files (`.smc`) are parsed into an Abstract Syntax Tree (AST) via a recursive-descent Pratt parser and executed on the `DexterVM` virtual machine.

### 1.1 Core Design Axioms
1. **Deterministic Resilience:** No standard operational error (division by zero, missing dictionary key, out-of-bounds array index, or syntax typo) causes an unhandled process termination or crash cascade.
2. **Unified Core Language:** All features—including HexaPhase multiplexing, Acme TTL memory, template strings, and the Python FFI bridge—are part of the core language runtime and require no external plugins.
3. **Synchronous Execution:** All statements, function calls, built-ins, and FFI bridges execute synchronously in execution step units (`execution_steps`).

---

## 2. Formal Lexical Grammar & Token Resolution

### 2.1 Keyword & Opcode Degeneracy
SMC maps multiple synonym tokens to canonical opcodes. Case-insensitive matching is applied to all keywords.

| Opcode | Canonical Keyword | Synonym Token Set | Syntax Form |
| :--- | :--- | :--- | :--- |
| `EXPERIMENT` | `experiment` | `program`, `module`, `secret_lab`, `dexter_lab_experiment`, `omnitrix_init` | `experiment "Name"` |
| `SET_VAR` | `let` | `set`, `var`, `sugar`, `spice`, `everything_nice`, `chemical_x` | `let ident = expr` |
| `TTL_BOX` | `acme` | `acme_anvil_box`, `acme_box`, `ephemeral`, `anvil_box`, `disposable_var` | `acme(ttl=int) ident = expr` |
| `IF` | `if` | `when`, `check_gate`, `test` | `if (expr) { stmts }` |
| `ELSE` | `else` | `otherwise`, `default` | `else { stmts }` |
| `WHILE` | `while` | `loop`, `cycle`, `road_runner_loop` | `while (expr) { stmts }` |
| `FOR` | `for` | `each`, `for_each`, `iterate` | `for item in container { stmts }` |
| `FN` | `fn` | `function`, `def`, `subroutine`, `recipe`, `technique` | `fn name(p1, p2) { stmts }` |
| `RETURN` | `return` | `yield`, `give`, `payload` | `return expr` |
| `SUMMON` | `bind` | `summon`, `summon_planeteer`, `planet_power`, `captain_planet`, `ring_bind` | `bind(ring="KEY") { stmts }` |
| `CALL_RING` | `dispatch` | `call`, `powers_combined`, `ring_call`, `invoke_ring`, `i_choose_you` | `dispatch "KEY"` |
| `TRANSFORM` | `mpp` | `transform`, `moon_prism_power`, `differentiate`, `evolve`, `morph` | `mpp ident = expr { stmts }` |
| `FALLBACK` | `fallback` | `tuxedo_mask`, `catch`, `default_handler`, `rose_throw` | `fallback { stmts }` |
| `PRINT` | `print` | `emit`, `say`, `shout`, `kamehameha`, `hadouken`, `cowabunga_news` | `print expr` |
| `MUTATE` | `mutate` | `dee_dee_mutation`, `dee_dee_button`, `oops_mutation`, `radioactive_spider` | `mutate { stmts }` |
| `IMPORT` | `import` | `include`, `require`, `load_module`, `plasmid_inject`, `transfect` | `import "path.smc"` |
| `PY_IMPORT` | `py_import` | `python_import`, `import_py`, `cyto_bridge`, `python` | `py_import "mod" as alias` |
| `HEXAPHASE` | `hexaphase` | `hexa_phase`, `multiplex`, `polyphase`, `catdog`, `cat_dog` | `hexaphase expr { stmts }` |
| `SLIP` | `slip` | `frameshift`, `prf`, `ribo_slip`, `phase_shift` | `slip(int_expr)` |
| `ATTENUATOR` | `attenuator` | `throttle`, `stem_loop`, `hairpin_gate`, `pause_gate` | `attenuator(threshold=expr) { stmts }` |
| `HALT` | `halt` | `exit`, `thats_all_folks`, `cowabunga`, `fin` | `halt` |

### 2.2 Wobble Typo-Tolerance Algorithm
Identifiers not found in keyword tables are evaluated via bounded Levenshtein distance $D(s, k)$:
1. Identifiers matching registered built-in functions (`len`, `push`, `pop`, `str`, `int`, etc.) or single-character symbols are **never** mutated.
2. For candidate keyword $k$ and input token $s$:
   $$D_{max} = \begin{cases} 1 & \text{if } |s| \le 4 \\ 1 & \text{if } 5 \le |s| \le 6 \\ 2 & \text{if } |s| \ge 7 \end{cases}$$
3. If $D(s, k) \le D_{max}$, $s$ is rewritten to $k$.

---

## 3. Explicit Operator Precedence & Associativity Matrix

SMC enforces a strict 8-level Pratt parsing hierarchy. Binary operators are evaluated strictly left-to-right; unary operators are evaluated right-to-left.

| Level | Operator | Operation | Associativity | Example Evaluation |
| :---: | :--- | :--- | :---: | :--- |
| **7 (Highest)** | `()` | Grouping / Function Call | Left-to-right | `fn(x)` |
| | `[]` | Index Access / Subscription | Left-to-right | `arr[0]`, `dict["key"]` |
| | `.` | Member Access | Left-to-right | `obj.member` |
| **6** | `!`, `not` | Logical Negation | Right-to-left | `!is_valid` |
| | `-` (unary) | Arithmetic Negation | Right-to-left | `-5` |
| **5** | `*` | Multiplication | Left-to-right | `a * b` |
| | `/` | Division (Zero-guarded) | Left-to-right | `a / b` |
| | `%` | Modulo | Left-to-right | `a % b` |
| **4** | `+` | Addition, String/List Concatenation | Left-to-right | `a + b` |
| | `-` | Subtraction | Left-to-right | `a - b` |
| **3** | `<` | Less Than | Left-to-right | `ball_y + 1 < y` $\rightarrow$ `(ball_y + 1) < y` |
| | `<=` | Less Than or Equal | Left-to-right | `a <= b` |
| | `>` | Greater Than | Left-to-right | `a > b` |
| | `>=` | Greater Than or Equal | Left-to-right | `a >= b` |
| **2** | `==` | Equality | Left-to-right | `x == 0` |
| | `!=` | Inequality | Left-to-right | `x != 10` |
| **1** | `&&`, `and` | Short-circuiting Logical AND | Left-to-right | `a > 0 && b < 10` |
| **0 (Lowest)** | `\|\|`, `or` | Short-circuiting Logical OR | Left-to-right | `x == 0 \|\| x == width - 1` |

### 3.1 Precedence Examples
* `ball_y + 1 < y`:
  Evaluates as `(ball_y + 1) < y` because Additive (`+`, Level 4) precedes Relational (`<`, Level 3).
* `x == 0 || x == width - 1`:
  Evaluates as `(x == 0) || (x == (width - 1))` because Additive (`-`, Level 4) > Equality (`==`, Level 2) > Logical OR (`||`, Level 0).

---

## 4. Types, Literals & String Interpolation

### 4.1 Primitive Types
* **Number (`int`, `float`):** 64-bit IEEE 754 floating point or integer.
* **Boolean (`bool`):** `true`, `false`.
* **Null (`null`):** Represents absence of value.
* **String (`str`):** UTF-8 encoded text.
  * Single/Double quoted: `'text'`, `"text"` (supports `\n`, `\t`, `\"`, `\'`, `\\`).
  * **Template Strings (Backticks):** `` `Hello ${name}, score: ${points * 2}` ``.
    * Supports multiline literals.
    * Expression blocks `${expr}` are evaluated in current scope and string-coerced.
    * Escaping: `\${` evaluates to literal `${`.

### 4.2 Composite Collection Types
* **List (`list`):** Dynamic ordered array: `[1, "two", [3, 4]]`.
* **Dictionary (`dict`):** Key-value map: `{"name": "Blossom", "hp": 100}`.

---

## 5. Scope, Mutability & Variable Lifecycle Semantics

### 5.1 Pass-by-Value vs. Pass-by-Reference
* **Primitives (`number`, `string`, `bool`, `null`):** Immutable. Passed by value.
* **Collections (`list`, `dict`):** Mutable reference objects. Passed by reference. Modifying collection elements inside a function (`target["hp"] -= dmg`, `push(arr, item)`) mutates the original object in place.

### 5.2 Scoping & Mutation Rules
1. **Declaration (`let x = val`):** Always creates or assigns to the innermost active scope (the local stack frame if inside a function, otherwise the global variable table).
2. **Indexed Assignment (`target[key] = val` / `target[key] -= val`):** Resolves `target` via lexical lookup and mutates the referenced collection object in place.
3. **Compound Assignment (`x += 1`):**
   * If `x` exists in current local call frame: mutates local `x`.
   * Else if `x` exists in global variables: mutates outer global `x`.
   * Else: creates and initializes `x` in current local scope.
4. **Undefined Variables:** Reading an unassigned variable returns `0` (or `null` in boolean context) without throwing fatal runtime exceptions.

### 5.3 Acme Anvil Ephemeral Memory (TTL Decay Rules)
* **Declaration:** `acme(ttl=N) name = value`
* **Allocation:** Stored in global table `ttl_memory[name] = TtlItem(value, ttl=N)`.
* **Decay Rule:** Every statement execution and every incoming HTTP request decrements all active TTL values by $1$.
* **Expiration:** When $\text{TTL} \le 0$, the entry is immediately deleted from memory.
* **Function Scoping:** TTL variables are globally accessible unless shadowed by a local variable of the same name. Expiration of a TTL variable inside a function immediately removes it from the global lookup fallback.

---

## 6. Built-ins vs. Keywords Formal Specification

All SMC operations are divided into **Keywords (Syntax Nodes)** and **Built-in Functions (Standard Library)**. All built-ins execute synchronously and return typed values.

### 6.1 Statement Keywords (Control & Primitives)

#### `hexaphase <expr> { ... }`
* **Type:** Statement Block Keyword.
* **Semantics:** Slices string `<expr>` of length $N$ into 6 channels stored in local/global variable `hexaphase_channels`:
  * `"+0"`: Indices $0, 3, 6, \dots$
  * `"+1"`: Indices $1, 4, 7, \dots$
  * `"+2"`: Indices $2, 5, 8, \dots$
  * `"-0"`: Reverse indices $0, 3, 6, \dots$
  * `"-1"`: Reverse indices $1, 4, 7, \dots$
  * `"-2"`: Reverse indices $2, 5, 8, \dots$

#### `slip(<offset_expr>)`
* **Type:** Statement Keyword.
* **Semantics:** Shifts VM execution phase: `current_phase = (current_phase + offset) % 3`.

#### `attenuator(threshold = <expr>) { ... }`
* **Type:** Statement Block Keyword.
* **Semantics:** Evaluates numeric threshold and executes nested block within a rate-limiting barrier.

---

### 6.2 Standard Built-in Functions

| Function | Signature | Return Type | Semantics & Invalid Argument Behavior |
| :--- | :--- | :--- | :--- |
| `len` | `len(target)` | `int` | Returns element count or string length. Returns `0` if target is non-collection. |
| `push` | `push(list, item)` | `list` | Appends `item` in place and returns list. Returns `[]` if target is non-list. |
| `pop` | `pop(list)` | `any` | Removes and returns last item. Returns `0` if list is empty. |
| `str` | `str(val)` | `str` | Converts value to string representation. |
| `int` | `int(val)` | `int` | Parses integer. Returns `0` on parse failure or invalid type. |
| `type` | `type(val)` | `str` | Returns `"list"`, `"dict"`, `"bool"`, `"number"`, `"str"`, or `"null"`. |
| `read_file` | `read_file(path: str)` | `str` | Reads UTF-8 file contents from disk. Returns `""` on file not found. |
| `write_file` | `write_file(path: str, data: str)` | `bool` | Writes UTF-8 text to disk. Returns `true` on success, `false` on failure. |
| `serve_file` | `serve_file(path: str, mime: str)` | `dict` | Prepares HTTP response dictionary `{"status": 200, "content_type": mime, "body": data}`. |
| `to_json` | `to_json(val)` | `str` | Serializes value to JSON string. Returns `"{}"` on failure. |
| `from_json` | `from_json(json_str: str)` | `any` | Parses JSON string into dictionary or list. Returns `{}` on failure. |
| `range` | `range(start, end[, step])` | `list` | Generates list of integers. Returns `[]` on invalid arguments. |
| `split` | `split(str, sep)` | `list` | Splits string by delimiter substring. |
| `join` | `join(list, sep)` | `str` | Joins list elements with delimiter string. |
| `keys` | `keys(dict)` | `list` | Returns list of dictionary keys. |
| `values` | `values(dict)` | `list` | Returns list of dictionary values. |
| `contains` | `contains(container, item)` | `bool` | Returns `true` if item is found in list, string, or dict keys. |
| `hexaphase_compile` | `hexaphase_compile(s1: str, s2: str)` | `str` | Interleaves two strings into multiplexed string. Returns `""` if missing args. |
| `hexaphase_channels`| `hexaphase_channels(s: str)` | `dict` | Decompiles string into 6-channel dictionary (`+0, +1, +2, -0, -1, -2`). |
| `phase_slip` | `phase_slip(s: str, offset: int)` | `str` | Rotates string by index offset (`s[offset:] + s[:offset]`). |
| `py_call` | `py_call(callable_str, *args)` | `any` | Invokes Python standard library function. Returns `None` on failure. |
| `py_eval` | `py_eval(expr_str: str)` | `any` | Evaluates Python expression string in sandboxed scope. |
| `py_import` | `py_import(mod_name, alias)` | `bool` | Bridges Python module into `py_modules`. Returns `true` on success. |
| `serve_http` | `serve_http(port: int, handler_fn: str)` | `bool` | Starts embedded multi-threaded HTTP server. Dispatches requests to `handler_fn(req)`. |

---

## 7. Runtime Error Handling & Fault-Tolerance Policy

| Fault Condition | Exact Runtime Behavior |
| :--- | :--- |
| **Division by Zero (`x / 0`)** | Emits `[ZERO_DIV_GUARD]` log; returns `0`. Never halts process. |
| **Missing List Index (`arr[99]`)** | Returns `0` (or `null`). Never raises `IndexError`. |
| **Negative List Index (`arr[-1]`)** | Wraps safely to end of list (`arr[len + index]`). |
| **Missing Dict Key (`dict["missing"]`)** | Returns `0`. Never raises `KeyError`. |
| **Infinite Recursion** | Hard limit of 100 nested stack frames. Emits `[STACK_OVERFLOW]` and unwinds cleanly. |
| **Unbound Ring Dispatch** | Executes `fallback { ... }` block if registered; otherwise passes cleanly. |
| **Cyclic Module Imports** | Detected and skipped via `imported_modules` tracking set. |
