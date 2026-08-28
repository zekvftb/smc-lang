/**
 * SMC (Saturday Morning Cartoons) - In-Browser DexterVM Runtime Engine
 * Implements fault-tolerant codon wobble lexing, AST parsing, Acme Anvil TTL decay,
 * and Planeteer/Senshi shape-based function dispatch in pure JavaScript.
 */

// ---------------------------------------------------------------------------
// 1. Tokens & Codon Degeneracy Dictionary
// ---------------------------------------------------------------------------

const OPCODE_SYNONYMS = {
    EXPERIMENT: ["EXPERIMENT", "PROGRAM", "MODULE", "DEXTER_LAB_EXPERIMENT", "SECRET_LAB", "OMNITRIX_INIT"],
    SET_VAR: ["LET", "SET", "VAR", "SUGAR", "SPICE", "EVERYTHING_NICE", "CHEMICAL_X"],
    TTL_BOX: ["ACME", "ACME_ANVIL_BOX", "ACME_BOX", "EPHEMERAL", "ANVIL_BOX", "DISPOSABLE_VAR"],
    IF: ["IF", "WHEN", "CHECK_GATE", "TEST"],
    ELSE: ["ELSE", "OTHERWISE", "DEFAULT"],
    WHILE: ["WHILE", "LOOP", "CYCLE", "ROAD_RUNNER_LOOP"],
    FOR: ["FOR", "EACH", "FOR_EACH", "ITERATE"],
    IN: ["IN", "INSIDE", "FROM"],
    FN: ["FN", "FUNCTION", "DEF", "SUBROUTINE", "RECIPE", "TECHNIQUE"],
    RETURN: ["RETURN", "YIELD", "GIVE", "PAYLOAD"],
    SUMMON: ["BIND", "SUMMON", "SUMMON_PLANETEER", "PLANET_POWER", "CAPTAIN_PLANET", "RING_BIND"],
    CALL_RING: ["DISPATCH", "CALL", "POWERS_COMBINED", "RING_CALL", "INVOKE_RING", "I_CHOOSE_YOU"],
    TRANSFORM: ["MPP", "TRANSFORM", "MOON_PRISM_POWER", "DIFFERENTIATE", "EVOLVE", "MORPH", "SAILOR_TRANSFORM"],
    FALLBACK: ["FALLBACK", "TUXEDO_MASK", "CATCH", "DEFAULT_HANDLER", "ROSE_THROW"],
    PRINT: ["PRINT", "EMIT", "SAY", "SHOUT", "KAMEHAMEHA", "HADOUKEN", "COWABUNGA_NEWS"],
    MUTATE: ["MUTATE", "DEE_DEE_MUTATION", "DEE_DEE_BUTTON", "OOPS_MUTATION", "RADIOACTIVE_SPIDER"],
    IMPORT: ["IMPORT", "INCLUDE", "REQUIRE", "LOAD_MODULE", "PLASMID_INJECT", "TRANSFECT"],
    PY_IMPORT: ["PY_IMPORT", "PYTHON_IMPORT", "IMPORT_PY", "CYTO_BRIDGE", "PYTHON"],
    HEXAPHASE: ["HEXAPHASE", "HEXA_PHASE", "MULTIPLEX", "POLYPHASE", "CATDOG", "CAT_DOG"],
    SLIP: ["SLIP", "FRAMESHIFT", "PRF", "RIBO_SLIP", "PHASE_SHIFT"],
    ATTENUATOR: ["ATTENUATOR", "THROTTLE", "STEM_LOOP", "HAIRPIN_GATE", "PAUSE_GATE"],
    HALT: ["HALT", "EXIT", "THATS_ALL_FOLKS", "COWABUNGA", "FIN"]
};

const VIRTUAL_FS = {
    "math_utils.smc": `let PI = 3.14159265\nfn square(x) { return x * x }\nfn power(b, e) {\n    let res = 1\n    for i in range(0, e) { res *= b }\n    return res\n}\n`,
    "models/user.smc": `let DEFAULT_ROLE = "Scientist"\nfn create_user(name) {\n    return { "name": name, "role": DEFAULT_ROLE, "access": true }\n}\n`
};

const KEYWORD_TO_OPCODE = {};
for (const [op, syns] of Object.entries(OPCODE_SYNONYMS)) {
    for (const syn of syns) {
        KEYWORD_TO_OPCODE[syn.toUpperCase()] = op;
    }
}

const BUILTIN_NAMES = new Set([
    "LEN", "PUSH", "POP", "STR", "INT", "TYPE", "READ_FILE", "WRITE_FILE", "SERVE_HTTP",
    "TO_JSON", "FROM_JSON", "RANGE", "SPLIT", "JOIN", "KEYS", "VALUES", "CONTAINS", "SERVE_FILE",
    "PY_CALL", "PY_EVAL", "HEXAPHASE_COMPILE", "HEXAPHASE_DECOMPILE", "HEXAPHASE_CHANNELS", "PHASE_SLIP",
    "TRUE", "FALSE", "NULL", "AND", "OR"
]);

function levenshteinDistance(s1, s2) {
    if (s1.length < s2.length) return levenshteinDistance(s2, s1);
    if (s2.length === 0) return s1.length;
    let prev = Array.from({ length: s2.length + 1 }, (_, i) => i);
    for (let i = 0; i < s1.length; i++) {
        let curr = [i + 1];
        for (let j = 0; j < s2.length; j++) {
            let ins = prev[j + 1] + 1;
            let del = curr[j] + 1;
            let sub = prev[j] + (s1[i] !== s2[j] ? 1 : 0);
            curr.push(Math.min(ins, del, sub));
        }
        prev = curr;
    }
    return prev[prev.length - 1];
}

