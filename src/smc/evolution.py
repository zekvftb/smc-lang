"""Genetic Programming (GP) & AST Evolution Subsystem for the SMC Language.

Utilizes SMC's native mutate, slip, and attenuator primitives to evolve AST programs
toward user-defined objective fitness functions with 100% deterministic reproducibility.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any, Callable

from smc.compiler import BytecodeCompiler
from smc.lexer import SmcLexer
from smc.parser import (
    AstNode,
    BinaryOpNode,
    ExpressionStatementNode,
    LiteralNode,
    PrintNode,
    ProgramNode,
    SetVarNode,
    SlipNode,
    SmcParser,
    VariableNode,
)
from smc.vm import DexterVM


@dataclass
class Individual:
    """An evolved SMC individual with source code, AST, and evaluated fitness."""

    source_code: str
    ast: ProgramNode
    fitness: float = -float("inf")
    generation: int = 0


class GeneticOptimizer:
    """Deterministic Genetic Programming Engine for SMC programs."""

    def __init__(
        self,
        population_size: int = 20,
        mutation_rate: float = 0.3,
        crossover_rate: float = 0.5,
        tournament_size: int = 3,
        seed: int = 42,
    ) -> None:
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_size = tournament_size
        self.rng = random.Random(seed)
        self.population: list[Individual] = []
        self.best_individual: Individual | None = None
        self.history: list[dict[str, Any]] = []

    def _generate_random_expression(self, depth: int = 0) -> AstNode:
        """Generate a random arithmetic expression AST."""
        if depth >= 2 or self.rng.random() < 0.4:
            if self.rng.random() < 0.5:
                return LiteralNode(value=self.rng.randint(1, 10))
            return VariableNode(name="x")

        op = self.rng.choice(["+", "-", "*"])
        left = self._generate_random_expression(depth + 1)
        right = self._generate_random_expression(depth + 1)
        return BinaryOpNode(left=left, op=op, right=right)

    def _generate_random_statement(self) -> AstNode:
        """Generate a random AST statement."""
        r = self.rng.random()
        if r < 0.6:
            # y = expr
            expr = self._generate_random_expression()
            return SetVarNode(name="y", expr=expr)
        if r < 0.8:
            # slip(+1) or slip(-1)
            offset = self.rng.choice([1, 2])
            return SlipNode(by_expr=LiteralNode(value=offset))
        # print y
        return PrintNode(expr=VariableNode(name="y"))

    def generate_random_individual(self) -> Individual:
        """Create a randomized valid SMC Program AST and source string."""
        n_stmts = self.rng.randint(2, 4)
        stmts = [self._generate_random_statement() for _ in range(n_stmts)]
        
        # Ensure at least one output assignment
        stmts.append(SetVarNode(name="result", expr=self._generate_random_expression()))

        prog = ProgramNode(name="evolved_program", statements=stmts)
        source = self.ast_to_source(prog)
        return Individual(source_code=source, ast=prog)

    def ast_to_source(self, prog: ProgramNode) -> str:
        """Render an AST Program back to clean SMC source syntax."""
        lines = [f"experiment '{prog.name}' {{"]
        for s in prog.statements:
            if isinstance(s, SetVarNode):
                lines.append(f"    let {s.name} = {self._expr_to_source(s.expr)}")
            elif isinstance(s, SlipNode):
                lines.append(f"    slip({self._expr_to_source(s.by_expr)})")
            elif isinstance(s, PrintNode):
                lines.append(f"    print {self._expr_to_source(s.expr)}")
        lines.append("}")
        return "\n".join(lines)

    def _expr_to_source(self, expr: AstNode) -> str:
        """Render expression node to string."""
        if isinstance(expr, LiteralNode):
            return str(expr.value)
        if isinstance(expr, VariableNode):
            return expr.name
        if isinstance(expr, BinaryOpNode):
            return f"({self._expr_to_source(expr.left)} {expr.op} {self._expr_to_source(expr.right)})"
        return "0"

    def mutate_individual(self, ind: Individual) -> Individual:
        """Apply deterministic stochastic mutations to an individual's AST."""
        # Deep clone statements by re-parsing source
        try:
            tokens = SmcLexer(ind.source_code).tokenize()
            cloned_ast = SmcParser(tokens).parse()
        except Exception:
            return ind

        new_stmts = list(cloned_ast.statements)
        if not new_stmts:
            return ind

        idx = self.rng.randint(0, len(new_stmts) - 1)
        target_stmt = new_stmts[idx]

        if isinstance(target_stmt, SetVarNode):
            # Mutate the expression
            new_stmts[idx] = SetVarNode(name=target_stmt.name, expr=self._generate_random_expression())
        elif isinstance(target_stmt, SlipNode):
            # Flip slip offset
            new_stmts[idx] = SlipNode(by_expr=LiteralNode(value=1 if target_stmt.by_expr != 1 else 2))
        else:
            # Insert a new statement
            new_stmts.append(self._generate_random_statement())

        new_prog = ProgramNode(name="mutated_ind", statements=new_stmts)
        new_src = self.ast_to_source(new_prog)
        return Individual(source_code=new_src, ast=new_prog)

    def evaluate_fitness(
        self,
        ind: Individual,
        fitness_fn: Callable[[dict[str, Any]], float],
    ) -> float:
        """Execute individual in DexterVM and compute objective fitness score."""
        try:
            tokens = SmcLexer(ind.source_code).tokenize()
            ast = SmcParser(tokens).parse()
            vm = DexterVM()
            res = vm.run(ast)
            score = fitness_fn(res["final_variables"])
        except Exception:
            score = -1000.0

        ind.fitness = score
        return score

    def tournament_selection(self) -> Individual:
        """Select best individual from random tournament sample."""
        candidates = self.rng.sample(self.population, min(self.tournament_size, len(self.population)))
        return max(candidates, key=lambda ind: ind.fitness)

    def evolve(
        self,
        generations: int,
        fitness_fn: Callable[[dict[str, Any]], float],
    ) -> Individual:
        """Run evolutionary generations and return highest-fitness individual."""
        # Initialize population
        self.population = [self.generate_random_individual() for _ in range(self.population_size)]

        for gen in range(generations):
            # Evaluate all individuals
            for ind in self.population:
                self.evaluate_fitness(ind, fitness_fn)
                ind.generation = gen

            # Sort by fitness descending
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            current_best = self.population[0]

            if self.best_individual is None or current_best.fitness > self.best_individual.fitness:
                self.best_individual = current_best

            avg_fitness = sum(x.fitness for x in self.population) / len(self.population)
            self.history.append({
                "generation": gen,
                "best_fitness": current_best.fitness,
                "avg_fitness": round(avg_fitness, 3),
                "best_source": current_best.source_code,
            })

            # Next generation with elitism (keep top 2)
            next_pop = [self.population[0], self.population[1]]

            while len(next_pop) < self.population_size:
                parent = self.tournament_selection()
                if self.rng.random() < self.mutation_rate:
                    child = self.mutate_individual(parent)
                else:
                    child = Individual(source_code=parent.source_code, ast=parent.ast)
                next_pop.append(child)

            self.population = next_pop

        return self.best_individual or self.population[0]
