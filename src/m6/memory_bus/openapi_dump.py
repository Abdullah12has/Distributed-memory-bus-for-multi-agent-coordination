"""Dump OpenAPI schema to stdout.

Invoked from ``make bus-openapi``. Keeps the spec at ``docs/openapi.json``
checked in so reviewers can diff API changes.
"""

from __future__ import annotations

import json
import sys

from m6.memory_bus.api import create_app


def main() -> None:
    app = create_app()
    json.dump(app.openapi(), sys.stdout, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
