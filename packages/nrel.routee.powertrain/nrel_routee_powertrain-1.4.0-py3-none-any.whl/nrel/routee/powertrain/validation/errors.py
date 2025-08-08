from __future__ import annotations
from dataclasses import dataclass

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from nrel.routee.powertrain.core.features import FeatureSetId
from nrel.routee.powertrain.core.model_config import ModelConfig
from nrel.routee.powertrain.estimators.estimator_interface import Estimator
from nrel.routee.powertrain.estimators.ngboost_estimator import NGBoostEstimator
from nrel.routee.powertrain.core.real_world_adjustments import ADJUSTMENT_FACTORS

REPR_ROWS = {
    "feature_set_id": "Feature Set ID",
    "target": "Target",
    "link_root_mean_squared_error": "Link RMSE",
    "link_norm_root_mean_squared_error": "Link Norm RMSE",
    "link_weighted_relative_percent_difference": "Link Weighted RPD",
    "net_error": "Net Error",
    "actual_dist_per_energy": "Actual Dist/Energy",
    "pred_dist_per_energy": "Predicted Dist/Energy",
    "real_world_pred_dist_per_energy": "Real World Predicted Dist/Energy",
    "trip_relative_percent_difference": "Trip RPD",
    "trip_weighted_relative_percent_difference": "Trip Weighted RPD",
    "trip_root_mean_squared_error": "Trip RMSE",
    "trip_norm_root_mean_squared_error": "Trip Norm RMSE",
    "link_negative_log_likelihood": "Link NLL",
    "link_continuous_ranked_probability_score": "Link CRPS",
    "link_prediction_interval_coverage_probability": "Link PICP",
    "trip_negative_log_likelihood": "Trip NLL",
    "trip_continuous_ranked_probability_score": "Trip CRPS",
    "trip_prediction_interval_coverage_probability": "Trip PICP",
}


def mean_squared_error(A, B, axis: Optional[int] = None) -> float:
    return np.square(A - B).mean(axis=axis)


def net_energy_error(target, target_pred) -> float:
    net_e = np.sum(target)
    net_e_pred = np.sum(target_pred)
    net_error = (net_e_pred - net_e) / net_e
    return net_error


def weighted_relative_percent_difference(target, target_pred) -> float:
    epsilon = np.finfo(np.float64).eps

    w = np.array(np.abs(target) / np.sum(np.abs(target)))

    error_norm = np.abs(
        2
        * (
            (target - target_pred)
            / np.maximum((np.abs(target) + np.abs(target_pred)), epsilon)
        )
    )

    mean_error = np.average(error_norm, weights=w)

    return mean_error


def relative_percent_difference(target, target_pred) -> float:
    epsilon = np.finfo(np.float64).eps

    error_norm = np.abs(
        2
        * (
            (target - target_pred)
            / np.maximum((np.abs(target) + np.abs(target_pred)), epsilon)
        )
    )

    mean_error = np.average(error_norm)

    return mean_error


def calculate_nll(target, target_pred, target_std) -> float:
    """
    Calculate Negative Log-Likelihood (NLL).
    """
    try:
        from scipy.stats import norm
    except ImportError:
        raise ImportError(
            "The calculate_nll function requires scipy. "
            "To install, you can do pip install scipy"
        )
    nll = -np.mean(norm.logpdf(target, loc=target_pred, scale=target_std))
    return nll


def calculate_crps(target, target_pred, target_std) -> float:
    """
    Calculate Continuous Ranked Probability Score (CRPS).
    """
    try:
        from scipy.stats import norm
    except ImportError:
        raise ImportError(
            "The calculate_nll function requires scipy. "
            "To install, you can do pip install scipy"
        )
    # CDF of the predicted distribution
    z = (target - target_pred) / target_std
    crps = target_std * (
        z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi)
    )
    return np.mean(crps)


def calculate_picp(target, lower_bound, upper_bound) -> float:
    """
    Calculate Prediction Interval Coverage Probability (PICP).
    """
    inside_interval = (target >= lower_bound) & (target <= upper_bound)
    picp = np.mean(inside_interval)
    return picp


def calculate_combined_sd(target_std) -> float:
    """
    Calculate the combined standard deviation of the target.
    """
    combined_variance = (target_std**2).sum()
    combined_sd = np.sqrt(combined_variance)
    return combined_sd


def errors_to_html_lines(errors: Errors) -> List[str]:
    html_lines = []
    for error_name, error_value in errors.to_dict().items():
        if error_value is None:
            # possible if there are not trip errors
            continue
        row_name = REPR_ROWS[error_name]
        html_lines.append(f"<tr><td>{row_name}</td><td>{error_value:.5f}</td></tr>")
    return html_lines


