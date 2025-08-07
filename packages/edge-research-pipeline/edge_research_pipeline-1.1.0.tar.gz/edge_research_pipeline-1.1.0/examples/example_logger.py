"""
Example: Pipeline Logger Usage
Location: examples/logger_example.py

Demonstrates initializing and using the PipelineLogger for:
- Step-level logging
- Config-driven and manual param control

See: docs/logger.md for full method and parameter details.
"""

from pathlib import Path
import pandas as pd
import edge_research
from edge_research import PipelineLogger, load_params, Config

# --- 1. Setup: Load Config (Recommended) ---

# Resolve params directory inside installed package
params_dir = Path(edge_research.__path__[0]) / "params"

# Load configuration files
default_params = params_dir / "default_params.yaml"
custom_params = params_dir / "custom_params.yaml"

params = load_params(str(default_params), str(custom_params))
cfg = Config(**params)

# --- 2. Choose Save Location and Logger Params ---

run_name = cfg.run_name
log_markdown = cfg.log_markdown
log_json = cfg.log_json
log_max_rows = cfg.log_max_rows

save_folder = Path("data/results") / run_name
save_folder.mkdir(parents=True, exist_ok=True)

# --- 3. Initialize Logger (Config-Driven) ---

logger = PipelineLogger(
    log_path=save_folder / f"{run_name}_log",
    log_markdown=log_markdown,
    log_json=log_json
)

# --- 4. Step Logging Example ---

example_df = pd.DataFrame([{'test_col': 'test_value'}])

logger.log_step(
    step_name="Example Step",
    info={"run_name": run_name, "log_markdown": log_markdown, "log_json": log_json},
    df=example_df,
    max_rows=log_max_rows
)

print(f"Logged 'Example Step' to {save_folder / f"{run_name}_log"}")

# --- 5. Manual Param Override Example (Optional) ---

# You can also manually specify log_markdown/log_json/log_max_rows if not using config.
manual_logger = PipelineLogger(
    log_path=save_folder / "manual_log",
    log_markdown=True,
    log_json=False
)
manual_logger.log_step(
    step_name="Manual Step",
    info={"custom": "value"},
    df=example_df,
    max_rows=20
)

# --- Reference ---

# See docs/logger.md for additional methods (e.g., logging tables, exceptions, custom formatting, etc.)