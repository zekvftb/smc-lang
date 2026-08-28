# 📐 SMC (Saturday Morning Cartoons) Formal Language Specification
**Specification Standard:** ISO/EBNF-Aligned Formal Language Reference  
**Version:** 0.7.0 (The HexaPhase Edition)  
**Target Runtime Engine:** DexterVM Dynamic Execution Environment  
**Maintainer:** Jason Rezek (`zekvftb@gmail.com`)  
**Repository:** `https://github.com/zekvftb/smc-lang`  

---

## 1. Formal Grammar Specification (EBNF)

### 1.1 Lexical Grammar
```ebnf
letter          = "A" | ... | "Z" | "a" | ... | "z" | "_" ;
digit           = "0" | ... | "9" ;
identifier      = letter , { letter | digit } ;

integer_lit     = digit , { digit } ;
float_lit       = digit , { digit } , "." , digit , { digit } ;
number_lit      = integer_lit | float_lit ;

escape_seq      = "\" , ( "n" | "t" | "r" | "\" | "'" | '"' | "$" | "`" ) ;
char_single     = escape_seq | ? any character except "'" or "\" ? ;
char_double     = escape_seq | ? any character except '"' or "\" ? ;
string_lit      = ( "'" , { char_single } , "'" ) 
                | ( '"' , { char_double } , '"' ) ;

interp_expr     = "${" , expression , "}" ;
template_char   = escape_seq | interp_expr | ? any character except "`" or "\" or "$" ? ;
template_lit    = "`" , { template_char } , "`" ;

boolean_lit     = "true" | "false" ;
null_lit        = "null" ;
literal         = number_lit | string_lit | template_lit | boolean_lit | null_lit ;
```

### 1.2 Expression Grammar (Pratt Precedence Hierarchy)
```ebnf
primary_expr    = literal
                | identifier
                | list_literal
                | dict_literal
                | "(" , expression , ")"
                | function_call ;

list_literal    = "[" , [ expression , { "," , expression } ] , "]" ;
dict_pair       = ( string_lit | identifier ) , ":" , expression ;
dict_literal    = "{" , [ dict_pair , { "," , dict_pair } ] , "}" ;
function_call   = identifier , "(" , [ expression , { "," , expression } ] , ")" ;

postfix_expr    = primary_expr , { "[" , expression , "]" } ;
unary_expr      = [ "!" | "not" | "-" ] , postfix_expr ;
mult_expr       = unary_expr , { ( "*" | "/" | "%" ) , unary_expr } ;
add_expr        = mult_expr , { ( "+" | "-" ) , mult_expr } ;
rel_expr        = add_expr , { ( "<" | "<=" | ">" | ">=" ) , add_expr } ;
eq_expr         = rel_expr , { ( "==" | "!=" ) , rel_expr } ;
and_expr        = eq_expr , { ( "&&" | "and" ) , eq_expr } ;
or_expr         = and_expr , { ( "||" | "or" ) , and_expr } ;
expression      = or_expr ;
```

### 1.3 Statement Grammar
```ebnf
program         = { statement } ;
block           = "{" , { statement } , "}" ;

statement       = experiment_decl
                | set_var_stmt
                | compound_assign
                | index_assign
                | acme_ttl_stmt
                | if_stmt
                | while_stmt
                | for_in_stmt
                | fn_decl
                | return_stmt
                | bind_stmt
                | dispatch_stmt
                | mpp_transform_stmt
                | fallback_stmt
                | print_stmt
                | mutate_stmt
                | import_stmt
                | py_import_stmt
                | hexaphase_stmt
                | slip_stmt
                | attenuator_stmt
                | halt_stmt
                | expr_stmt ;

experiment_decl = "experiment" , string_lit ;
set_var_stmt    = ( "let" | "set" | "var" ) , identifier , "=" , expression ;
compound_assign = identifier , ( "+=" | "-=" | "*=" | "/=" ) , expression ;
index_assign    = identifier , "[" , expression , "]" , ( "=" | "+=" | "-=" | "*=" | "/=" ) , expression ;
acme_ttl_stmt   = "acme" , "(" , "ttl" , "=" , integer_lit , ")" , identifier , "=" , expression ;

