from __future__ import annotations

import os
import sys
from pathlib import Path


def add_lattice_estimator_to_path() -> Path:
    here = Path(__file__).resolve()
    artifact_root = here.parents[1]
    workspace_root = here.parents[2]

    candidates = []
    env_path = os.environ.get("LATTICE_ESTIMATOR_PATH")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(
        [
            artifact_root / "third_party" / "lattice-estimator",
            artifact_root / "lattice-estimator",
            workspace_root / "lattice-estimator",
        ]
    )

    for candidate in candidates:
        if (candidate / "estimator" / "__init__.py").is_file():
            sys.path.insert(0, str(candidate))
            return candidate

    tried = "\n".join(f"  - {path}" for path in candidates)
    raise SystemExit(
        "Could not find lattice-estimator. Run scripts/setup_lattice_estimator.sh, "
        "set LATTICE_ESTIMATOR_PATH, or place a checkout at "
        "third_party/lattice-estimator.\nTried:\n" + tried
    )
