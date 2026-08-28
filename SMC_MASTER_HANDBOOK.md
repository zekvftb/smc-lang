# 📐 SMC (Saturday Morning Cartoons) Formal Language Specification
**Specification Standard:** ISO/EBNF-Aligned Formal Language Reference  
**Version:** 0.7.0 (The HexaPhase Edition)  
**Target Runtime Engine:** DexterVM Dynamic Execution Environment  
**Maintainer:** Jason Rezek (`zekvftb@gmail.com`)  
**Repository:** `https://github.com/zekvftb/smc-lang`  

---

## 1. Formal Grammar Specification (EBNF)

### 1.1 Lexical Grammar
````ebnf
whitespace      = " " | "\t" | "\r" | "\n" ;
comment         = "#" , { ? any character except newline ? } , ( "\n" | ? EOF ? ) ;
letter          = "A" | ... | "Z" | "a" | ... | "z" ;
digit           = "0" | ... | "9" ;
ident_start     = letter | "_" ;
ident_char      = letter | digit | "_" ;
identifier      = ident_start , { ident_char } ;

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
reserved_token  = "." | ";" | "@" | "~" ;
````

### 1.2 Lexical & Case-Sensitivity Rules
1. **Keyword Case-Insensitivity:** All canonical keywords and cartoon synonym tokens are matched case-insensitively (`LET`, `let`, `Let`, `SUGAR`, `sugar`).
2. **Identifier Case-Sensitivity:** User-defined identifiers (variable names, function names, dictionary keys) are strictly **case-sensitive** (`blossom` $\neq$ `Blossom`).
3. **Lexical Built-in Shadowing Scope:** User-defined variables and function declarations within an active scope shadow standard built-in functions of the same name (e.g. declaring `let len = 5` shadows built-in `len()`). Shadowing applies recursively to all child and nested scopes within the declaring frame, and the original built-in binding is automatically restored upon frame termination.
4. **Reserved Symbols:** The dot (`.`), semicolon (`;`), at-sign (`@`), and tilde (`~`) tokens are reserved for future namespace and macro extensions. Subscript indexing `dict["key"]` is the canonical member access operator.
5. **Whitespace & Comment Invariance:** Whitespace characters (`\x20`, `\t`, `\r`, `\n`) and comments (`#` to newline/EOF) are ignored and discarded by the lexer as delimiters, generating zero runtime tokens.

### 1.3 Expression Grammar (Uniform Postfix Pratt Hierarchy)
```ebnf
primary_expr    = literal
                | identifier
                | list_literal
                | dict_literal
                | "(" , expression , ")" ;

list_literal    = "[" , [ expression , { "," , expression } ] , "]" ;
dict_pair       = ( string_lit | identifier ) , ":" , expression ;
dict_literal    = "{" , [ dict_pair , { "," , dict_pair } ] , "}" ;

call_suffix     = "(" , [ expression , { "," , expression } ] , ")" ;
index_suffix    = "[" , expression , "]" ;
postfix_expr    = primary_expr , { call_suffix | index_suffix } ;

unary_expr      = [ "!" | "not" | "-" ] , postfix_expr ;
mult_expr       = unary_expr , { ( "*" | "/" | "%" ) , unary_expr } ;
add_expr        = mult_expr , { ( "+" | "-" ) , mult_expr } ;
rel_expr        = add_expr , { ( "<" | "<=" | ">" | ">=" ) , add_expr } ;
eq_expr         = rel_expr , { ( "==" | "!=" ) , rel_expr } ;
and_expr        = eq_expr , { ( "&&" | "and" ) , eq_expr } ;
or_expr         = and_expr , { ( "||" | "or" ) , and_expr } ;
expression      = or_expr ;
```

### 1.4 Statement Grammar
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

## 2. Abstract Runtime Semantics & State Model

