from nvidia_eval_commons.api.run import run_eval


def main():
    # Add this `framework_entrypoint:main` as an entrypoint to `pyproject.toml`, example
    run_eval()