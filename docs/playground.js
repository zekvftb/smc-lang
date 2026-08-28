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
    HALT: ["HALT", "EXIT", "THATS_ALL_FOLKS", "COWABUNGA", "FIN"]
};

const KEYWORD_TO_OPCODE = {};
for (const [op, syns] of Object.entries(OPCODE_SYNONYMS)) {
    for (const syn of syns) {
        KEYWORD_TO_OPCODE[syn.toUpperCase()] = op;
    }
}

const BUILTIN_NAMES = new Set(["LEN", "PUSH", "POP", "STR", "INT", "TYPE"]);

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
                const op = resolveWobbleOpcode(ident);
                if (op) {
                    tokens.push({ type: "KEYWORD", value: ident, opcode: op, line: startLine, col: startCol });
                } else {
                    tokens.push({ type: "IDENTIFIER", value: ident, line: startLine, col: startCol });
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
        return this.parseEquality();
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

        // Identifiers (Variable, Function Call, or Index)
        if (tok.type === "IDENTIFIER") {
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
                return typeof val;
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
        } else if (node.type === "Halt") {
            this.halted = true;
            this.stdout.push("[THATS_ALL_FOLKS] [HALT] Program reached clean termination.");
        }
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