### 2.1 State Space & Storage Model
An executing SMC environment consists of six distinct state components:
1. **Activation Call Stack ($\mathcal{S}$):** A stack of local activation frames $[\sigma_0, \sigma_1, \dots, \sigma_k]$, where $\sigma_k: \text{Identifier} \to \text{Value}$. Function scopes are isolated (no implicit outer local closure capture).
2. **Ephemeral Environment ($\mathcal{E}_{TTL}$):** A map $\text{Identifier} \to (\text{Value}, \tau)$, where $\tau \in \mathbb{Z}^+$ is the discrete step time-to-live.
3. **Global Environment ($\mathcal{G}$):** A persistent global symbol map $\text{Identifier} \to \text{Value}$.
4. **Content-Addressable Ring Registry ($\mathcal{R}$):** A map from categorical string keys to lists of executable statement sequences.
5. **Execution Phase State ($\Phi_{phase}$):** Current reading phase register $\Phi_{phase} \in \{0, 1, 2\}$, initialized to $0$ and modulated via `slip()`.
6. **Execution Clock ($\tau_{clk}$):** Discrete monotonically increasing step counter incremented on every statement evaluation and request cycle.

### 2.2 Variable Resolution Hierarchy
Lookup for identifier $x$ is formally defined as:
$$\text{resolve}(x) = \begin{cases} 
\sigma_{top}(x) & \text{if } x \in \text{dom}(\sigma_{top}) \\
v & \text{if } x \notin \text{dom}(\sigma_{top}) \land (x \mapsto (v, \tau)) \in \mathcal{E}_{TTL} \land \tau > 0 \\
\mathcal{G}(x) & \text{if } x \notin \text{dom}(\sigma_{top}) \land x \notin \text{dom}(\mathcal{E}_{TTL}) \land x \in \text{dom}(\mathcal{G}) \\
0 & \text{otherwise (safe default fallback)}
\end{cases}$$

### 2.3 Statements vs. Expressions & Expression Discarding
* **Statement-Oriented Architecture:** SMC is an imperative statement-based language. Statement blocks `{ stmts }` do **not** evaluate to expression values.
* **Expression Statements (`expr_stmt`):** Any valid expression (e.g. `fn_call()`, `x + 1`) may be executed as a standalone statement. In script execution mode, its return value is discarded; in interactive REPL mode, non-null values are formatted and emitted to stdout.

---

## 3. Explicit Operator Precedence Matrix

SMC enforces an 8-level Pratt parsing hierarchy. Subscript indexing (`[]`) and function calls (`()`) are uniform postfix operators with highest precedence.

| Level | Operator | Operation | Associativity | Example Evaluation |
| :---: | :--- | :--- | :---: | :--- |
| **7 (Highest)** | `()` | Function Call | Left-to-right | `get_fn()(arg)` |
| | `[]` | Index Access / Subscription | Left-to-right | `arr[0]`, `dict["key"]`, `get_list()[0]` |
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
| **1** | `&&`, `and` | Logical Conjunction (Short-circuiting) | Left-to-right | `a > 0 && b < 10` |
| **0 (Lowest)** | `\|\|`, `or` | Logical Disjunction (Short-circuiting) | Left-to-right | `x == 0 \|\| x == width - 1` |

### 3.1 Operator Semantics & Fault Tolerance
* **Arithmetic Fault Invariance:** Division by zero (`a / 0`) and modulo by zero (`a % 0`) deterministically evaluate to numeric `0` and emit a diagnostic warning to stdout without raising unhandled runtime termination exceptions.
* **Canonical Subscript Access:** In SMC v0.7.0, all object and associative container access is performed via index subscription `obj["field"]`. The dot `.` token is reserved for future grammar versions.

---

## 4. Type System & Coercion Specification

| Type | Mutability | Truthiness Rule | String Concatenation (`+`) | Equality (`==`) |
| :--- | :--- | :--- | :--- | :--- |
| **`number`** | Value (Immutable) | $x \neq 0$ | Formats number to string | Numeric equality |
| **`string`** | Value (Immutable) | $\text{len}(s) > 0$ | Direct concatenation | Byte string equality |
| **`bool`** | Value (Immutable) | `true` / `false` | `"true"` / `"false"` | Boolean identity |
| **`null`** | Value (Immutable) | **Always `false`** | **Coerces to `"null"`** | **`null == null` is `true`** |
| **`list`** | **Reference (Mutable)** | $\text{len}(L) > 0$ | Formats JSON array string | Reference equality |
| **`dict`** | **Reference (Mutable)** | $\text{len}(D) > 0$ | Formats JSON object string | Reference equality |

