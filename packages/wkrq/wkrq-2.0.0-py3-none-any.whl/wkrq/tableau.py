"""
wKrQ tableau construction engine.

Optimized tableau prover for wKrQ logic with industrial-grade performance.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .formula import (
    CompoundFormula,
    Constant,
    Formula,
    RestrictedUniversalFormula,
)
from .semantics import FALSE, TRUE, UNDEFINED, TruthValue
from .signs import Sign, SignedFormula, e, f, m, n, t


class RuleType(Enum):
    """Types of tableau rules for optimization."""

    ALPHA = "alpha"  # Non-branching rules (high priority)
    BETA = "beta"  # Branching rules (lower priority)


@dataclass
class RuleInfo:
    """Information about a tableau rule for optimization."""

    name: str
    rule_type: RuleType
    priority: int  # Lower numbers = higher priority
    complexity_cost: int  # Estimated computational cost
    conclusions: list[list[SignedFormula]]
    instantiation_constant: Optional[str] = None  # For universal quantifier tracking

    def __lt__(self, other: "RuleInfo") -> bool:
        """Compare rules for priority ordering."""
        # Alpha rules always come first
        if self.rule_type == RuleType.ALPHA and other.rule_type != RuleType.ALPHA:
            return True
        if self.rule_type != RuleType.ALPHA and other.rule_type == RuleType.ALPHA:
            return False

        # Then by explicit priority
        if self.priority != other.priority:
            return self.priority < other.priority

        # Finally by complexity cost
        return self.complexity_cost < other.complexity_cost


@dataclass
class TableauNode:
    """A node in the tableau tree."""

    id: int
    formula: SignedFormula
    parent: Optional["TableauNode"] = None
    children: list["TableauNode"] = field(default_factory=list)
    rule_applied: Optional[str] = None
    is_closed: bool = False
    closure_reason: Optional[str] = None
    depth: int = 0

    def add_child(self, child: "TableauNode", rule: Optional[str] = None) -> None:
        """Add a child node."""
        child.parent = self
        child.depth = self.depth + 1
        child.rule_applied = rule
        self.children.append(child)


@dataclass
class Branch:
    """A branch in the tableau with industrial-grade optimizations."""

    id: int
    nodes: list[TableauNode] = field(default_factory=list)
    formulas: set[SignedFormula] = field(default_factory=set)
    is_closed: bool = False
    closure_reason: Optional[str] = None

    # Optimization: index formulas by sign and formula for O(1) lookup
    formula_index: dict[Sign, dict[Formula, set[int]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(set))
    )

    # Constraint propagation: track unit literals and implications
    unit_literals: set[SignedFormula] = field(default_factory=set)
    implications: list[tuple[SignedFormula, SignedFormula]] = field(
        default_factory=list
    )

    # Performance metrics
    complexity_score: int = 0
    branching_factor: int = 0

    # Track processed formulas to avoid reprocessing
    _processed_formulas: set[SignedFormula] = field(default_factory=set)

    # Track ground terms (constants) for unification
    ground_terms: set[str] = field(default_factory=set)

    # Track universal quantifier instantiations: formula -> set of constants used
    _universal_instantiations: dict[SignedFormula, set[str]] = field(
        default_factory=dict
    )

    def add_formula(self, signed_formula: SignedFormula, node: TableauNode) -> bool:
        """Add a formula to the branch. Return True if branch closes."""
        # Skip if already exists (basic duplicate detection)
        if signed_formula in self.formulas:
            return False

        # Check for immediate contradiction (O(1) with indexing)
        if self._check_contradiction(signed_formula):
            self.is_closed = True
            self.closure_reason = f"{signed_formula} contradicts existing formula"
            return True

        # Add to branch structures
        self.formulas.add(signed_formula)
        self.nodes.append(node)
        self.formula_index[signed_formula.sign][signed_formula.formula].add(
            len(self.nodes) - 1
        )

        # Extract ground terms from the formula
        self._extract_ground_terms(signed_formula.formula)

        # Update complexity score for branch selection
        self.complexity_score += self._formula_complexity(signed_formula.formula)

        # Constraint propagation: detect unit literals
        if self._is_unit_literal(signed_formula):
            self.unit_literals.add(signed_formula)
            self._propagate_unit_literal(signed_formula)

        return False

    def _check_contradiction(self, new_formula: SignedFormula) -> bool:
        """Check if new formula contradicts existing formulas.

        Per Ferguson Definition 10: A branch closes if there is a sentence φ
        and distinct v, u ∈ V₃ such that both v : φ and u : φ appear on B.
        """
        # Check if formula already exists with a different sign from {t, f, e}
        for sign in [t, f, e]:
            if (
                sign != new_formula.sign
                and len(self.formula_index[sign][new_formula.formula]) > 0
            ):
                # Found same formula with different truth value - contradiction!
                return True
        return False

    def has_formula(self, signed_formula: SignedFormula) -> bool:
        """Check if branch already contains this signed formula."""
        return signed_formula in self.formulas

    def _formula_complexity(self, formula: Formula) -> int:
        """Calculate complexity score of a formula."""
        if formula.is_atomic():
            return 1
        return formula.complexity()

    def _is_unit_literal(self, signed_formula: SignedFormula) -> bool:
        """Check if this is a unit literal (atomic formula)."""
        return signed_formula.formula.is_atomic()

    def _propagate_unit_literal(self, unit_literal: SignedFormula) -> None:
        """Propagate constraints from unit literal."""
        # In a more sophisticated implementation, this would propagate
        # the literal through implications and update other formulas
        # For now, just track it for future optimization
        pass

    def _extract_ground_terms(self, formula: Formula) -> None:
        """Extract ground terms (constants) from a formula for unification."""
        from .formula import Constant, PredicateFormula

        if isinstance(formula, PredicateFormula):
            # Extract constants from predicate arguments
            for term in formula.terms:
                if isinstance(term, Constant):
                    self.ground_terms.add(term.name)
        elif isinstance(formula, CompoundFormula):
            # Recursively extract from subformulas
            for subformula in formula.subformulas:
                self._extract_ground_terms(subformula)
        elif hasattr(formula, "restriction") and hasattr(formula, "matrix"):
            # Handle restricted quantifiers
            self._extract_ground_terms(formula.restriction)
            self._extract_ground_terms(formula.matrix)

    def _find_best_instantiation_constant(self, variable_name: str) -> Optional[str]:
        """Find the best constant to instantiate a quantified variable with.

        Uses unification principles: prefer existing constants over fresh ones.
        """
        # First, try to find constants that appear in the restriction or matrix
        # This implements a simple form of unification for tableau theorem proving
        if self.ground_terms:
            # Return the first available ground term
            # In a more sophisticated implementation, we could rank these by relevance
            return next(iter(self.ground_terms))

        # If no ground terms available, we'll need to generate a fresh constant
        return None

    def _unify_with_existing_terms(self, formula: Formula) -> dict[str, str]:
        """Attempt to unify quantified variables with existing ground terms.

        This is a simplified unification that looks for opportunities to use
        existing constants instead of always generating fresh ones.
        """
        from .formula import RestrictedQuantifierFormula

        unification_map = {}

        if isinstance(formula, RestrictedQuantifierFormula):
            var_name = formula.var.name
            best_constant = self._find_best_instantiation_constant(var_name)
            if best_constant:
                unification_map[var_name] = best_constant

        return unification_map


@dataclass
class Model:
    """A model extracted from an open branch."""

    valuations: dict[str, TruthValue]
    constants: dict[str, set[Formula]]  # For first-order models

    def __str__(self) -> str:
        val_str = ", ".join(f"{k}={v}" for k, v in sorted(self.valuations.items()))
        if self.constants:
            const_str = "; ".join(
                f"{c}: {', '.join(str(f) for f in fs)}"
                for c, fs in sorted(self.constants.items())
            )
            return f"{{valuations: {{{val_str}}}, constants: {{{const_str}}}}}"
        return f"{{{val_str}}}"


@dataclass
class TableauResult:
    """Result of tableau construction."""

    satisfiable: bool
    models: list[Model]
    closed_branches: int
    open_branches: int
    total_nodes: int
    tableau: Optional["Tableau"] = None

    @property
    def valid(self) -> bool:
        """Check if the original formula is valid (no countermodels)."""
        return not self.satisfiable


class Tableau:
    """Industrial-grade optimized tableau for wKrQ logic."""

    def __init__(self, initial_formulas: list[SignedFormula]):
        if not initial_formulas:
            raise ValueError("Cannot create tableau with empty formula list")
        self.root = TableauNode(0, initial_formulas[0])
        self.nodes: list[TableauNode] = [self.root]
        self.branches: list[Branch] = []
        self.open_branches: list[Branch] = []
        self.closed_branches: list[Branch] = []
        self.node_counter = 1
        self.constants: set[str] = set()  # Track introduced constants

        # Performance optimization settings
        self.max_branching_factor = 1000  # Prevent exponential explosion
        self.max_tableau_depth = 100  # Prevent infinite loops
        self.early_termination = True  # Stop on first satisfying model

        # Advanced optimization state
        self.global_processed_formulas: set[SignedFormula] = set()
        self.branch_selection_strategy = (
            "least_complex"  # "least_complex", "depth_first", "breadth_first"
        )
        self.rule_application_stats: dict[str, int] = defaultdict(int)

        # Initialize with first branch
        initial_branch = self._create_branch(0)
        self.branches.append(initial_branch)
        self.open_branches.append(initial_branch)

        # Add initial formulas to root and branch
        for i, sf in enumerate(initial_formulas):
            if i == 0:
                # First formula goes to root
                self.root.formula = sf
                initial_branch.add_formula(sf, self.root)
            else:
                # Additional formulas as children of root
                node = TableauNode(self.node_counter, sf)
                self.node_counter += 1
                self.nodes.append(node)
                self.root.add_child(node)

                if initial_branch.add_formula(sf, node):
                    self.open_branches.remove(initial_branch)
                    self.closed_branches.append(initial_branch)
                    break

        # Update global constants from all initial ground terms
        for branch in self.branches:
            self.constants.update(branch.ground_terms)

    def _create_branch(self, branch_id: int) -> Branch:
        """Factory method for creating branches. Can be overridden by subclasses."""
        return Branch(branch_id)

    def is_complete(self) -> bool:
        """Check if tableau construction is complete."""
        return len(self.open_branches) == 0 or all(
            self._branch_is_complete(branch) for branch in self.open_branches
        )

    def _branch_is_complete(self, branch: Branch) -> bool:
        """Check if all possible rules have been applied to a branch."""
        for node in branch.nodes:
            if self._get_applicable_rule(node.formula, branch) is not None:
                return False
        return True

    def _get_applicable_rule(
        self, signed_formula: SignedFormula, branch: Branch
    ) -> Optional[RuleInfo]:
        """Get the next applicable rule for a signed formula using Ferguson's system."""
        from .ferguson_rules import get_applicable_rule as get_ferguson_rule

        # Check if already processed (except for universal quantifiers)
        if hasattr(branch, "_processed_formulas"):
            if signed_formula in branch._processed_formulas:
                # Allow re-processing of universal quantifiers for new constants
                if not (
                    isinstance(signed_formula.formula, RestrictedUniversalFormula)
                    and signed_formula.sign == t
                ):
                    return None
        else:
            branch._processed_formulas = set()

        # Create a fresh constant generator
        def fresh_constant_generator() -> Constant:
            return Constant(f"c_{len(branch.nodes)}")

        # Get used constants for this formula if it's a universal quantifier
        used_constants = None
        if isinstance(signed_formula.formula, RestrictedUniversalFormula):
            if hasattr(branch, "_universal_instantiations"):
                used_constants = branch._universal_instantiations.get(
                    signed_formula, set()
                )
            else:
                branch._universal_instantiations = {}
                used_constants = set()

        # Get Ferguson rule
        ferguson_rule = get_ferguson_rule(
            signed_formula,
            fresh_constant_generator,
            list(branch.ground_terms) if branch.ground_terms else None,
            used_constants,
        )

        if not ferguson_rule:
            return None

        # Convert Ferguson rule to RuleInfo
        rule_type = (
            RuleType.ALPHA if not ferguson_rule.is_branching() else RuleType.BETA
        )
        priority = 1 if rule_type == RuleType.ALPHA else 10

        return RuleInfo(
            name=ferguson_rule.name,
            rule_type=rule_type,
            priority=priority,
            complexity_cost=len(ferguson_rule.conclusions),
            conclusions=ferguson_rule.conclusions,
            instantiation_constant=ferguson_rule.instantiation_constant,
        )

    def apply_rule(  # noqa: C901
        self, node: TableauNode, branch: Branch, rule_info: RuleInfo
    ) -> None:
        """Apply a tableau rule with optimization, creating new branches if needed."""

        # Mark the formula as processed (except for universal quantifiers which can be reprocessed)
        if not hasattr(branch, "_processed_formulas"):
            branch._processed_formulas = set()

        # For universal quantifiers, mark the instantiation as used instead of marking formula as processed
        if (
            hasattr(rule_info, "instantiation_constant")
            and rule_info.instantiation_constant is not None
        ):
            # This is a universal quantifier instantiation
            if not hasattr(branch, "_universal_instantiations"):
                branch._universal_instantiations = {}
            if node.formula not in branch._universal_instantiations:
                branch._universal_instantiations[node.formula] = set()
            branch._universal_instantiations[node.formula].add(
                rule_info.instantiation_constant
            )
        else:
            # Regular formula processing
            branch._processed_formulas.add(node.formula)

        # Update statistics
        self.rule_application_stats[rule_info.name] += 1

        conclusions = rule_info.conclusions

        if len(conclusions) == 1:
            # Non-branching rule (alpha rule)
            for signed_formula in conclusions[0]:
                if not branch.has_formula(signed_formula):
                    new_node = TableauNode(self.node_counter, signed_formula)
                    self.node_counter += 1
                    self.nodes.append(new_node)
                    node.add_child(new_node, rule_info.name)

                    if branch.add_formula(signed_formula, new_node):
                        # Branch closed
                        if branch in self.open_branches:
                            self.open_branches.remove(branch)
                            self.closed_branches.append(branch)
                        return
        else:
            # Branching rule (beta rule)
            # Remove current branch from open branches
            if branch in self.open_branches:
                self.open_branches.remove(branch)

            parent_node = node
            for _i, conclusion_set in enumerate(conclusions):
                # Create new branch
                new_branch = self._create_branch(len(self.branches))
                self.branches.append(new_branch)

                # Copy existing formulas to new branch
                for existing_node in branch.nodes:
                    new_branch.add_formula(existing_node.formula, existing_node)

                # Copy ground terms from parent branch
                new_branch.ground_terms = branch.ground_terms.copy()

                # Copy universal instantiation tracking
                new_branch._universal_instantiations = {
                    sf: constants.copy()
                    for sf, constants in branch._universal_instantiations.items()
                }

                # Copy processed formulas to avoid reprocessing
                if hasattr(branch, "_processed_formulas"):
                    new_branch._processed_formulas = branch._processed_formulas.copy()
                else:
                    new_branch._processed_formulas = set()

                # Add new formulas
                branch_closed = False
                for signed_formula in conclusion_set:
                    if not new_branch.has_formula(signed_formula):
                        new_node = TableauNode(self.node_counter, signed_formula)
                        self.node_counter += 1
                        self.nodes.append(new_node)
                        parent_node.add_child(new_node, rule_info.name)

                        if new_branch.add_formula(signed_formula, new_node):
                            branch_closed = True
                            break

                if branch_closed:
                    self.closed_branches.append(new_branch)
                else:
                    self.open_branches.append(new_branch)

    def construct(self) -> TableauResult:
        """Construct the tableau with industrial-grade optimizations."""
        max_iterations = 1000  # Increased for complex formulas
        iteration = 0

        while (
            self.open_branches
            and not self.is_complete()
            and iteration < max_iterations
            and len(self.branches) < self.max_branching_factor
        ):

            iteration += 1

            # Advanced branch selection strategy
            selected_branch = self._select_optimal_branch()
            if not selected_branch:
                break

            # Get all applicable rules for this branch and prioritize them
            applicable_rules = self._get_prioritized_rules(selected_branch)
            if not applicable_rules:
                # No more rules can be applied to any branch
                break

            # Apply the highest priority rule
            best_rule = applicable_rules[0]  # Already sorted by priority
            node, rule_info = best_rule

            self.apply_rule(node, selected_branch, rule_info)

            # Early termination for satisfiability (first model found)
            if self.early_termination and len(self.open_branches) > 0:
                # Check if any branch is ready for model extraction (all atomic)
                for branch in self.open_branches:
                    if all(node.formula.formula.is_atomic() for node in branch.nodes):
                        break

        # Extract models from open branches
        models = []
        for branch in self.open_branches:
            if not branch.is_closed:
                model = self._extract_model(branch)
                if model:
                    models.append(model)

        return TableauResult(
            satisfiable=len(models) > 0,
            models=models,
            closed_branches=len(self.closed_branches),
            open_branches=len(self.open_branches),
            total_nodes=len(self.nodes),
            tableau=self,
        )

    def _extract_model(self, branch: Branch) -> Optional[Model]:
        """Extract a model from an open branch."""
        # Get all atoms
        atoms: set[str] = set()
        for node in branch.nodes:
            atoms.update(node.formula.formula.get_atoms())

        # Build valuation
        valuations = {}

        for atom in atoms:
            # Check what signs appear for this atom
            has_t = any(
                node.formula.sign == t and str(node.formula.formula) == atom
                for node in branch.nodes
            )
            has_f = any(
                node.formula.sign == f and str(node.formula.formula) == atom
                for node in branch.nodes
            )
            has_e = any(
                node.formula.sign == e and str(node.formula.formula) == atom
                for node in branch.nodes
            )
            has_m = any(
                node.formula.sign == m and str(node.formula.formula) == atom
                for node in branch.nodes
            )
            has_n = any(
                node.formula.sign == n and str(node.formula.formula) == atom
                for node in branch.nodes
            )

            # Direct truth value signs take precedence
            if has_t:
                valuations[atom] = TRUE
            elif has_f:
                valuations[atom] = FALSE
            elif has_e:
                valuations[atom] = UNDEFINED
            elif has_m:
                # m means both t and f are possible - choose one
                valuations[atom] = TRUE  # Could also be FALSE
            elif has_n:
                # n means both f and e are possible - choose f
                valuations[atom] = FALSE  # Could also be UNDEFINED
            else:
                # No constraint, default to undefined
                valuations[atom] = UNDEFINED

        return Model(valuations, {})

    def _select_optimal_branch(self) -> Optional[Branch]:
        """Select the optimal branch to process next."""
        if not self.open_branches:
            return None

        if self.branch_selection_strategy == "least_complex":
            # Select branch with lowest complexity score
            return min(self.open_branches, key=lambda b: b.complexity_score)
        elif self.branch_selection_strategy == "depth_first":
            # Select most recently created branch
            return self.open_branches[-1]
        elif self.branch_selection_strategy == "breadth_first":
            # Select oldest branch
            return self.open_branches[0]
        else:
            # Default: least complex
            return min(self.open_branches, key=lambda b: b.complexity_score)

    def _get_prioritized_rules(
        self, branch: Branch
    ) -> list[tuple[TableauNode, RuleInfo]]:
        """Get all applicable rules for a branch, sorted by priority."""
        applicable_rules = []

        for node in branch.nodes:
            rule_info = self._get_applicable_rule(node.formula, branch)
            if rule_info:
                applicable_rules.append((node, rule_info))

        # Sort by rule priority (RuleInfo.__lt__ handles the logic)
        applicable_rules.sort(key=lambda x: x[1])

        return applicable_rules

    def _try_extract_model(self, branch: Branch) -> Optional[Model]:
        """Try to extract a model from a branch (non-destructive)."""
        try:
            return self._extract_model(branch)
        except Exception:
            return None