function resolveWobbleOpcode(rawToken) {
    const clean = rawToken.trim().toUpperCase();
    if (clean.length <= 1) return null;
    if (BUILTIN_NAMES.has(clean)) return null;
    if (KEYWORD_TO_OPCODE[clean]) return KEYWORD_TO_OPCODE[clean];

    const maxDist = clean.length <= 4 ? 1 : 2;
    let bestOp = null;
    let bestDist = 999;

    for (const [kw, op] of Object.entries(KEYWORD_TO_OPCODE)) {
        if (Math.abs(clean.length - kw.length) > maxDist) continue;
        const dist = levenshteinDistance(clean, kw);
        if (dist < bestDist && dist <= maxDist) {
            bestDist = dist;
            bestOp = op;
        }
    }
    return bestOp;
}

// ---------------------------------------------------------------------------
// 2. Lexer
// ---------------------------------------------------------------------------

class SmcLexer {
    constructor(source) {
        this.source = source;
        this.pos = 0;
        this.line = 1;
        this.col = 1;
    }

    peek(offset = 0) {
        const idx = this.pos + offset;
        return idx < this.source.length ? this.source[idx] : "\0";
    }

    advance() {
        const ch = this.peek();
        this.pos++;
        if (ch === "\n") {
            this.line++;
            this.col = 1;
        } else {
            this.col++;
        }
        return ch;
    }

    skipWhitespaceAndComments() {
        while (this.pos < this.source.length) {
            const ch = this.peek();
            if (" \t\r\n".includes(ch)) {
                this.advance();
            } else if (ch === "#") {
                while (this.pos < this.source.length && this.peek() !== "\n") {
                    this.advance();
                }
            } else {
                break;
            }
        }
    }

    tokenize() {
        const tokens = [];
        while (this.pos < this.source.length) {
            this.skipWhitespaceAndComments();
            if (this.pos >= this.source.length) break;

            const ch = this.peek();
            const startLine = this.line;
            const startCol = this.col;

            // Multi-char operators
            if (ch === "=" && this.peek(1) === "=") {
                this.advance(); this.advance();
                tokens.push({ type: "EQ_EQ", value: "==", line: startLine, col: startCol });
            } else if (ch === "!" && this.peek(1) === "=") {
                this.advance(); this.advance();
                tokens.push({ type: "NOT_EQ", value: "!=", line: startLine, col: startCol });
            } else if (ch === "<" && this.peek(1) === "=") {
                this.advance(); this.advance();
                tokens.push({ type: "LTE", value: "<=", line: startLine, col: startCol });
            } else if (ch === ">" && this.peek(1) === "=") {
                this.advance(); this.advance();
                tokens.push({ type: "GTE", value: ">=", line: startLine, col: startCol });
            } else if (ch === "&" && this.peek(1) === "&") {
                this.advance(); this.advance();
                tokens.push({ type: "AND", value: "&&", line: startLine, col: startCol });
            } else if (ch === "|" && this.peek(1) === "|") {
                this.advance(); this.advance();
                tokens.push({ type: "OR", value: "||", line: startLine, col: startCol });
            } else if (ch === "+" && this.peek(1) === "=") {
                this.advance(); this.advance();
                tokens.push({ type: "PLUS_EQ", value: "+=", line: startLine, col: startCol });
            } else if (ch === "-" && this.peek(1) === "=") {
                this.advance(); this.advance();
                tokens.push({ type: "MINUS_EQ", value: "-=", line: startLine, col: startCol });
            } else if (ch === "*" && this.peek(1) === "=") {
                this.advance(); this.advance();
                tokens.push({ type: "STAR_EQ", value: "*=", line: startLine, col: startCol });
            } else if (ch === "/" && this.peek(1) === "=") {
                this.advance(); this.advance();
                tokens.push({ type: "SLASH_EQ", value: "/=", line: startLine, col: startCol });
            }
            // Single-character delimiters
            else if (ch === "(") { this.advance(); tokens.push({ type: "LPAREN", value: "(", line: startLine, col: startCol }); }
            else if (ch === ")") { this.advance(); tokens.push({ type: "RPAREN", value: ")", line: startLine, col: startCol }); }
            else if (ch === "[") { this.advance(); tokens.push({ type: "LBRACKET", value: "[", line: startLine, col: startCol }); }
            else if (ch === "]") { this.advance(); tokens.push({ type: "RBRACKET", value: "]", line: startLine, col: startCol }); }
            else if (ch === "{") { this.advance(); tokens.push({ type: "LBRACE", value: "{", line: startLine, col: startCol }); }
            else if (ch === "}") { this.advance(); tokens.push({ type: "RBRACE", value: "}", line: startLine, col: startCol }); }
            else if (ch === ":") { this.advance(); tokens.push({ type: "COLON", value: ":", line: startLine, col: startCol }); }
            else if (ch === "=") { this.advance(); tokens.push({ type: "EQUALS", value: "=", line: startLine, col: startCol }); }
            else if (ch === ",") { this.advance(); tokens.push({ type: "COMMA", value: ",", line: startLine, col: startCol }); }
            else if (ch === "+") { this.advance(); tokens.push({ type: "PLUS", value: "+", line: startLine, col: startCol }); }
            else if (ch === "-") { this.advance(); tokens.push({ type: "MINUS", value: "-", line: startLine, col: startCol }); }
            else if (ch === "*") { this.advance(); tokens.push({ type: "STAR", value: "*", line: startLine, col: startCol }); }
            else if (ch === "/") { this.advance(); tokens.push({ type: "SLASH", value: "/", line: startLine, col: startCol }); }
            else if (ch === "%") { this.advance(); tokens.push({ type: "PERCENT", value: "%", line: startLine, col: startCol }); }
            else if (ch === "<") { this.advance(); tokens.push({ type: "LT", value: "<", line: startLine, col: startCol }); }
            else if (ch === ">") { this.advance(); tokens.push({ type: "GT", value: ">", line: startLine, col: startCol }); }
            else if (ch === "!") { this.advance(); tokens.push({ type: "NOT", value: "!", line: startLine, col: startCol }); }
            // Strings
            else if (ch === '"' || ch === "'") {
                const quote = this.advance();
                let strVal = "";
                while (this.pos < this.source.length && this.peek() !== quote) {
                    strVal += this.advance();
                }
                if (this.peek() === quote) this.advance();
                tokens.push({ type: "STRING", value: strVal, line: startLine, col: startCol });
            }
            // Template Strings: `...`
            else if (ch === '`') {
                this.advance();
                let strVal = "";
                while (this.pos < this.source.length && this.peek() !== '`') {
                    strVal += this.advance();
                }
                if (this.peek() === '`') this.advance();
                tokens.push({ type: "TEMPLATE_STRING", value: strVal, line: startLine, col: startCol });
            }
            // Numbers
            else if (/[0-9]/.test(ch)) {
                let numStr = "";
                while (this.pos < this.source.length && (/[0-9]/.test(this.peek()) || this.peek() === ".")) {
                    numStr += this.advance();
                }
                tokens.push({ type: "NUMBER", value: parseFloat(numStr), line: startLine, col: startCol });
            }
            // Identifiers & Keywords
            else if (/[a-zA-Z_]/.test(ch)) {
                let ident = "";
                while (this.pos < this.source.length && /[a-zA-Z0-9_]/.test(this.peek())) {
                    ident += this.advance();
                }
                const identLower = ident.toLowerCase();
                if (identLower === "and") {
                    tokens.push({ type: "AND", value: "and", line: startLine, col: startCol });
                } else if (identLower === "or") {
                    tokens.push({ type: "OR", value: "or", line: startLine, col: startCol });
                } else {
                    const op = resolveWobbleOpcode(ident);
                    if (op) {
                        tokens.push({ type: "KEYWORD", value: ident, opcode: op, line: startLine, col: startCol });
                    } else {
                        tokens.push({ type: "IDENTIFIER", value: ident, line: startLine, col: startCol });
                    }
                }
            } else {
                this.advance();
            }
        }
        tokens.push({ type: "EOF", value: "", line: this.line, col: this.col });
        return tokens;
    }
}

