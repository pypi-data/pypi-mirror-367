"""
ACrQ-specific tableau implementation with bilateral predicate support.

This module extends the standard wKrQ tableau to handle bilateral predicates
according to Ferguson's ACrQ system.
"""

from dataclasses import dataclass, field
from typing import Optional

from .acrq_ferguson_rules import get_acrq_rule
from .formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Formula,
    PredicateFormula,
    RestrictedUniversalFormula,
)
from .semantics import FALSE, BilateralTruthValue, TruthValue
from .signs import Sign, SignedFormula, e, f, t
from .tableau import Branch, Model, RuleInfo, RuleType, Tableau


class ACrQBranch(Branch):
    """Branch for ACrQ tableau with paraconsistent contradiction detection."""

    def __init__(self, branch_id: int):
        """Initialize ACrQ branch."""
        super().__init__(branch_id)
        self.bilateral_pairs: dict[str, str] = {}  # Maps R to R*

    def _check_contradiction(self, new_formula: SignedFormula) -> bool:
        """Check for contradictions per Ferguson's Lemma 5.

        A branch closes in ACrQ when:
        1. Standard contradiction: u:φ and v:φ appear for distinct u,v ∈ {t,f,e}
        2. But NOT when t:R(a) and t:R*(a) appear (this is a glut, allowed)

        The key insight from Lemma 5 is that φ* = ψ* ensures they share a
        common primary logical operator, preventing closure in glut cases.
        """
        formula = new_formula.formula
        sign = new_formula.sign

        # Check standard contradictions (distinct signs from {t,f,e})
        for other_sign in [t, f, e]:
            if other_sign != sign and len(self.formula_index[other_sign][formula]) > 0:
                # Check if this is a bilateral predicate glut case
                if sign == t and other_sign == t:
                    # Both are t - check if they form a glut (R and R*)
                    if self._is_bilateral_glut(formula, sign):
                        # This is allowed in ACrQ - don't close
                        return False
                # Standard contradiction - close branch
                return True

        return False

    def _is_bilateral_glut(self, formula: Formula, sign: Sign) -> bool:
        """Check if this formula forms a bilateral glut with existing formulas.

        Returns True if we have both t:R(a) and t:R*(a) which is allowed.
        """
        if not isinstance(formula, PredicateFormula) and not isinstance(
            formula, BilateralPredicateFormula
        ):
            return False

        # Get the base name and check for its dual
        if isinstance(formula, BilateralPredicateFormula):
            base_name = formula.get_base_name()
            is_negative = formula.is_negative
        else:
            # Regular predicate
            if formula.predicate_name.endswith("*"):
                base_name = formula.predicate_name[:-1]
                is_negative = True
            else:
                base_name = formula.predicate_name
                is_negative = False

        # Look for the dual predicate with same sign
        for node_id in self.formula_index[sign][formula]:
            # Get the actual signed formula from the node
            node = self.nodes[node_id]
            other = node.formula.formula
            if isinstance(other, PredicateFormula) or isinstance(
                other, BilateralPredicateFormula
            ):
                # Check if it's the dual
                if isinstance(other, BilateralPredicateFormula):
                    other_base = other.get_base_name()
                    other_negative = other.is_negative
                else:
                    if other.predicate_name.endswith("*"):
                        other_base = other.predicate_name[:-1]
                        other_negative = True
                    else:
                        other_base = other.predicate_name
                        other_negative = False

                # If same base name but different polarity, it's a glut
                if base_name == other_base and is_negative != other_negative:
                    # Check that arguments match
                    if str(formula.terms) == str(other.terms):
                        return True

        return False