@dataclass
class Errors:
    link_root_mean_squared_error: float
    link_norm_root_mean_squared_error: float
    link_weighted_relative_percent_difference: float

    net_error: float
    actual_dist_per_energy: float
    pred_dist_per_energy: float
    real_world_pred_dist_per_energy: float

    trip_relative_percent_difference: Optional[float] = None
    trip_weighted_relative_percent_difference: Optional[float] = None
    trip_root_mean_squared_error: Optional[float] = None
    trip_norm_root_mean_squared_error: Optional[float] = None

    link_negative_log_likelihood: Optional[float] = None
    link_continuous_ranked_probability_score: Optional[float] = None
    link_prediction_interval_coverage_probability: Optional[float] = None

    trip_negative_log_likelihood: Optional[float] = None
    trip_continuous_ranked_probability_score: Optional[float] = None
    trip_prediction_interval_coverage_probability: Optional[float] = None

    @classmethod
    def from_dict(self, d: dict) -> Errors:
        return Errors(**d)

    def to_dict(self) -> dict:
        out_d = {}
        for k, v in self.__dict__.items():
            if v is not None:
                out_d[k] = float(v)
        return out_d

    def _repr_html_(self) -> str:
        html_lines = ["<table border='1' style='border-collapse: collapse;'>"]

        html_lines.extend(errors_to_html_lines(self))

        html_lines.append("</table>")

        return "".join(html_lines)


def estimator_errors_to_html_lines(estimator_errors: EstimatorErrors) -> List[str]:
    html_lines = []

    html_lines.append(
        "<tr><td colspan='2' style='border-bottom: 2px solid black;"
        "text-align: center;'><b>Estimator Errors</b></td></tr>"
    )
    html_lines.append(
        f"<tr><td>Feature Set ID</td><td>{estimator_errors.feature_set_id}</td></tr>"
    )
    for target, errors in estimator_errors.error_by_target.items():
        html_lines.append(f"<tr><td>Target</td><td>{target}</td></tr>")
        html_lines.extend(errors_to_html_lines(errors))

    return html_lines


@dataclass
class EstimatorErrors:
    feature_set_id: FeatureSetId
    error_by_target: Dict[str, Errors]

    @classmethod
    def from_dict(cls, d: dict) -> EstimatorErrors:
        d["error_by_target"] = {
            k: Errors.from_dict(v) for k, v in d["error_by_target"].items()
        }
        return EstimatorErrors(**d)

    def to_dict(self) -> dict:
        out_dict = self.__dict__.copy()
        out_dict["error_by_target"] = {
            k: v.to_dict() for k, v in self.error_by_target.items()
        }
        return out_dict

    def _repr_html_(self) -> str:
        html_lines = ['<table border="1" style="border-collapse: collapse;">']
        html_lines.extend(estimator_errors_to_html_lines(self))
        html_lines.append("</table>")
        return "".join(html_lines)


@dataclass
class ModelErrors:
    estimator_errors: Dict[FeatureSetId, EstimatorErrors]

    @classmethod
    def from_dict(cls, d: dict) -> ModelErrors:
        d["estimator_errors"] = {
            k: EstimatorErrors.from_dict(v) for k, v in d["estimator_errors"].items()
        }
        return ModelErrors(**d)

    def to_dict(self) -> dict:
        out_dict = self.__dict__.copy()
        out_dict["estimator_errors"] = {
            k: v.to_dict() for k, v in self.estimator_errors.items()
        }
        return out_dict

    def _repr_html_(self) -> str:
        html_lines = ['<table border="1" style="border-collapse: collapse;">']
        for _, estimator_error in self.estimator_errors.items():
            html_lines.extend(estimator_errors_to_html_lines(estimator_error))
        html_lines.append("</table>")

        return "".join(html_lines)

    def __repr__(self) -> str:
        """
        Returns a pretty printed summary of the model errors
        """
        summary_lines = []

        max_key_length = max([len(row_name) for row_name in REPR_ROWS.values()])

        summary_lines.append("=" * (max_key_length + 20))
        for feature_set_id, estimator_error in self.estimator_errors.items():
            for target, errors in estimator_error.error_by_target.items():
                summary_lines.append(
                    f"{'Feature Set ID:':<{max_key_length}} {feature_set_id}"
                )
                summary_lines.append(f"{'Target:':<{max_key_length}} {target}")
                for error_name, error_value in errors.to_dict().items():
                    if error_value is None:
                        # possible if there are not trip errors
                        continue
                    row_name = REPR_ROWS[error_name]
                    summary_lines.append(
                        f"{row_name:<{max_key_length}} {error_value:.3f}"
                    )
                summary_lines.append("=" * (max_key_length + 20))

        return "\n".join(summary_lines)