// ---------------------------------------------------------------------------
// 3. Parser
// ---------------------------------------------------------------------------

class SmcParser {
    constructor(tokens) {
        this.tokens = tokens;
        this.pos = 0;
    }

    peek(offset = 0) {
        const idx = this.pos + offset;
        return idx < this.tokens.length ? this.tokens[idx] : this.tokens[this.tokens.length - 1];
    }

    advance() {
        const tok = this.peek();
        this.pos++;
        return tok;
    }

    matchOpcode(op) {
        const tok = this.peek();
        return tok.type === "KEYWORD" && tok.opcode === op;
    }

    parseExpression() {
        return this.parseLogicalOr();
    }

    parseLogicalOr() {
        let expr = this.parseLogicalAnd();
        while (this.peek().type === "OR") {
            const op = this.advance().value;
            const right = this.parseLogicalAnd();
            expr = { type: "BinaryOp", left: expr, op, right };
        }
        return expr;
    }

    parseLogicalAnd() {
        let expr = this.parseEquality();
        while (this.peek().type === "AND") {
            const op = this.advance().value;
            const right = this.parseEquality();
            expr = { type: "BinaryOp", left: expr, op, right };
        }
        return expr;
    }

    parseEquality() {
        let expr = this.parseComparison();
        while (["EQ_EQ", "NOT_EQ"].includes(this.peek().type)) {
            const op = this.advance().value;
            const right = this.parseComparison();
            expr = { type: "BinaryOp", left: expr, op, right };
        }
        return expr;
    }

    parseComparison() {
        let expr = this.parseTerm();
        while (["LT", "LTE", "GT", "GTE"].includes(this.peek().type)) {
            const op = this.advance().value;
            const right = this.parseTerm();
            expr = { type: "BinaryOp", left: expr, op, right };
        }
        return expr;
    }

    parseTerm() {
        let expr = this.parseFactor();
        while (["PLUS", "MINUS"].includes(this.peek().type)) {
            const op = this.advance().value;
            const right = this.parseFactor();
            expr = { type: "BinaryOp", left: expr, op, right };
        }
        return expr;
    }

    parseFactor() {
        let expr = this.parseUnary();
        while (["STAR", "SLASH", "PERCENT"].includes(this.peek().type)) {
            const op = this.advance().value;
            const right = this.parseUnary();
            expr = { type: "BinaryOp", left: expr, op, right };
        }
        return expr;
    }

    parseUnary() {
        if (["MINUS", "NOT"].includes(this.peek().type)) {
            const op = this.advance().value;
            const operand = this.parseUnary();
            return { type: "UnaryOp", op, operand };
        }
        return this.parsePrimary();
    }

    parsePrimary() {
        const tok = this.peek();

        if (tok.type === "NUMBER" || tok.type === "STRING") {
            this.advance();
            return { type: "Literal", value: tok.value };
        }

        // Template Strings: `Hello ${name}!`
        if (tok.type === "TEMPLATE_STRING") {
            this.advance();
            const raw = tok.value;
            const pattern = /\$\{([^}]+)\}/g;
            const parts = [];
            let lastIdx = 0;
            let match;
            while ((match = pattern.exec(raw)) !== null) {
                if (match.index > lastIdx) {
                    parts.push({ type: "Literal", value: raw.slice(lastIdx, match.index) });
                }
                const exprCode = match[1].trim();
                const subLexer = new SmcLexer(exprCode);
                const subToks = subLexer.tokenize();
                const subParser = new SmcParser(subToks);
                const subAst = subParser.parseExpression();
                parts.push({ type: "FunctionCall", name: "str", args: [subAst] });
                lastIdx = pattern.lastIndex;
            }
            if (lastIdx < raw.length) {
                parts.push({ type: "Literal", value: raw.slice(lastIdx) });
            }
            if (parts.length === 0) return { type: "Literal", value: "" };
            let resExpr = parts[0];
            for (let i = 1; i < parts.length; i++) {
                resExpr = { type: "BinaryOp", left: resExpr, op: "+", right: parts[i] };
            }
            return resExpr;
        }

