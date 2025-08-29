from pathlib import Path
import argparse
import os

import plotly.graph_objects as go
import polars as pl
from skrub import tabular_pipeline
from sklearn.linear_model import ElasticNet
from plotly.subplots import make_subplots



rate_code_mapping = {
    1: "Standard rate",
    2: "JFK",
    3: "Newark",
    4: "Nassau or Westchester",
    5: "Negotiated fare",
    6: "Group ride",
    99: "Unknown",
}


def analyze_taxi_unit_economics(data_folder: str) -> pl.DataFrame:
    """
    Read the files in data_folder and return a DataFrame with unit-economic metrics.
    """
    # Lazily scan all parquet files in the folder for memory efficiency
    q = pl.scan_parquet(os.path.join(data_folder, '*.parquet'))

    # Feature Engineering and Cleaning
    # Chaining operations in Polars is highly efficient
    processed_q = (
        q.with_columns(
            trip_duration_minutes=(
                pl.col("tpep_dropoff_datetime") - pl.col("tpep_pickup_datetime")
            ).dt.total_seconds() / 60,
            net_total_amount=pl.col("total_amount") - pl.col("tip_amount")
        )
        .filter(
            (pl.col("trip_distance") > 0) &
            (pl.col("trip_duration_minutes") > 0) &
            (pl.col("total_amount") > 0)
        )
        .with_columns(
            net_effective_rate_per_mile=(
                pl.col("net_total_amount") / pl.col("trip_distance")
            ),
            net_effective_rate_per_minute=(
                pl.col("net_total_amount") / pl.col("trip_duration_minutes")
            )
        )
        .with_columns(
        pl.col("RatecodeID").map_elements(
            lambda x: rate_code_mapping.get(x, "Unknown"), 
            return_dtype=pl.String
        ).alias("RateCodeName")
    )
    )
    return processed_q.collect()

def plot_and_save_metrics(df: pl.DataFrame, file_path: str) -> None:
        """Creates, displays, and saves bar charts for the unit-economic metrics."""
        df_pandas = df.to_pandas()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Median Net Effective Rate per Mile", "Median Net Effective Rate per Minute"),
            horizontal_spacing=0.1
        )
        
        fig.add_trace(
            go.Bar(
                x=df_pandas["RateCodeName"],
                y=df_pandas["median_rate_per_mile"],
                name="Rate per Mile ($)",
                text=[f"{val:.2f}" for val in df_pandas["median_rate_per_mile"]],
                textposition="outside",
                marker_color="lightblue"
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(
                x=df_pandas["RateCodeName"],
                y=df_pandas["median_rate_per_minute"],
                name="Rate per Minute ($)",
                text=[f"{val:.2f}" for val in df_pandas["median_rate_per_minute"]],
                textposition="outside",
                marker_color="lightcoral"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="<b>Taxi Unit Economics by Rate Code</b>",
            showlegend=False,
            height=500,
            width=1200
        )
        fig.update_xaxes(title_text="Rate Code", row=1, col=1)
        fig.update_xaxes(title_text="Rate Code", row=1, col=2)
        fig.update_yaxes(title_text="Rate per Mile ($)", row=1, col=1)
        fig.update_yaxes(title_text="Rate per Minute ($)", row=1, col=2)
        
        fig.write_html(file_path)
        print(f"Plot saved to {file_path}")


if __name__ == "__main__":

    Q2_DEFAULT_FOLDER = Path("data").joinpath("Q2")
    INPUT_FOLDER_DEFAULT = Q2_DEFAULT_FOLDER
    OUTPUT_FOLDER_DEFAULT = Q2_DEFAULT_FOLDER.joinpath("output")

    INPUT_FOLDER_DEFAULT.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER_DEFAULT.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description="Analyze taxi data and generate reports.")
    parser.add_argument(
        "--data-path",
        type=str,
        default=INPUT_FOLDER_DEFAULT.as_posix(),
        help="Path to the folder containing input parquet files.",
    )
    args = parser.parse_args()
    input_folder = Path(args.data_path)
    output_path = input_folder.joinpath("output")


    processed_data = analyze_taxi_unit_economics(input_folder.as_posix())
    print("\n--- Unit-Economic Metrics by Rate Code (First 5 rows) ---")
    print(processed_data.head())

    analysis_df = (
        processed_data.group_by("RatecodeID")
        .agg(
            pl.median("net_effective_rate_per_mile").alias("median_rate_per_mile"),
            pl.median("net_effective_rate_per_minute").alias("median_rate_per_minute"),
            pl.len().alias("trip_count")
        )
        .sort("RatecodeID")
        .with_columns(
            pl.col("RatecodeID").map_elements(
                lambda x: rate_code_mapping.get(x, "Unknown"), 
                return_dtype=pl.String
            ).alias("RateCodeName")
        )
    )
    print("\n--- Median-Based Unit Economics ---")
    print(analysis_df)
    plot_and_save_metrics(analysis_df, str(output_path.joinpath("median_unit_economics.html")))

    # Fit models and plot coefficient-based metrics
    grouped_results = []
    for rate_code_name in processed_data["RateCodeName"].unique():
        if rate_code_name is not None:
            group_data = processed_data.filter(pl.col("RateCodeName") == rate_code_name)
            print(f"Fitting model for {rate_code_name}...")
            if len(group_data) > 1:
                X_group = group_data.select(pl.col("trip_distance"), pl.col("trip_duration_minutes"))
                y_group = group_data.select(pl.col("fare_amount"))
                
                group_model = tabular_pipeline(ElasticNet(fit_intercept=False, positive=True), n_jobs=-1)
                group_model.fit(X_group, y_group)
            
                rate_code_id = group_data["RatecodeID"].first()
                median_rate_per_mile = group_model[-1].coef_[0]
                median_rate_per_minute = group_model[-1].coef_[1]
                
                grouped_results.append({
                    "RatecodeID": rate_code_id,
                    "median_rate_per_mile": median_rate_per_mile,
                    "median_rate_per_minute": median_rate_per_minute,
                    "trip_count": len(group_data),
                    "RateCodeName": rate_code_name
                })

    grouped_models_df = pl.DataFrame(grouped_results).sort("RatecodeID")
    print("\n--- Model-Based Unit Economics (Coefficients) ---")
    print(grouped_models_df)
    plot_and_save_metrics(grouped_models_df, str(output_path.joinpath("model_coefficient_economics.html")))