### 4.1 Collection & Index Assignment Semantics
* **Dictionary Index Assignment (`dict[key] = val` / `dict[key] += val`):** If `key` is absent, it is automatically created and assigned. In compound assignments (`+=`, `-=`), absent keys initialize from default value `0`.
* **List Index Assignment (`arr[idx] = val`):**
  * If $0 \le \text{idx} < \text{len}(arr)$: Mutates element in place.
  * If $\text{idx} < 0$: Resolves from end of array ($\text{idx} \leftarrow \text{len}(arr) + \text{idx}$).
  * If $\text{idx} \ge \text{len}(arr)$: Out-of-bounds assignments are safely caught and ignored without process termination.

---

## 5. Subsystem Semantics & Environmental Lifecycles

### 5.1 HexaPhase Multiplexing (`hexaphase`)
* **Syntax:** `hexaphase expr { stmts }`
* **Lifecycle & Scope:** Evaluates `expr` into 6 channels (`"+0", "+1", "+2", "-0", "-1", "-2"`). Binds dictionary `hexaphase_channels` into the runtime environment. The binding remains active throughout the block and persists until overwritten by a subsequent `hexaphase` block. Nested blocks overwrite the binding in-place.

### 5.2 Programmed Ribosomal Frameshifting (`slip`)
* **Syntax:** `slip(offset_expr)`
* **Semantics:** Updates the execution phase register:
  $$\Phi_{phase} \leftarrow (\Phi_{phase} + \text{int}(\text{eval}(offset\_expr))) \pmod 3$$
  Reflects the new integer value into global binding `current_phase`.

### 5.3 Stochastic Fault-Injection Block (`mutate`) [Experimental]
* **Syntax:** `mutate { stmts }`
* **Semantics:** Executes statements within a supervised fault-injection sandbox. At each step, a stochastic mutation engine perturbs AST dispatch or argument values with a default error rate of $\rho = 0.05$ (5%). PRNG seeds can be deterministically set via `py_call("random.seed", seed)`.