        // Dictionary: { k: v, ... }
        if (tok.type === "LBRACE") {
            this.advance();
            const pairs = [];
            while (this.peek().type !== "RBRACE" && this.peek().type !== "EOF") {
                const k = this.parseExpression();
                if (this.peek().type === "COLON") this.advance();
                const v = this.parseExpression();
                pairs.push([k, v]);
                if (this.peek().type === "COMMA") this.advance();
            }
            if (this.peek().type === "RBRACE") this.advance();
            let expr = { type: "Dict", pairs };
            while (this.peek().type === "LBRACKET") {
                this.advance();
                const idx = this.parseExpression();
                if (this.peek().type === "RBRACKET") this.advance();
                expr = { type: "IndexAccess", target: expr, index: idx };
            }
            return expr;
        }

        // List: [ item, ... ]
        if (tok.type === "LBRACKET") {
            this.advance();
            const elements = [];
            while (this.peek().type !== "RBRACKET" && this.peek().type !== "EOF") {
                elements.push(this.parseExpression());
                if (this.peek().type === "COMMA") this.advance();
            }
            if (this.peek().type === "RBRACKET") this.advance();
            let expr = { type: "List", elements };
            while (this.peek().type === "LBRACKET") {
                this.advance();
                const idx = this.parseExpression();
                if (this.peek().type === "RBRACKET") this.advance();
                expr = { type: "IndexAccess", target: expr, index: idx };
            }
            return expr;
        }

        // Identifiers (Variable, Function Call, Booleans, or Index)
        if (tok.type === "IDENTIFIER") {
            const lower = tok.value.toLowerCase();
            if (lower === "true") { this.advance(); return { type: "Literal", value: true }; }
            if (lower === "false") { this.advance(); return { type: "Literal", value: false }; }
            if (["null", "none"].includes(lower)) { this.advance(); return { type: "Literal", value: null }; }

            this.advance();
            const name = tok.value;
            let expr;
            if (this.peek().type === "LPAREN") {
                this.advance();
                const args = [];
                while (this.peek().type !== "RPAREN" && this.peek().type !== "EOF") {
                    args.push(this.parseExpression());
                    if (this.peek().type === "COMMA") this.advance();
                }
                if (this.peek().type === "RPAREN") this.advance();
                expr = { type: "FunctionCall", name, args };
            } else {
                expr = { type: "Variable", name };
            }

            while (this.peek().type === "LBRACKET") {
                this.advance();
                const idx = this.parseExpression();
                if (this.peek().type === "RBRACKET") this.advance();
                expr = { type: "IndexAccess", target: expr, index: idx };
            }
            return expr;
        }

        // Grouping: (expr)
        if (tok.type === "LPAREN") {
            this.advance();
            const expr = this.parseExpression();
            if (this.peek().type === "RPAREN") this.advance();
            return expr;
        }

