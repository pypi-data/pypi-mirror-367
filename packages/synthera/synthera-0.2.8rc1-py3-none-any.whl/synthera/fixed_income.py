import base64
import io
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional

import matplotlib.figure as mpl_figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.core.getipython import get_ipython
from numpy.typing import NDArray
from pydantic import BaseModel, Field, field_validator, model_validator

from synthera.chartconfig import rcParamsSynthera
from synthera.protocols import SyntheraClientProtocol

_logger: logging.Logger = logging.getLogger(__name__)

plt.rcParams.update(rcParamsSynthera)

Array1D = Annotated[NDArray[np.float64], Literal["1D array"]]
Array2D = Annotated[NDArray[np.float64], Literal["2D array"]]
Array3D = Annotated[NDArray[np.float64], Literal["3D array"]]
Array4D = Annotated[NDArray[np.float64], Literal["4D array"]]

INDEX_COLUMN_NAME: str = "IDX"
SAMPLE_COLUMN_NAME: str = "SAMPLE"
YC_COLUMN_PREFIX: str = "YC"


class GetModelLabelsRequest(BaseModel):
    """Request for get model labels."""

    model_label: str


class GetModelLabelsResponse(BaseModel):
    """Response for get model labels."""

    model_labels: List[str]


class ModelMetadata(BaseModel):
    """Model metadata."""

    model_label: str
    dataset: str
    universe: str
    curve_labels: list[str]
    start_date_training: str
    end_date_training: str
    max_simulate_days: int
    conditional_days: int
    tenors: list[float]


class GetModelMetadataResponse(BaseModel):
    """Response for model metadata."""

    metadata: ModelMetadata


class SimulateRequest(BaseModel):
    """Request for simulate."""

    model_label: str = Field(
        ...,  # Make it required
        description="Model label",
        examples=["YieldGAN-vV-z0"],
        min_length=1,
    )
    curve_labels: List[str] = Field(
        ...,  # Make it required
        description="List of yield curve labels",
        examples=["USA", "GBR", "DEU"],
        min_length=1,  # Ensure at least one curve name is provided
    )
    no_samples: int = Field(
        ...,  # Make it required
        description="Number of samples",
        examples=[100, 1000, 10000],
        gt=0,
    )
    no_days: int = Field(
        ...,  # Make it required
        description="Number of simulation days",
        examples=[3, 30, 120],
        gt=0,
    )
    reference_date: str = Field(
        ...,  # Make it required
        description="Reference date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",  # Regex pattern for YYYY-MM-DD
    )
    return_conditional: bool = Field(
        default=False,  # Provide default value
        description="Return conditional flag (optional; defaults to false)",
    )
    conditional_vol_factor: Optional[float] = Field(
        default=None,
        description="Conditional volatility factor",
    )
    fallback_on_missing_date: Optional[bool] = Field(
        default=None,
        description="Fallback on missing reference date",
    )

    @field_validator("reference_date")
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Must be YYYY-MM-DD")
        return v

    @model_validator(mode="after")
    def validate_model(self) -> "SimulateRequest":
        # Ensure reference date is not in the future
        if datetime.strptime(self.reference_date, "%Y-%m-%d") > datetime.now():
            raise ValueError("reference_date cannot be in the future")

        # Validate total data points don't exceed reasonable limit
        total_points = self.no_samples * self.no_days * len(self.curve_labels)
        if total_points > 100_000_000:  # 100 million points limit
            raise ValueError(
                f"Total data points ({total_points}) exceeds maximum limit"
            )

        return self


class SimulateOutput(BaseModel):
    """Output for simulate."""

    curve_label: str
    data: str


class SimulateMetadata(ModelMetadata):
    """Metadata for simulate request

    Inherits from ModelMetadata.
    """

    reference_date: str
    return_conditional: Optional[bool] = None
    conditional_vol_factor: Optional[float] = None
    fallback_on_missing_date: Optional[bool] = None


class SimulateResponse(BaseModel):
    outputs: List[SimulateOutput]
    metadata: SimulateMetadata


def _is_jupyter() -> bool:
    """Check if running in Jupyter environment."""
    try:
        get_ipython()
    except NameError:
        return False
    return True


def _handle_plot_display(fig: mpl_figure.Figure, show_plot: bool) -> mpl_figure.Figure:
    """Handle plot display to prevent double display in Jupyter."""
    if show_plot and not _is_jupyter():
        plt.show()

    if _is_jupyter():
        plt.close(fig)

    return fig