@dataclass
class ACrQModel(Model):
    """Model for ACrQ with bilateral predicate support."""

    bilateral_valuations: dict[str, BilateralTruthValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize bilateral valuations from standard valuations."""
        super().__init__(self.valuations, self.constants)
        self.bilateral_valuations = {}

        # Group predicates by base name
        bilateral_predicates: dict[str, dict[str, dict[str, TruthValue]]] = {}

        for atom_str, value in self.valuations.items():
            # Skip propositional atoms
            if "(" not in atom_str:
                continue

            # Extract predicate name and arguments
            pred_name = atom_str.split("(")[0]
            args = "(" + atom_str.split("(", 1)[1]

            # Determine base name
            if pred_name.endswith("*"):
                base_name = pred_name[:-1]
                is_negative = True
            else:
                base_name = pred_name
                is_negative = False

            # Initialize structure if needed
            if base_name not in bilateral_predicates:
                bilateral_predicates[base_name] = {}

            key = f"{base_name}{args}"
            if key not in bilateral_predicates[base_name]:
                bilateral_predicates[base_name][key] = {
                    "positive": FALSE,
                    "negative": FALSE,
                }

            # Set the appropriate value
            if is_negative:
                bilateral_predicates[base_name][key]["negative"] = value
            else:
                bilateral_predicates[base_name][key]["positive"] = value

        # Create bilateral truth values
        for _base_name, pred_instances in bilateral_predicates.items():
            for key, values in pred_instances.items():
                btv = BilateralTruthValue(
                    positive=values["positive"], negative=values["negative"]
                )
                self.bilateral_valuations[key] = btv


class ACrQTableau(Tableau):
    """Extended tableau for ACrQ with bilateral predicate support."""

    def __init__(self, initial_formulas: list[SignedFormula]) -> None:
        """Initialize ACrQ tableau with bilateral predicate tracking."""
        self.bilateral_pairs: dict[str, str] = (
            {}
        )  # Maps R to R* - Initialize before super()
        super().__init__(initial_formulas)
        self.logic_system = "ACrQ"
        self._constant_counter = 0  # Initialize counter for fresh constants

        # Identify bilateral predicates in initial formulas
        self._identify_bilateral_predicates(initial_formulas)

    def _identify_bilateral_predicates(self, formulas: list[SignedFormula]) -> None:
        """Identify and register bilateral predicate pairs."""
        for sf in formulas:
            self._extract_bilateral_pairs(sf.formula)

    def _extract_bilateral_pairs(self, formula: Formula) -> None:
        """Extract bilateral predicate pairs from a formula."""
        if isinstance(formula, BilateralPredicateFormula):
            # Register both R -> R* and R* -> R mappings
            pos_name = formula.positive_name
            neg_name = f"{formula.positive_name}*"
            self.bilateral_pairs[pos_name] = neg_name
            self.bilateral_pairs[neg_name] = pos_name

        elif isinstance(formula, CompoundFormula):
            for sub in formula.subformulas:
                self._extract_bilateral_pairs(sub)

        elif hasattr(formula, "restriction") and hasattr(formula, "matrix"):
            # Handle quantified formulas
            self._extract_bilateral_pairs(formula.restriction)
            self._extract_bilateral_pairs(formula.matrix)

    def _create_branch(self, branch_id: int) -> ACrQBranch:
        """Create an ACrQ branch with paraconsistent contradiction detection."""
        branch = ACrQBranch(branch_id)
        branch.bilateral_pairs = self.bilateral_pairs.copy()
        return branch

    def _get_applicable_rule(
        self, signed_formula: SignedFormula, branch: Branch
    ) -> Optional[RuleInfo]:
        """Get applicable rule using ACrQ Ferguson rules from Definition 18."""
        # Use ACrQ-specific Ferguson rules which:
        # 1. Drop the general negation elimination rule
        # 2. Handle bilateral predicates specially
        # 3. Keep all other wKrQ rules

        # Get the ACrQ rule from our Ferguson rules module
        from .formula import Constant

        def fresh_constant_generator() -> Constant:
            """Generate fresh constants for quantifier instantiation."""
            self._constant_counter += 1
            return Constant(f"c_{self._constant_counter}")

        # Get existing constants from branch
        existing_constants = list(branch.ground_terms) if branch.ground_terms else []

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

        ferguson_rule = get_acrq_rule(
            signed_formula, fresh_constant_generator, existing_constants, used_constants
        )

        if ferguson_rule:
            # Convert FergusonRule to RuleInfo
            rule_type = (
                RuleType.BETA if ferguson_rule.is_branching() else RuleType.ALPHA
            )
            priority = 10 if rule_type == RuleType.ALPHA else 20

            return RuleInfo(
                name=ferguson_rule.name,
                rule_type=rule_type,
                priority=priority,
                complexity_cost=len(ferguson_rule.conclusions),
                conclusions=ferguson_rule.conclusions,
                instantiation_constant=ferguson_rule.instantiation_constant,
            )

        # If no ACrQ rule applies, the formula might be atomic
        return None

    def _extract_model(self, branch: Branch) -> Optional[ACrQModel]:
        """Extract an ACrQ model from an open branch."""
        # Use base class to get standard model
        base_model = super()._extract_model(branch)

        if base_model is None:
            return None

        # Create ACrQ model with bilateral valuations
        acrq_model = ACrQModel(
            valuations=base_model.valuations, constants=base_model.constants
        )

        return acrq_model
