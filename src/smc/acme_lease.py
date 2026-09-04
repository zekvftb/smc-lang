"""Context-Weighted Ephemeral Leasing Module for SMC-Lang Runtime.

Enhances Acme Ephemeral Memory with context priority tiers (Optimal, Strong, Weak),
dynamic memory pressure eviction, TTL decay management, and leak-free resource lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Optional


class ContextPriority(str, Enum):
    OPTIMAL = "Optimal"
    STRONG = "Strong"
    WEAK = "Weak"

    @property
    def weight(self) -> float:
        if self == ContextPriority.OPTIMAL:
            return 3.0
        elif self == ContextPriority.STRONG:
            return 2.0
        else:
            return 1.0


@dataclass
class ContextLeaseItem:
    """An ephemeral variable bound with context priority and Acme TTL countdown."""

    name: str
    value: Any
    ttl: int
    initial_ttl: int
    priority: ContextPriority = ContextPriority.STRONG
    created_step: int = 0

    @property
    def weight(self) -> float:
        return self.priority.weight

    @property
    def retention_score(self) -> float:
        """Score determines eviction ordering under memory pressure (lower score evicts first)."""
        return self.ttl * self.weight


class AcmeLeaseManager:
    """Manages context-weighted ephemeral variable leasing and pressure eviction."""

    def __init__(self, max_capacity: int = 128) -> None:
        self.max_capacity = max_capacity
        self.leases: dict[str, ContextLeaseItem] = {}
        self.evictions_under_pressure: int = 0
        self.natural_expirations: int = 0
        self.current_step: int = 0

    def allocate(
        self,
        name: str,
        value: Any,
        ttl: int,
        priority: str | ContextPriority = ContextPriority.STRONG,
    ) -> ContextLeaseItem:
        """Allocate an ephemeral lease with specified context priority."""
        if isinstance(priority, str):
            p_upper = priority.capitalize()
            if p_upper == "Optimal":
                p_enum = ContextPriority.OPTIMAL
            elif p_upper == "Weak":
                p_enum = ContextPriority.WEAK
            else:
                p_enum = ContextPriority.STRONG
        else:
            p_enum = priority

        ttl_clean = max(1, int(ttl))

        # Check memory pressure before allocation
        if len(self.leases) >= self.max_capacity and name not in self.leases:
            self._evict_lowest_priority()

        item = ContextLeaseItem(
            name=name,
            value=value,
            ttl=ttl_clean,
            initial_ttl=ttl_clean,
            priority=p_enum,
            created_step=self.current_step,
        )
        self.leases[name] = item
        return item

    def _evict_lowest_priority(self) -> Optional[str]:
        """Evict the item with the lowest retention score under memory pressure."""
        if not self.leases:
            return None

        lowest_name = min(self.leases, key=lambda k: self.leases[k].retention_score)
        del self.leases[lowest_name]
        self.evictions_under_pressure += 1
        return lowest_name

    def tick_step(self) -> list[str]:
        """Tick down all active leases by 1 unit. Returns list of expired variable names."""
        self.current_step += 1
        expired = []
        for name, item in list(self.leases.items()):
            item.ttl -= 1
            if item.ttl <= 0:
                expired.append(name)
                del self.leases[name]
                self.natural_expirations += 1
        return expired

    def get(self, name: str) -> Optional[Any]:
        """Retrieve value of active lease, or None if expired/unbound."""
        item = self.leases.get(name)
        return item.value if item is not None else None

    def has(self, name: str) -> bool:
        """Check if lease is currently active."""
        return name in self.leases

    def clear(self) -> None:
        """Clear all active leases."""
        self.leases.clear()

    def stats(self) -> dict[str, Any]:
        """Summary statistics of ephemeral memory manager."""
        return {
            "active_leases": len(self.leases),
            "max_capacity": self.max_capacity,
            "natural_expirations": self.natural_expirations,
            "pressure_evictions": self.evictions_under_pressure,
            "current_step": self.current_step,
        }