class SimulateResults:
    dataframes: OrderedDict[str, pd.DataFrame]
    names: List[str]
    column_names: List[str]
    ndarray: Array4D
    metadata: Dict[str, Any]

    def __init__(
        self,
        dataframes: OrderedDict[str, pd.DataFrame],
        names: List[str],
        column_names: List[str],
        ndarray: Array4D,
        metadata: Dict[str, Any],
    ):
        self.dataframes = dataframes
        self.names = names
        self.column_names = column_names
        self.ndarray = ndarray
        self.metadata = metadata

    def get_dates(self) -> list[pd.Timestamp]:
        first_country: str = self.names[0]
        dates: list[pd.Timestamp] = list(
            set(self.dataframes[first_country][INDEX_COLUMN_NAME].to_list())
        )
        dates.sort()
        return dates

    def get_yc_indices(self) -> list[int]:
        columns: list[str] = self.column_names
        yc_indexes: list[int] = [
            i for i in range(len(columns)) if YC_COLUMN_PREFIX in columns[i]
        ]
        return yc_indexes

    def get_yc_samples(
        self,
    ) -> Array4D:
        yc_indices: list[int] = self.get_yc_indices()
        yield_curve_samples: Array4D = self.ndarray[:, :, :, yc_indices]
        return yield_curve_samples

    def get_country_yc_samples(self, country: str) -> Array3D:
        country_str = country.strip().upper()
        if country_str not in self.names:
            raise ValueError(f"Country {country_str} not found")

        country_idx: float = self.names.index(country_str)
        yield_curve_samples: Array4D = self.get_yc_samples()

        country_samples: Array3D = yield_curve_samples[:, country_idx, :, :]
        return country_samples

    def get_yc_sample(self, country: str, sample_num: int = 0) -> Array2D:
        if sample_num < 0:
            raise IndexError(f"Sample number ({sample_num}) must be greater than 0")

        yc_samples: Array3D = self.get_country_yc_samples(country)

        num_samples: int = yc_samples.shape[0]
        if sample_num > num_samples - 1:
            raise IndexError(
                f"Sample number ({sample_num}) must be less than number of samples ({num_samples})"
            )
        yc_sample: Array2D = yc_samples[sample_num]
        return yc_sample

    def get_country_sample_at_t(
        self,
        country: str,
        time_idx: int = 0,
        sample_num: int = 0,
    ) -> Array1D:
        if time_idx < 0:
            raise IndexError(f"Time index ({time_idx}) must be greater than 0")

        yc_sample: Array2D = self.get_yc_sample(country, sample_num)

        num_time_steps: int = yc_sample.shape[0]
        if time_idx > num_time_steps - 1:
            raise IndexError(
                f"Time index ({time_idx}) must be less than number of time steps ({num_time_steps})"
            )
        country_sample: Array1D = yc_sample[time_idx]
        return country_sample

    def plot_country_sample_at_time(
        self,
        country: str,
        time_idx: int = 0,
        sample_num: int = 0,
        show_plot: bool = False,
    ) -> mpl_figure.Figure:
        country_sample: Array1D = self.get_country_sample_at_t(
            country, time_idx, sample_num
        )
        dates: list[pd.Timestamp] = self.get_dates()
        date_str: str = dates[time_idx].strftime("%Y-%m-%d")
        tenors: list[float] = self.metadata["tenors"]

        fig, ax = plt.subplots()
        ax.plot(tenors, country_sample)
        ax.set_xlabel("Maturities (years)")
        ax.set_ylabel("Yield (%)")
        ax.set_title(f"Yield Curve for {country} at {date_str}\n (Sample {sample_num})")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return _handle_plot_display(fig, show_plot)

    def plot_country_all_samples_at_time(
        self,
        country: str,
        time_idx: int = 0,
        show_plot: bool = False,
    ) -> mpl_figure.Figure:
        country_samples: Array3D = self.get_country_yc_samples(
            country
        )  # shape: (num_samples, num_days, num_maturities)
        dates: list[pd.Timestamp] = self.get_dates()
        date_str: str = dates[time_idx].strftime("%Y-%m-%d")
        tenors: list[float] = self.metadata["tenors"]

        fig, ax = plt.subplots()

        num_samples = country_samples.shape[0]
        for sample_idx in range(num_samples):
            yield_curve_data = country_samples[sample_idx, time_idx, :]
            ax.plot(tenors, yield_curve_data, label=f"Sample {sample_idx}", alpha=0.7)

        ax.set_xlabel("Maturities (years)")
        ax.set_ylabel("Yield (%)")
        ax.set_title(
            f"All Yield Curve Samples (n={num_samples}) for {country} at {date_str}"
        )
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return _handle_plot_display(fig, show_plot)

    def plot_country_sample_yield_curve_over_time(
        self, country: str, sample_num: int = 0, show_plot: bool = False
    ) -> mpl_figure.Figure:
        yields_array: Array2D = np.array(
            self.get_yc_sample(country, sample_num)
        )  # shape = (num_days, num_maturities)
        tenor_years: Array1D = np.array(self.metadata["tenors"])
        num_days: int = yields_array.shape[0]
        num_maturities: int = yields_array.shape[1]
        dates: list[pd.Timestamp] = self.get_dates()

        date_ordinals = np.array([single_date.toordinal() for single_date in dates])

        x_matrix = np.tile(tenor_years[np.newaxis, :], (num_days, 1))
        y_matrix = np.tile(date_ordinals[:, np.newaxis], (1, num_maturities))
        z_matrix = yields_array

        tick_count: int = min(6, num_days)
        tick_indices: NDArray[np.int32] = np.linspace(
            0, num_days - 1, tick_count, dtype=int
        )
        tick_vals: NDArray[np.int32] = date_ordinals[tick_indices]
        tick_texts: list[str] = [dates[i].strftime("%Y-%m-%d") for i in tick_indices]

        fig = mpl_figure.Figure()
        ax = fig.add_subplot(111, projection="3d")

        ax.plot_surface(
            x_matrix,
            y_matrix,
            z_matrix,
            cmap="viridis",
            alpha=0.8,
            linewidth=0,
            antialiased=True,
        )
        ax.set_xlabel("Maturity (years)")
        ax.set_ylabel("Generate Date", labelpad=20)
        ax.set_zlabel("Yield (%)")
        ax.set_title(f"{country} Yield Curve Over Time (Sample {sample_num})")

        ax.set_yticks(tick_vals)
        ax.set_yticklabels(tick_texts)
        plt.tight_layout()

        return _handle_plot_display(fig, show_plot)