def solve(formula: Formula, sign: Sign = t) -> TableauResult:
    """Solve a formula with the given sign."""
    signed_formula = SignedFormula(sign, formula)
    tableau = Tableau([signed_formula])
    return tableau.construct()


def valid(formula: Formula) -> bool:
    """Check if a formula is valid (true in all models).

    In weak Kleene logic, validity means the formula receives value 't'
    in ALL interpretations, not just those where premises are true.

    A formula is valid iff:
    - f:φ is unsatisfiable (cannot be false), AND
    - e:φ is unsatisfiable (cannot be undefined)
    """
    # Check if formula can be false
    result_f = solve(formula, f)
    if result_f.satisfiable:
        return False  # Can be false, so not valid

    # Check if formula can be undefined
    result_e = solve(formula, e)
    if result_e.satisfiable:
        return False  # Can be undefined, so not valid

    # If cannot be false or undefined, must be valid (always true)
    return True


def entails(premises: list[Formula], conclusion: Formula) -> bool:
    """Check if premises entail conclusion."""
    # P1, ..., Pn |- Q iff (P1 & ... & Pn & ~Q) is unsatisfiable
    from .formula import Conjunction, Negation

    if not premises:
        # Empty premises, check if conclusion is valid
        return valid(conclusion)

    # Combine premises
    combined_premises = premises[0]
    for p in premises[1:]:
        combined_premises = Conjunction(combined_premises, p)

    # Test satisfiability of premises & ~conclusion
    test_formula = Conjunction(combined_premises, Negation(conclusion))
    result = solve(test_formula, t)

    return not result.satisfiable