if_stmt         = "if" , "(" , expression , ")" , block , [ "else" , block ] ;
while_stmt      = "while" , "(" , expression , ")" , block ;
for_in_stmt     = "for" , identifier , "in" , expression , block ;

fn_decl         = "fn" , identifier , "(" , [ identifier , { "," , identifier } ] , ")" , block ;
return_stmt     = "return" , [ expression ] ;

bind_stmt       = "bind" , "(" , "ring" , "=" , expression , ")" , block ;
dispatch_stmt   = "dispatch" , expression ;
mpp_transform_stmt = "mpp" , identifier , "=" , expression , block ;
fallback_stmt   = "fallback" , block ;

print_stmt      = "print" , expression ;
mutate_stmt     = "mutate" , block ;
import_stmt     = "import" , string_lit ;
py_import_stmt  = "py_import" , string_lit , [ "as" , identifier ] ;

hexaphase_stmt  = "hexaphase" , expression , block ;
slip_stmt       = "slip" , "(" , expression , ")" ;
attenuator_stmt = "attenuator" , "(" , "threshold" , "=" , expression , ")" , block ;
halt_stmt       = "halt" ;
expr_stmt       = expression ;
```

---

## 2. Abstract Runtime Semantics & Environment

### 2.1 State Space & Storage Model
An executing SMC environment consists of five distinct storage segments:
1. **Activation Call Stack ($\mathcal{S}$):** A sequence of local frames $[\sigma_0, \sigma_1, \dots, \sigma_k]$, where $\sigma_k$ maps identifiers to value bindings.
2. **Ephemeral Environment ($\mathcal{E}_{TTL}$):** A map from identifiers to pairs $(v, \tau)$, where $v$ is the bound value and $\tau \in \mathbb{Z}^+$ is the remaining time-to-live.
3. **Global Environment ($\mathcal{G}$):** A persistent map from identifiers to global value bindings.
4. **Content-Addressable Ring Registry ($\mathcal{R}$):** A map from categorical string keys to lists of executable statement blocks.
5. **Execution Clock ($\tau_{clk}$):** A monotonically increasing discrete counter incremented on every evaluation step and incoming request.

### 2.2 Variable Resolution Hierarchy
Lookup for identifier $x$ is defined formally as:
$$\text{resolve}(x) = \begin{cases} 
\sigma_{top}(x) & \text{if } x \in \text{dom}(\sigma_{top}) \\
v & \text{if } x \notin \text{dom}(\sigma_{top}) \land (x \mapsto (v, \tau)) \in \mathcal{E}_{TTL} \land \tau > 0 \\
\mathcal{G}(x) & \text{if } x \notin \text{dom}(\sigma_{top}) \land x \notin \text{dom}(\mathcal{E}_{TTL}) \land x \in \text{dom}(\mathcal{G}) \\
0 & \text{otherwise (safe default fallback)}
\end{cases}$$

### 2.3 Undefined Read Semantics
* **Deterministic Default:** Reading an uninitialized identifier evaluates to `0` in numeric context, `""` in string concatenation, and `null` / `false` in logical tests.
* **Non-Halting Guarantee:** Uninitialized variable reads emit an internal runtime step log but **never** raise fatal exceptions or abort the process.

---

## 3. Type System & Value Coercion Specification

| Type | Representation | Mutability | Truthiness Rule | Coercion with String (`+`) | Equality Semantics (`==`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`number`** | 64-bit IEEE 754 float / int | Immutable (Value) | $x \neq 0$ | Formatted string (e.g. `"42"`) | Numeric value equality |
| **`string`** | UTF-8 character string | Immutable (Value) | $\text{len}(s) > 0$ | Self | Byte-level string equality |
| **`bool`** | `true`, `false` | Immutable (Value) | Direct identity | `"true"` / `"false"` | Boolean identity |
| **`null`** | Absence of value | Immutable (Value) | **Always `false`** | **Coerces to `"null"`** | **`null == null` is `true`** |
| **`list`** | Ordered dynamic array | **Mutable (Ref)** | $\text{len}(L) > 0$ | Formatted JSON-like string | Reference / structural equality |
| **`dict`** | Associative hash map | **Mutable (Ref)** | $\text{len}(D) > 0$ | Formatted JSON-like string | Reference / structural equality |

### 3.1 `null` Coercion & Membership Semantics
* **String Concatenation:** `"Status: " + null` $\rightarrow$ `"Status: null"`.
* **Logical Condition:** `if (null) { ... }` $\rightarrow$ Condition evaluates to `false`.
* **Collection Membership:** `contains([1, null, 3], null)` $\rightarrow$ Evaluates to `true`.
* **Type Identification:** `type(null)` $\rightarrow$ Returns string `"null"`.

---

## 4. Subsystem & Keyword Semantics

### 4.1 Ephemeral Memory Decay (`acme`)
* **Syntax:** `acme(ttl = k) ident = expr`
* **Allocation:** Inserts $(ident \mapsto (\text{eval}(expr), k))$ into $\mathcal{E}_{TTL}$.
* **Decay Lifecycle:** At each execution step ($\tau_{clk} \leftarrow \tau_{clk} + 1$), for all $(x \mapsto (v, \tau)) \in \mathcal{E}_{TTL}$:
  $$\tau \leftarrow \tau - 1$$
  $$\text{if } \tau \le 0 \implies \mathcal{E}_{TTL} \leftarrow \mathcal{E}_{TTL} \setminus \{x\}$$

### 4.2 Stochastic Fault-Injection (`mutate`)
* **Syntax:** `mutate { stmts }`
* **Semantics:** Executes nested statements within a supervised fault-injection sandbox. At each step within the block, the runtime introduces a stochastic perturbation (simulated bit-flip, random operator substitution, or argument jitter) governed by the active mutation rate. The runtime's codon wobble engine and watchdog layers dynamically absorb these errors, and execution steps survived are tracked in telemetry.

### 4.3 HexaPhase 6-Channel Multiplexing (`hexaphase`)
* **Syntax:** `hexaphase expr { stmts }`
* **Semantics:** Evaluates `expr` as string $S$ of length $N$. Binds variable `hexaphase_channels` to dictionary:
  $$\begin{aligned}
  \text{"+0"} &= \left( S_i \mid i \equiv 0 \pmod 3 \right), & \text{"-0"} &= \left( \text{rev}(S)_i \mid i \equiv 0 \pmod 3 \right) \\
  \text{"+1"} &= \left( S_i \mid i \equiv 1 \pmod 3 \right), & \text{"-1"} &= \left( \text{rev}(S)_i \mid i \equiv 1 \pmod 3 \right) \\
  \text{"+2"} &= \left( S_i \mid i \equiv 2 \pmod 3 \right), & \text{"-2"} &= \left( \text{rev}(S)_i \mid i \equiv 2 \pmod 3 \right)
  \end{aligned}$$

### 4.4 Programmed Ribosomal Frameshifting (`slip`)
* **Syntax:** `slip(offset)`
* **Semantics:** Computes phase transition: $\text{phase} \leftarrow (\text{phase} + \text{int}(\text{eval}(offset))) \pmod 3$. Updates global binding `current_phase`.

### 4.5 Attenuator Pause Gate (`attenuator`)
* **Syntax:** `attenuator(threshold = expr) { stmts }`
* **Semantics:** Evaluates numeric resistance barrier and throttles throughput of statements within the block.

---

## 5. Python FFI & Security Sandbox Specification

### 5.1 FFI Operations
* `py_import(mod_name, alias)`: Loads host Python module into active runtime bridge.
* `py_call(target_str, *args)`: Dynamically resolves callable (e.g. `"math.sqrt"`, `"random.randint"`, `"secrets.token_hex"`), marshals arguments from SMC types to CPython types, invokes callable synchronously, and marshals return values back to SMC types.
* `py_eval(expr_str)`: Evaluates Python expressions synchronously within a whitelisted sandbox.

### 5.2 Sandbox Scope & Security Boundaries
`py_eval` executes with standard builtins restricted and an explicit module scope containing:
$$\mathcal{S}_{sandbox} = \{ \text{math}, \text{random}, \text{datetime}, \text{json}, \text{time}, \text{os}, \text{sys} \} \cup \mathcal{M}_{imported} \cup \mathcal{G}$$
* **Network & Disk Access:** Modules requiring host system I/O inherit standard user-level permissions of the host process.
* **Marshalling Safety:** Circular Python references are intercepted and serialized safely without stack recursion errors.

---

## 6. HTTP Web Server Subsystem (`serve_http`)

### 6.1 Server Invocation & Lifecycle
* **Syntax:** `serve_http(port: int, handler_fn: str)`
* **Protocol:** Multi-threaded HTTP/1.1 daemon listening on `0.0.0.0:port`.
* **Execution:** Synchronously receives HTTP requests, increments `execution_steps`, ticks active TTL memory, and invokes `handler_fn(req)`.

### 6.2 Request Object Schema (`req: dict`)
The runtime passes a structured dictionary to `handler_fn`:
```json
{
  "path": "/api/resource",
  "method": "GET",
  "headers": {
    "host": "localhost:3000",
    "user-agent": "Mozilla/5.0 ...",
    "content-type": "application/json"
  },
  "body": "{\"param\": 123}"
}
```

### 6.3 Response Object Schema & Fallbacks
The handler must return a response structure:
* **Dictionary Response:**
  ```json
  {
    "status": 200,
    "content_type": "text/html; charset=utf-8",
    "body": "<h1>Response Payload</h1>"
  }
  ```
* **String Response:** If `handler_fn` returns a raw string, the server automatically wraps it as `HTTP 200 OK` with `Content-Type: text/html; charset=utf-8`.
* **Malformed Output Fallback:** If `handler_fn` returns an invalid type, the server safely coerces it via `str()` with `HTTP 200 OK`.

---

## 7. Standard Built-in Function Reference

| Function | Signature | Return Type | Semantics & Error Fallback |
| :--- | :--- | :--- | :--- |
| `len` | `len(target)` | `int` | Element count or string length. Returns `0` if non-collection. |
| `push` | `push(list, item)` | `list` | Appends `item` in place; returns list. Returns `[]` if target is non-list. |
| `pop` | `pop(list)` | `any` | Removes and returns last element. Returns `0` if list is empty. |
| `str` | `str(val)` | `str` | Converts value to string representation. |
| `int` | `int(val)` | `int` | Parses integer. Returns `0` on parse failure. |
| `type` | `type(val)` | `str` | Returns `"list"`, `"dict"`, `"bool"`, `"number"`, `"str"`, or `"null"`. |
| `read_file` | `read_file(path: str)` | `str` | Reads UTF-8 file. Returns `""` on I/O failure. |
| `write_file` | `write_file(path: str, data: str)` | `bool` | Writes UTF-8 text to disk. Returns `true` on success, `false` on failure. |
| `serve_file` | `serve_file(path: str, mime: str)` | `dict` | Returns HTTP response structure `{"status": 200, "content_type": mime, "body": content}`. |
| `to_json` | `to_json(val)` | `str` | Formats data as JSON string. Returns `"{}"` on failure. |
| `from_json` | `from_json(str)` | `any` | Parses JSON string into dictionary/list. Returns `{}` on failure. |
| `range` | `range(start, end[, step])` | `list` | Generates list of integers. Returns `[]` on invalid arguments. |
| `split` | `split(str, sep)` | `list` | Splits string by delimiter substring. |
| `join` | `join(list, sep)` | `str` | Joins list elements with separator string. |
| `keys` | `keys(dict)` | `list` | Returns list of dictionary keys. |
| `values` | `values(dict)` | `list` | Returns list of dictionary values. |
| `contains` | `contains(container, item)` | `bool` | Returns `true` if item is found in list, string, or dict keys. |
| `hexaphase_compile`| `hexaphase_compile(s1, s2)`| `str` | Interleaves two strings into multiplexed string. Returns `""` on missing args. |
| `hexaphase_channels`| `hexaphase_channels(s)`| `dict` | Slices string into 6-channel dictionary (`+0..-2`). |
| `phase_slip` | `phase_slip(s, offset)` | `str` | Rotates string by index offset. |