        this.advance();
        return { type: "Literal", value: tok.value };
    }

    parse() {
        let name = "Untitled_Toon_Experiment";
        const statements = [];

        if (this.matchOpcode("EXPERIMENT")) {
            this.advance();
            if (["STRING", "IDENTIFIER"].includes(this.peek().type)) {
                name = this.advance().value;
            }
        }

        while (this.pos < this.tokens.length && this.peek().type !== "EOF") {
            const stmt = this.parseStatement();
            if (stmt) statements.push(stmt);
        }

        return { type: "Program", name, statements };
    }

    parseStatement() {
        const tok = this.peek();
        if (tok.type === "EOF") return null;

        // LET
        if (this.matchOpcode("SET_VAR")) {
            this.advance();
            const ident = this.advance().value;
            if (this.peek().type === "EQUALS") this.advance();
            const expr = this.parseExpression();
            return { type: "SetVar", name: ident, expr };
        }

        // ACME TTL
        if (this.matchOpcode("TTL_BOX")) {
            this.advance();
            let ttl = 3;
            if (this.peek().type === "LPAREN") {
                this.advance();
                if (String(this.peek().value).toLowerCase() === "ttl") {
                    this.advance();
                    if (this.peek().type === "EQUALS") this.advance();
                    ttl = parseInt(this.advance().value);
                }
                if (this.peek().type === "RPAREN") this.advance();
            }
            const ident = this.advance().value;
            if (this.peek().type === "EQUALS") this.advance();
            const expr = this.parseExpression();
            return { type: "TtlBox", name: ident, expr, ttl };
        }

        // IF / ELSE
        if (this.matchOpcode("IF")) {
            this.advance();
            const cond = this.parseExpression();
            const thenBranch = [];
            if (this.peek().type === "LBRACE") {
                this.advance();
                while (this.pos < this.tokens.length && this.peek().type !== "RBRACE") {
                    const s = this.parseStatement();
                    if (s) thenBranch.push(s);
                }
                if (this.peek().type === "RBRACE") this.advance();
            }
            const elseBranch = [];
            if (this.matchOpcode("ELSE")) {
                this.advance();
                if (this.peek().type === "LBRACE") {
                    this.advance();
                    while (this.pos < this.tokens.length && this.peek().type !== "RBRACE") {
                        const s = this.parseStatement();
                        if (s) elseBranch.push(s);
                    }
                    if (this.peek().type === "RBRACE") this.advance();
                }
            }
            return { type: "If", condition: cond, thenBranch, elseBranch };
        }

        // WHILE
        if (this.matchOpcode("WHILE")) {
            this.advance();
            const cond = this.parseExpression();
            const body = [];
            if (this.peek().type === "LBRACE") {
                this.advance();
                while (this.pos < this.tokens.length && this.peek().type !== "RBRACE") {
                    const s = this.parseStatement();
                    if (s) body.push(s);
                }
                if (this.peek().type === "RBRACE") this.advance();
            }
            return { type: "While", condition: cond, body };
        }

        // FOR-IN
        if (this.matchOpcode("FOR")) {
            this.advance();
            const itemName = this.advance().value;
            if (this.matchOpcode("IN")) this.advance();
            const coll = this.parseExpression();
            const body = [];
            if (this.peek().type === "LBRACE") {
                this.advance();
                while (this.pos < this.tokens.length && this.peek().type !== "RBRACE") {
                    const s = this.parseStatement();
                    if (s) body.push(s);
                }
                if (this.peek().type === "RBRACE") this.advance();
            }
            return { type: "ForIn", itemName, collection: coll, body };
        }

        // FN
        if (this.matchOpcode("FN")) {
            this.advance();
            const fnName = this.advance().value;
            const params = [];
            if (this.peek().type === "LPAREN") {
                this.advance();
                while (this.peek().type !== "RPAREN" && this.peek().type !== "EOF") {
                    params.push(this.advance().value);
                    if (this.peek().type === "COMMA") this.advance();
                }
                if (this.peek().type === "RPAREN") this.advance();
            }
            const body = [];
            if (this.peek().type === "LBRACE") {
                this.advance();
                while (this.pos < this.tokens.length && this.peek().type !== "RBRACE") {
                    const s = this.parseStatement();
                    if (s) body.push(s);
                }
                if (this.peek().type === "RBRACE") this.advance();
            }
            return { type: "FunctionDef", name: fnName, params, body };
        }

        // RETURN
        if (this.matchOpcode("RETURN")) {
            this.advance();
            const expr = this.parseExpression();
            return { type: "Return", expr };
        }

        // SUMMON (BIND RING)
        if (this.matchOpcode("SUMMON")) {
            this.advance();
            let ring = "HEART";
            if (this.peek().type === "LPAREN") {
                this.advance();
                if (String(this.peek().value).toLowerCase() === "ring") {
                    this.advance();
                    if (this.peek().type === "EQUALS") this.advance();
                    ring = String(this.advance().value).toUpperCase();
                } else {
                    ring = String(this.advance().value).toUpperCase();
                }
                if (this.peek().type === "RPAREN") this.advance();
            }
            const body = [];
            if (this.peek().type === "LBRACE") {
                this.advance();
                while (this.pos < this.tokens.length && this.peek().type !== "RBRACE") {
                    const s = this.parseStatement();
                    if (s) body.push(s);
                }
                if (this.peek().type === "RBRACE") this.advance();
            }
            return { type: "Summon", ring, body };
        }

        // CALL RING (DISPATCH)
        if (this.matchOpcode("CALL_RING")) {
            this.advance();
            const ring = String(this.advance().value).toUpperCase();
            return { type: "CallRing", ring };
        }

        // TRANSFORM (MOON_PRISM_POWER)
        if (this.matchOpcode("TRANSFORM")) {
            this.advance();
            const ident = this.advance().value;
            if (this.peek().type === "EQUALS") this.advance();
            const expr = this.parseExpression();
            const body = [];
            if (this.peek().type === "LBRACE") {
                this.advance();
                while (this.pos < this.tokens.length && this.peek().type !== "RBRACE") {
                    const s = this.parseStatement();
                    if (s) body.push(s);
                }
                if (this.peek().type === "RBRACE") this.advance();
            }
            return { type: "Transform", target: ident, expr, body };
        }

        // FALLBACK (TUXEDO_MASK)
        if (this.matchOpcode("FALLBACK")) {
            this.advance();
            const body = [];
            if (this.peek().type === "LBRACE") {
                this.advance();
                while (this.pos < this.tokens.length && this.peek().type !== "RBRACE") {
                    const s = this.parseStatement();
                    if (s) body.push(s);
                }
                if (this.peek().type === "RBRACE") this.advance();
            }
            return { type: "Fallback", body };
        }

        // PRINT
        if (this.matchOpcode("PRINT")) {
            this.advance();
            const expr = this.parseExpression();
            return { type: "Print", expr };
        }

        // Indexed Assignment / Compound Assign / Function Call Expression
        if (tok.type === "IDENTIFIER") {
            const nextTok = this.peek(1);

            // ident[k] = val or ident[k] += val
            if (nextTok.type === "LBRACKET") {
                const name = this.advance().value;
                this.advance(); // [
                const idx = this.parseExpression();
                if (this.peek().type === "RBRACKET") this.advance();
                const opTok = this.advance();
                const valExpr = this.parseExpression();
                return { type: "IndexAssign", target: name, index: idx, op: opTok.value, value: valExpr };
            }

            // ident += val
            if (["PLUS_EQ", "MINUS_EQ", "STAR_EQ", "SLASH_EQ"].includes(nextTok.type)) {
                const name = this.advance().value;
                const op = this.advance().value;
                const expr = this.parseExpression();
                return { type: "CompoundAssign", name, op, expr };
            }

            // ident = val (reassignment)
            if (nextTok.type === "EQUALS") {
                const name = this.advance().value;
                this.advance(); // =
                const expr = this.parseExpression();
                return { type: "SetVar", name, expr };
            }

            // ident(...)
            if (nextTok.type === "LPAREN") {
                const expr = this.parseExpression();
                return { type: "ExpressionStatement", expr };
            }
        }

        // IMPORT: import "module.smc"
        if (this.matchOpcode("IMPORT")) {
            this.advance();
            const path = this.advance().value;
            return { type: "Import", path: String(path) };
        }

        // PY_IMPORT: py_import "math"
        if (this.matchOpcode("PY_IMPORT")) {
            this.advance();
            const mod = this.advance().value;
            let alias = null;
            if (this.peek().type === "IDENTIFIER" && String(this.peek().value).toLowerCase() === "as") {
                this.advance();
                alias = this.advance().value;
            }
            return { type: "PyImport", module: String(mod), alias };
        }

        // HALT
        if (this.matchOpcode("HALT")) {
            this.advance();
            return { type: "Halt" };
        }

        this.advance();
        return null;
    }
}

// ---------------------------------------------------------------------------
// 4. In-Browser DexterVM
// ---------------------------------------------------------------------------