### 5.4 Python FFI & Security Policy
* **Syntax:** `py_call("target", *args)`, `py_eval("expr")`, `py_import "mod" as alias`
* **Security Model:** Designed for **trusted local execution** (scientific pipelines, local toolchains). The FFI inherits standard host process OS permissions (unrestricted disk and network access under the running user's account).

### 5.5 Embedded HTTP Web Server (`serve_http`)
* **Syntax:** `serve_http(port: int, handler_fn: str)`
* **Request Structure (`req: dict`):**
  ```json
  {
    "path": "/api/v1/resource",
    "method": "GET",
    "headers": { "host": "127.0.0.1:3000", "content-type": "application/json" },
    "body": "..."
  }
  ```
* **Response Structure:** Expects `{"status": int, "content_type": str, "body": str}`. Raw strings are automatically wrapped with `HTTP 200 OK text/html; charset=utf-8`.

### 5.6 Content-Addressable Ring Binding & Dispatch (`bind` / `dispatch` / `fallback`)
* **Syntax:** `bind(ring = expr) { stmts }`, `dispatch expr`, `fallback { stmts }`
* **Key Coercion:** Ring keys are normalized to uppercase string representations:
  $$\text{key}_{ring} \leftarrow \text{upper}(\text{str}(\text{eval}(expr)))$$
  Thus `bind(ring="fire")` and `dispatch "FIRE"` match identically.
* **Watchdog Execution:** If `dispatch` targets an unmapped ring key, the runtime executes the registered `fallback` block (Tuxedo Mask Watchdog). If no fallback is registered, execution proceeds without raising errors.

---

## 6. Execution Modalities & Tooling Reference

SMC source code may be parsed, evaluated, and executed across four standardized execution modalities:

### 6.1 Web Browser & WASM Playground (Zero-Install Execution)
* **Host URL:** `https://zekvftb.github.io/smc-lang/`
* **Architecture:** Client-side WebAssembly environment running Pyodide with DexterVM.
* **Security & Isolation:** 100% in-browser sandboxed execution with zero backend server dependencies and zero user data logging.

### 6.2 Native Command Line Interface (`smc`)
The canonical SMC CLI toolchain provides complete operational lifecycle management:
```powershell
# 1. Run a standalone SMC script
smc run path/to/program.smc

# 2. Launch the interactive REPL shell
smc repl

# 3. Execute dual-frame overlapping bytecode (CatDog mode)
# Note: CatDog execution is a CLI tokenizer transformation mode (alternating even/odd tokens),
# not a standalone language opcode keyword.
smc catdog path/to/dual_track.smc

# 4. Inspect token stream and automated typo repairs
smc tokens path/to/program.smc

# 5. Scaffold a new production project directory
smc init my_app
```

### 6.3 Host Embedding & Python SDK Integration
SMC can be embedded directly into existing scientific and data processing applications:
```python
from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM

# Tokenize and parse source code
source_code = """
let dataset = [10, 20, 30]
let total = 0
for val in dataset {
    total += val
}
"""
tokens = SmcLexer(source_code).tokenize()
ast = SmcParser(tokens).parse()

# Execute within DexterVM
vm = DexterVM()
result = vm.run(ast)

# Access computed variables from host
print(result["final_variables"]["total"])  # 60
```

### 6.4 IDE Syntax Highlighting & Grammar
The SMC language provides a formal TextMate grammar definition (`smc.tmLanguage.json`) compatible with Visual Studio Code, Cursor, and VSCodium, delivering real-time keyword highlighting, bracket matching, and template literal interpolation coloring.

---

## 7. Formal Language Conformance & Implementation Standards

To ensure cross-platform reproducibility and guarantee that alternative compiler and interpreter implementations behave identically to DexterVM, compliant runtimes must satisfy the following five invariants:

### 7.1 Grammatical & Operator Invariant
1. All compliant parsers must enforce the exact 8-tier Pratt precedence hierarchy defined in Section 3.
2. Function invocations (`()`) and subscript indexing (`[]`) must operate as uniform left-associative postfix operators with equal precedence (Tier 7).

### 7.2 Memory & State Invariant
1. **Activation Stack Isolation:** Function calls must create an isolated activation frame. Local variables declared inside a function body must not leak into parent or global environments upon function return.
2. **Monotonic Ephemeral Decay:** Variables declared with `acme(ttl=k)` must decrement their counter $\tau$ on every discrete execution step and upon receiving an HTTP request, vaporizing completely when $\tau \le 0$.
3. **Phase Storage:** The reading phase register $\Phi_{phase} \in \{0, 1, 2\}$ must initialize to $0$, expose its value via `current_phase`, and wrap modulo 3 upon `slip(k)`.

### 7.3 Type Coercion & Arithmetic Fault Invariant
1. **Safe Division:** Division by zero (`a / 0`) or modulo by zero (`a % 0`) must never raise a fatal process termination exception; compliant runtimes must evaluate the expression to `0` and emit a diagnostic warning to stdout.
2. **Safe Uninitialized Reads:** Reading unassigned variables must deterministically evaluate to numeric `0`, string `""`, or boolean `false`.
3. **Out-of-Bounds Subscripts:** Writing to an out-of-bounds list index must be safely trapped and ignored without terminating program execution.

### 7.4 Content-Addressable Ring Normalization Invariant
1. All ring keys in `bind(ring=expr)` and `dispatch expr` must undergo uppercase string normalization ($\text{key} \leftarrow \text{upper}(\text{str}(\text{eval}(expr)))$).
2. If `dispatch` targets an unmapped ring key, the runtime must invoke the `fallback` handler if present, or continue execution silently if absent.

### 7.5 Typo-Tolerance & Degeneracy Rules
1. Keyword synonyms (e.g. `SUGAR`, `SPICE`, `LET`, `SET`, `VAR`) must map to identical AST statement representations.
2. Lexical Levenshtein edit-distance repair must be strictly bounded: length $\le 4 \implies d=1$; $5 \le \text{length} \le 6 \implies d=1$; $\text{length} \ge 7 \implies d=2$.
3. Built-in functions (`len`, `push`, `pop`, `str`, `int`, etc.) and single-character identifiers must never undergo automatic mutation repair.