class FixedIncome:
    fixed_income_endpoint: str = "fixed-income"
    simulate_api_endpoint: str = f"{fixed_income_endpoint}/simulate"
    get_model_labels_api_endpoint: str = f"{fixed_income_endpoint}/getModelLabels"
    get_model_metadata_api_endpoint: str = f"{fixed_income_endpoint}/getModelMetadata"

    def __init__(self, client: SyntheraClientProtocol) -> None:
        self.client: SyntheraClientProtocol = client

    def _decode_to_df(self, encoded_data: str) -> pd.DataFrame:
        """Decode a base64-encoded feather file string into a pandas DataFrame."""
        try:
            base64_bytes: bytes = base64.b64decode(encoded_data)
            buffer: io.BytesIO = io.BytesIO(base64_bytes)
            df: pd.DataFrame = pd.read_feather(buffer)
        except Exception as e:
            raise ValueError(f"Failed to decode data: {e}")
        return df

    def simulate(self, params: dict[str, Any]) -> SimulateResults:
        """Simulate yield curves.

        Args:
            params: Parameters for the simulate request

        Returns:
            SimulateResults object
        """
        # pre-processing
        request: SimulateRequest = SimulateRequest.model_validate(params)

        _logger.info(f"Requesting yield curves simulation: {request.model_dump()}")

        # make request
        response: dict[str, Any] = self.client.make_post_request(
            endpoint=self.simulate_api_endpoint,
            payload=request.model_dump(),
        )

        response: SimulateResponse = SimulateResponse.model_validate(response)

        # post-processing
        dataframes: OrderedDict[str, pd.DataFrame] = OrderedDict()
        for output in response.outputs:
            df: pd.DataFrame = self._decode_to_df(output.data)
            df["IDX"] = pd.to_datetime(df["IDX"], unit="s")
            df["SAMPLE"] = df["SAMPLE"].astype(int)
            dataframes.update({output.curve_label: df})

        array: Array4D = np.concatenate(
            [
                df.values.reshape(request.no_samples, 1, -1, df.values.shape[1])
                for _, df in dataframes.items()
            ],
            axis=1,
        )

        return SimulateResults(
            dataframes=dataframes,
            names=list(dataframes.keys()),
            ndarray=array,
            column_names=list(list(dataframes.values())[0].columns),
            metadata=response.metadata.model_dump(),
        )

    def get_model_labels(self) -> List[str]:
        """Get the list of model labels."""
        response: dict[str, Any] = self.client.make_get_request(
            endpoint=self.get_model_labels_api_endpoint,
        )
        model_labels: GetModelLabelsResponse = GetModelLabelsResponse.model_validate(
            response
        )
        return model_labels.model_labels

    def get_model_metadata(self, model_label: str) -> ModelMetadata:
        """Get the metadata for a model."""
        request: GetModelLabelsRequest = GetModelLabelsRequest(model_label=model_label)
        response: dict[str, Any] = self.client.make_get_request(
            endpoint=self.get_model_metadata_api_endpoint,
            params=request.model_dump(),
        )
        model_metadata: GetModelMetadataResponse = (
            GetModelMetadataResponse.model_validate(response)
        )
        return model_metadata.metadata