class DexterVM {
    constructor() {
        this.variables = {};
        this.ttlMemory = {};
        this.planeteerRings = {};
        this.functions = {};
        this.callStack = [];
        this.returnTriggered = false;
        this.lastReturnValue = 0;
        this.fallbackHandler = null;
        this.stdout = [];
        this.executionSteps = 0;
        this.anvilsDropped = 0;
        this.halted = false;
        this.importedModules = new Set();
        this.serverPort = null;
        this.serverHandler = null;
    }

    tickAcmeTtls() {
        const expired = [];
        for (const [name, item] of Object.entries(this.ttlMemory)) {
            item.ttl -= 1;
            if (item.ttl <= 0) expired.push(name);
        }
        for (const name of expired) {
            delete this.ttlMemory[name];
            this.anvilsDropped += 1;
            this.stdout.push(`[ACME_ANVIL] *ANVIL DROPPED* on '${name}'! Ephemeral variable dissolved.`);
        }
    }

    getVar(name) {
        if (this.callStack.length > 0 && name in this.callStack[this.callStack.length - 1]) {
            return this.callStack[this.callStack.length - 1][name];
        }
        if (name in this.ttlMemory) return this.ttlMemory[name].value;
        if (name in this.variables) return this.variables[name];
        return 0;
    }

    setVar(name, val) {
        if (this.callStack.length > 0) {
            this.callStack[this.callStack.length - 1][name] = val;
        } else {
            this.variables[name] = val;
        }
    }

    evalExpr(node) {
        if (!node) return 0;

        if (node.type === "Literal") return node.value;
        if (node.type === "Variable") return this.getVar(node.name);

        if (node.type === "List") {
            return node.elements.map(e => this.evalExpr(e));
        }

        if (node.type === "Dict") {
            const obj = {};
            for (const [kNode, vNode] of node.pairs) {
                obj[this.evalExpr(kNode)] = this.evalExpr(vNode);
            }
            return obj;
        }

        if (node.type === "IndexAccess") {
            const target = this.evalExpr(node.target);
            const idx = this.evalExpr(node.index);
            if (target && typeof target === "object") {
                if (Array.isArray(target) || typeof target === "string") {
                    let numIdx = parseInt(idx);
                    if (numIdx < 0) numIdx = target.length + numIdx;
                    return target[numIdx] ?? 0;
                }
                return target[idx] ?? 0;
            }
            return 0;
        }

        if (node.type === "FunctionCall") {
            const args = node.args.map(a => this.evalExpr(a));
            const fnLower = node.name.toLowerCase();

            // Built-ins
            if (fnLower === "len") return args[0]?.length ?? 0;
            if (fnLower === "push" && Array.isArray(args[0])) {
                args[0].push(args[1]);
                return args[0];
            }
            if (fnLower === "pop" && Array.isArray(args[0])) return args[0].pop() ?? 0;
            if (fnLower === "str") return String(args[0] ?? "");
            if (fnLower === "int") return parseInt(args[0] ?? 0) || 0;
            if (fnLower === "type") {
                const val = args[0];
                if (Array.isArray(val)) return "list";
                if (val && typeof val === "object") return "dict";
                if (typeof val === "boolean") return "bool";
                if (typeof val === "number") return "number";
                return typeof val;
            }
            if (fnLower === "to_json") {
                try { return JSON.stringify(args[0], null, 2); } catch { return "{}"; }
            }
            if (fnLower === "from_json") {
                try { return JSON.parse(args[0]); } catch { return {}; }
            }
            if (fnLower === "range") {
                if (args.length === 1) return Array.from({length: parseInt(args[0]) || 0}, (_, i) => i);
                if (args.length >= 2) {
                    const start = parseInt(args[0]) || 0, end = parseInt(args[1]) || 0, step = parseInt(args[2]) || 1;
                    const res = [];
                    for (let i = start; i < end; i += step) res.push(i);
                    return res;
                }
                return [];
            }
            if (fnLower === "split") {
                return String(args[0] ?? "").split(args[1] ?? "");
            }
            if (fnLower === "join") {
                return (Array.isArray(args[0]) ? args[0] : []).join(args[1] ?? "");
            }
            if (fnLower === "keys") {
                return args[0] && typeof args[0] === "object" ? Object.keys(args[0]) : [];
            }
            if (fnLower === "values") {
                return args[0] && typeof args[0] === "object" ? Object.values(args[0]) : [];
            }
            if (fnLower === "contains") {
                if (Array.isArray(args[0]) || typeof args[0] === "string") return args[0].includes(args[1]);
                if (args[0] && typeof args[0] === "object") return args[1] in args[0];
                return false;
            }
            if (fnLower === "hexaphase_compile") {
                const s1 = String(args[0] ?? ""), s2 = String(args[1] ?? "");
                const res = [];
                const maxL = Math.max(s1.length, s2.length);
                for (let i = 0; i < maxL; i++) {
                    if (i < s1.length) res.push(s1[i]);
                    if (i < s2.length) res.push(s2[i]);
                }
                return res.join("");
            }
            if (fnLower === "hexaphase_decompile" || fnLower === "hexaphase_channels") {
                const s = String(args[0] ?? "");
                const n = s.length;
                const rev = s.split("").reverse().join("");
                return {
                    "+0": Array.from({length: Math.ceil(n/3)}, (_, i) => s[i*3]).join(""),
                    "+1": Array.from({length: Math.ceil((n-1)/3)}, (_, i) => s[i*3+1]).join(""),
                    "+2": Array.from({length: Math.ceil((n-2)/3)}, (_, i) => s[i*3+2]).join(""),
                    "-0": Array.from({length: Math.ceil(n/3)}, (_, i) => rev[i*3]).join(""),
                    "-1": Array.from({length: Math.ceil((n-1)/3)}, (_, i) => rev[i*3+1]).join(""),
                    "-2": Array.from({length: Math.ceil((n-2)/3)}, (_, i) => rev[i*3+2]).join(""),
                };
            }
            if (fnLower === "phase_slip") {
                const s = String(args[0] ?? "");
                const offset = (parseInt(args[1]) || 1) % (s.length || 1);
                return s.slice(offset) + s.slice(0, offset);
            }
            if (fnLower === "serve_http") {
                this.serverPort = args[0] || 3000;
                this.serverHandler = String(args[1] || "handle_request");
                this.stdout.push(`[HTTP_SERVER] Laboratory server active on port ${this.serverPort}! Virtual Browser connected.`);
                return true;
            }
            if (fnLower === "py_call") {
                if (!args || args.length === 0) return null;
                const target = String(args[0]);
                const cArgs = args.slice(1);
                if (target === "math.sqrt" || target === "sqrt") return Math.sqrt(cArgs[0] ?? 0);
                if (target === "math.pow" || target === "pow") return Math.pow(cArgs[0] ?? 0, cArgs[1] ?? 1);
                if (target === "math.sin" || target === "sin") return Math.sin(cArgs[0] ?? 0);
                if (target === "math.cos" || target === "cos") return Math.cos(cArgs[0] ?? 0);
                if (target === "math.floor" || target === "floor") return Math.floor(cArgs[0] ?? 0);
                if (target === "math.ceil" || target === "ceil") return Math.ceil(cArgs[0] ?? 0);
                if (target === "random.randint") {
                    const min = cArgs[0] ?? 0, max = cArgs[1] ?? 100;
                    return Math.floor(Math.random() * (max - min + 1)) + min;
                }
                if (target === "random.random") return Math.random();
                if (target === "datetime.datetime.now" || target === "datetime.now") return new Date().toISOString();
                if (target === "datetime.date.today" || target === "date.today") return new Date().toISOString().split("T")[0];
                if (target === "secrets.token_hex") return Array.from({length: (cArgs[0] || 8) * 2}, () => Math.floor(Math.random()*16).toString(16)).join("");
                this.stdout.push(`[PY_BRIDGE] Emulated call to '${target}' executed.`);
                return 0;
            }
            if (fnLower === "py_eval") {
                if (!args || args.length === 0) return null;
                const expr = String(args[0]);
                if (expr === "math.pi") return Math.PI;
                if (expr.includes("datetime.now().year") || expr.includes("year")) return new Date().getFullYear();
                try {
                    return Function(`"use strict"; return (${expr.replace(/math\./g, "Math.").replace(/sum\(/g, "([").replace(/\)/g, "].reduce((a,b)=>a+b,0))")})`)();
                } catch (e) {
                    return `[PY_EVAL] ${expr}`;
                }
            }

            // User function
            return this.callFunction(node.name, args);
        }

        if (node.type === "UnaryOp") {
            const val = this.evalExpr(node.operand);
            if (node.op === "-") return -val;
            if (node.op === "!") return !val;
            return val;
        }

        if (node.type === "BinaryOp") {
            const left = this.evalExpr(node.left);
            const right = this.evalExpr(node.right);
            const op = node.op;

            if (op === "+") {
                if (Array.isArray(left) && Array.isArray(right)) return left.concat(right);
                if (typeof left === "string" || typeof right === "string") return String(left) + String(right);
                return left + right;
            }
            if (op === "-") return left - right;
            if (op === "*") return left * right;
            if (op === "/") {
                if (right === 0) {
                    this.stdout.push("[WARNING] Division by zero detected; clamped to 0.");
                    return 0;
                }
                return left / right;
            }
            if (op === "%") return right !== 0 ? left % right : 0;
            if (op === "==") return left == right;
            if (op === "!=") return left != right;
            if (op === "<") return left < right;
            if (op === "<=") return left <= right;
            if (op === ">") return left > right;
            if (op === ">=") return left >= right;
            if (["&&", "and"].includes(op)) return Boolean(left) && Boolean(right);
            if (["||", "or"].includes(op)) return Boolean(left) || Boolean(right);
        }

        return 0;
    }

