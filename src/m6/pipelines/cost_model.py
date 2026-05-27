"""Per-provider €/1M-token pricing.

Single source of truth. Update the dict; experiments update automatically.
Pricing grounded in ``docs/TECHNICAL_REFERENCE.md`` §7.4:

* GPT-4o-mini, Claude Haiku 4.5 — TalentAdore production pricing (May 2026).
* Frontier-Sonnet tier — ``financial-analysis-university-ai-service-economy.pdf``
  p. 10 (USD 3 / 1M input, USD 15 / 1M output ≈ EUR 2.76 / EUR 13.80).
* Local — on-prem ConfidentialMind amortised cost (EUR 0.05/1M).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PricePerMillion:
    """EUR per 1M tokens for one provider/model."""

    input_eur: float
    output_eur: float


PRICING: dict[str, PricePerMillion] = {
    # OpenAI prices (USD-converted to EUR at ~0.92 EUR/USD, May 2026).
    "gpt-4o-mini":           PricePerMillion(input_eur=0.138, output_eur=0.552),
    "gpt-4o":                PricePerMillion(input_eur=2.30,  output_eur=9.20),

    # Anthropic prices (USD-converted to EUR, May 2026).
    "claude-haiku-4-5":      PricePerMillion(input_eur=0.92,  output_eur=4.60),
    "claude-sonnet-4-6":     PricePerMillion(input_eur=2.76,  output_eur=13.80),
    "claude-opus-4-6":       PricePerMillion(input_eur=13.80, output_eur=69.00),

    # Frontier reference price (financial-analysis-university-ai-service-economy.pdf p. 10).
    "frontier-sonnet-tier":  PricePerMillion(input_eur=2.76,  output_eur=13.80),

    # Local amortised cost (financial-analysis p. 10).
    "local-mlx":             PricePerMillion(input_eur=0.05,  output_eur=0.05),
    "local-llamacpp-int4":   PricePerMillion(input_eur=0.05,  output_eur=0.05),
    "local-ollama":          PricePerMillion(input_eur=0.05,  output_eur=0.05),

    # Featherless API — open-source models served via API.
    # Free tier / pay-per-use. Estimate based on comparable providers.
    "Qwen/Qwen2.5-72B-Instruct":           PricePerMillion(input_eur=0.37,  output_eur=0.37),
    "meta-llama/Llama-3.3-70B-Instruct":    PricePerMillion(input_eur=0.37,  output_eur=0.37),
    "mistralai/Mistral-Small-24B-Instruct-2501": PricePerMillion(input_eur=0.14, output_eur=0.14),
}


def eur_for_call(model: str, input_tokens: int, output_tokens: int) -> float:
    """Look up the price for ``model``, return EUR cost.

    Raises :class:`KeyError` for unknown models — we prefer fail-fast over a
    silent zero cost that would bias the C3 cost analysis.
    """
    price = PRICING[model]
    return (input_tokens / 1_000_000.0) * price.input_eur + (
        output_tokens / 1_000_000.0
    ) * price.output_eur


def register_price(model: str, *, input_eur: float, output_eur: float) -> None:
    """Add or override a price at runtime. Used by tests and the CLI ``--price`` flag."""
    PRICING[model] = PricePerMillion(input_eur=input_eur, output_eur=output_eur)