def compute_errors(
    test_df: pd.DataFrame,
    estimators: Dict[FeatureSetId, Estimator],
    config: ModelConfig,
) -> ModelErrors:
    """
    Computes the error metrics for a set of predictions relative
    to the ground truth data

    Args:
        test_df: the test dataframe
        estimators: a set of estimators
        config: The model configuration

    Returns: a dictionary with all of the error values

    """
    test_df = test_df.copy()

    model_errors = {}

    for feature_set_id, estimator in estimators.items():
        feature_set = config.feature_set_map[feature_set_id]
        target_set = config.target
        distance = config.distance
        predict_method = config.predict_method

        predictions = estimator.predict(
            test_df,
            feature_set=feature_set,
            distance=distance,
            target_set=target_set,
            predict_method=predict_method,
        )

        estimator_errors = {}

        for energy_name in target_set.target_name_list:
            errors = {}
            target = np.array(test_df[energy_name])
            target_pred = np.array(predictions[energy_name])

            rmse = np.sqrt(mean_squared_error(target, target_pred))
            errors["link_root_mean_squared_error"] = rmse
            errors["link_norm_root_mean_squared_error"] = rmse / (
                sum(test_df[energy_name]) / len(test_df)
            )

            ew_rpe = weighted_relative_percent_difference(target, target_pred)
            errors["link_weighted_relative_percent_difference"] = ew_rpe

            trip_column = config.trip_column

            if trip_column in test_df.columns:
                test_df["energy_pred"] = target_pred
                gb = test_df.groupby(trip_column).agg(
                    {energy_name: "sum", "energy_pred": "sum"}
                )
                t_rpd = relative_percent_difference(gb[energy_name], gb["energy_pred"])
                t_wrpd = weighted_relative_percent_difference(
                    gb[energy_name], gb["energy_pred"]
                )
                t_rmse = np.sqrt(mean_squared_error(gb[energy_name], gb["energy_pred"]))

                errors["trip_relative_percent_difference"] = t_rpd
                errors["trip_weighted_relative_percent_difference"] = t_wrpd
                errors["trip_root_mean_squared_error"] = t_rmse
                errors["trip_norm_root_mean_squared_error"] = t_rmse / (
                    sum(gb[energy_name]) / len(gb)
                )

            if isinstance(estimator, NGBoostEstimator):
                try:
                    from scipy.stats import norm
                except ImportError:
                    raise ImportError(
                        "The errors for the NGBoostEstimator requires other dependnecies like scipy. "
                        "To install, you can do `pip install nrel.routee.powertrain[ngboost]"
                    )
                target_std = np.array(predictions[energy_name + "_std"])
                alpha = 0.05
                z = norm.ppf(1 - alpha / 2)  # z-score for 95% confidence
                lower_bound = target_pred - z * target_std
                upper_bound = target_pred + z * target_std

                errors["link_negative_log_likelihood"] = calculate_nll(
                    target, target_pred, target_std
                )
                errors["link_continuous_ranked_probability_score"] = calculate_crps(
                    target, target_pred, target_std
                )
                errors["link_prediction_interval_coverage_probability"] = round(
                    calculate_picp(target, lower_bound, upper_bound), 2
                )

                if trip_column in test_df.columns:
                    test_df["energy_pred"] = target_pred
                    test_df["energy_pred_std"] = target_std
                    gb = test_df.groupby(trip_column).agg(
                        {
                            energy_name: "sum",
                            "energy_pred": "sum",
                            "energy_pred_std": calculate_combined_sd,
                        }
                    )
                    lower_bound = gb["energy_pred"] - z * gb["energy_pred_std"]
                    upper_bound = gb["energy_pred"] + z * gb["energy_pred_std"]

                    errors["trip_negative_log_likelihood"] = calculate_nll(
                        gb[energy_name], gb["energy_pred"], gb["energy_pred_std"]
                    )
                    errors["trip_continuous_ranked_probability_score"] = calculate_crps(
                        gb[energy_name], gb["energy_pred"], gb["energy_pred_std"]
                    )
                    errors["trip_prediction_interval_coverage_probability"] = round(
                        calculate_picp(gb[energy_name], lower_bound, upper_bound), 2
                    )

            errors["net_error"] = net_energy_error(target, target_pred)

            total_dist = test_df[distance.name].sum()

            real_word_pred = target_pred * ADJUSTMENT_FACTORS[config.powertrain_type]

            pred_energy = np.sum(target_pred)
            real_word_pred_energy = np.sum(real_word_pred)
            actual_energy = np.sum(target)

            errors["actual_dist_per_energy"] = total_dist / actual_energy
            errors["pred_dist_per_energy"] = total_dist / pred_energy
            errors["real_world_pred_dist_per_energy"] = (
                total_dist / real_word_pred_energy
            )

            errors_obj = Errors(**errors)

            estimator_errors[energy_name] = errors_obj

        estimator_errors_obj = EstimatorErrors(feature_set_id, estimator_errors)

        model_errors[feature_set_id] = estimator_errors_obj

    model_errors_obj = ModelErrors(model_errors)

    return model_errors_obj