    callFunction(name, args) {
        if (!this.functions[name]) {
            this.stdout.push(`[ERROR] Undefined function '${name}' called.`);
            return 0;
        }
        if (this.callStack.length >= 100) {
            this.stdout.push("[STACK_OVERFLOW] Maximum recursion depth (100 frames) exceeded!");
            return 0;
        }

        const fnDef = this.functions[name];
        const frame = {};
        for (let i = 0; i < fnDef.params.length; i++) {
            frame[fnDef.params[i]] = args[i] ?? 0;
        }

        this.callStack.push(frame);
        this.returnTriggered = false;
        this.lastReturnValue = 0;

        for (const stmt of fnDef.body) {
            if (this.halted || this.returnTriggered) break;
            this.executeNode(stmt);
        }

        const ret = this.lastReturnValue;
        this.returnTriggered = false;
        this.callStack.pop();
        return ret;
    }

    executeNode(node) {
        if (this.halted || this.returnTriggered || !node) return;

        this.executionSteps++;
        this.tickAcmeTtls();

        if (node.type === "SetVar") {
            const val = this.evalExpr(node.expr);
            this.setVar(node.name, val);
        } else if (node.type === "CompoundAssign") {
            const curr = this.getVar(node.name);
            const operand = this.evalExpr(node.expr);
            if (node.op === "+=") this.setVar(node.name, (typeof curr === "string" || typeof operand === "string") ? String(curr) + String(operand) : curr + operand);
            else if (node.op === "-=") this.setVar(node.name, curr - operand);
            else if (node.op === "*=") this.setVar(node.name, curr * operand);
            else if (node.op === "/=") this.setVar(node.name, operand !== 0 ? curr / operand : 0);
        } else if (node.type === "IndexAssign") {
            const target = this.getVar(node.target);
            const idx = this.evalExpr(node.index);
            const val = this.evalExpr(node.value);
            if (target && typeof target === "object") {
                let curr = target[idx] ?? 0;
                if (node.op === "=") target[idx] = val;
                else if (node.op === "+=") target[idx] = curr + val;
                else if (node.op === "-=") target[idx] = curr - val;
                else if (node.op === "*=") target[idx] = curr * val;
                else if (node.op === "/=") target[idx] = val !== 0 ? curr / val : 0;
            }
        } else if (node.type === "TtlBox") {
            const val = this.evalExpr(node.expr);
            this.ttlMemory[node.name] = { value: val, ttl: node.ttl };
        } else if (node.type === "If") {
            if (this.evalExpr(node.condition)) {
                for (const s of node.thenBranch) this.executeNode(s);
            } else {
                for (const s of node.elseBranch) this.executeNode(s);
            }
        } else if (node.type === "While") {
            let count = 0;
            while (this.evalExpr(node.condition) && count < 5000 && !this.halted && !this.returnTriggered) {
                count++;
                for (const s of node.body) this.executeNode(s);
            }
        } else if (node.type === "ForIn") {
            const coll = this.evalExpr(node.collection);
            let items = [];
            if (Array.isArray(coll) || typeof coll === "string") items = Array.from(coll);
            else if (coll && typeof coll === "object") items = Object.keys(coll);

            for (const item of items) {
                if (this.halted || this.returnTriggered) break;
                this.setVar(node.itemName, item);
                for (const s of node.body) this.executeNode(s);
            }
        } else if (node.type === "FunctionDef") {
            this.functions[node.name] = node;
        } else if (node.type === "Return") {
            this.lastReturnValue = this.evalExpr(node.expr);
            this.returnTriggered = true;
        } else if (node.type === "ExpressionStatement") {
            this.evalExpr(node.expr);
        } else if (node.type === "Summon") {
            this.planeteerRings[node.ring.toUpperCase()] = node.body;
        } else if (node.type === "CallRing") {
            const r = node.ring.toUpperCase();
            if (this.planeteerRings[r]) {
                this.stdout.push(`[CAPTAIN_PLANET] (Ring: ${r}) Powers combined! Function activated.`);
                for (const s of this.planeteerRings[r]) this.executeNode(s);
            } else if (this.fallbackHandler) {
                this.stdout.push(`[TUXEDO_MASK] (Watchdog Fallback) Unbound ring '${r}' intercepted! 'My work here is done.'`);
                for (const s of this.fallbackHandler) this.executeNode(s);
            } else {
                this.stdout.push(`[CAPTAIN_PLANET] [WARNING] No matching ring '${r}' bound.`);
            }
        } else if (node.type === "Transform") {
            const val = this.evalExpr(node.expr);
            this.setVar(node.target, val);
            this.stdout.push(`[MPP] (Moon Prism Power Transformation) '${node.target}' evolved to '${val}'!`);
            for (const s of node.body) this.executeNode(s);
        } else if (node.type === "Fallback") {
            this.fallbackHandler = node.body;
        } else if (node.type === "Print") {
            this.stdout.push(String(this.evalExpr(node.expr)));
        } else if (node.type === "Import") {
            const path = node.path;
            if (this.importedModules.has(path)) return;
            const basename = path.replace(/^.*[\\/]/, "");
            const code = VIRTUAL_FS[path] || VIRTUAL_FS[basename];
            if (code) {
                this.importedModules.add(path);
                const subLexer = new SmcLexer(code);
                const subToks = subLexer.tokenize();
                const subParser = new SmcParser(subToks);
                const subAst = subParser.parse();
                this.run(subAst);
                this.stdout.push(`[IMPORT] Successfully loaded virtual module: ${basename}`);
            } else {
                this.stdout.push(`[IMPORT_ERROR] Cannot find module '${path}' in virtual file system.`);
            }
        } else if (node.type === "PyImport") {
            const alias = node.alias || node.module.split(".").pop();
            this.stdout.push(`[PY_BRIDGE] Successfully loaded Python module '${node.module}' as '${alias}'.`);
        } else if (node.type === "Halt") {
            this.halted = true;
            this.stdout.push("[THATS_ALL_FOLKS] [HALT] Program reached clean termination.");
        }
    }

