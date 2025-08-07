from pathlib import Path

from nvidia_eval_commons.api.api_dataclasses import EvaluationResult
from nvidia_eval_commons.api.base import EvalFrameworkBase
from nvidia_eval_commons.api.run import register_framework

from .output import parse_output


@register_framework
class GarakEvalFramework(EvalFrameworkBase):
    @staticmethod
    def parse_output(output_dir: str) -> EvaluationResult:
        return parse_output(output_dir)

    @staticmethod
    def framework_def() -> Path:
        return Path(__file__).parent.joinpath("framework.yml")