    dispatchSimulatedRequest(method, path, body = "") {
        this.executionSteps++;
        this.tickAcmeTtls();

        const reqObj = {
            method: method.toUpperCase(),
            path: path,
            headers: { "user-agent": "SMC-Virtual-Browser/1.0" },
            body: body
        };

        const handlerName = this.serverHandler || "handle_request";
        if (this.functions[handlerName]) {
            const response = this.callFunction(handlerName, [reqObj]);
            if (response && typeof response === "object" && !Array.isArray(response)) {
                return {
                    status: response.status || 200,
                    contentType: response.content_type || "text/html; charset=utf-8",
                    body: response.body !== undefined ? response.body : ""
                };
            }
            return {
                status: 200,
                contentType: "text/html; charset=utf-8",
                body: String(response)
            };
        }

        return {
            status: 404,
            contentType: "text/html; charset=utf-8",
            body: `<h1>404 Not Found</h1><p>Handler '${handlerName}' not registered in experiment.</p>`
        };
    }

    run(program) {
        this.stdout.push(`[DEXTER_VM] [LAB_INIT] Initializing experiment '${program.name}'...`);
        for (const stmt of program.statements) {
            if (this.halted) break;
            this.executeNode(stmt);
        }
        return {
            name: program.name,
            steps: this.executionSteps,
            anvils: this.anvilsDropped,
            stdout: this.stdout,
            variables: { ...this.variables },
            ttlMemory: { ...this.ttlMemory },
            functions: Object.keys(this.functions)
        };
    }
}

// ---------------------------------------------------------------------------
// 5. CatDog Frame Slicer
// ---------------------------------------------------------------------------

function sliceCatDog(tokens) {
    const cat = [];
    const dog = [];
    const nonEof = tokens.slice(0, -1);
    for (let i = 0; i < nonEof.length; i++) {
        if (i % 2 === 0) cat.push(nonEof[i]);
        else dog.push(nonEof[i]);
    }
    const eof = tokens[tokens.length - 1];
    cat.push(eof);
    dog.push(eof);
    return { cat, dog };
}

// Export to global window for browser playground
window.SmcEngine = {
    SmcLexer,
    SmcParser,
    DexterVM,
    sliceCatDog
};
