from pathlib import Path
import csv
import itertools
import concurrent.futures
import time
import argparse

def solve_subset_sum(target: float, numbers: list[float]) -> tuple[list[float], float]:
    """
    Return the best subset combination of small numbers whose sum is as close as possible to the big number
    without exceeding it.
    """
    best_sum = 0
    best_combination = []

    # Iterate through all possible combination lengths (from 1 to all numbers)
    for i in range(1, len(numbers) + 1):
        # Generate all combinations of the current length
        for combo in itertools.combinations(numbers, i):
            current_sum = sum(combo)
            # Check if the current sum is a better fit than the previous best
            if best_sum < current_sum <= target:
                best_sum = current_sum
                best_combination = list(combo)

            # If we hit the target exactly, we can"t do better.
            if best_sum == target:
                return best_combination, best_sum

    return best_combination, best_sum

def process_row_worker(args: tuple[int, list[str]]) -> str | None:
    """
    Worker function to process a single row. Designed to be run in a separate process.
    """
    i, row = args
    if not row:
        return None

    # Clean the row by replacing empty strings with 0 and converting to float
    try:
        cleaned_row = [float(num or 0) for num in row]
    except ValueError:
        return f"Row {i+1}: Contains non-float values. Skipping."

    big_number = cleaned_row[0]
    small_numbers = cleaned_row[1:]

    # Find the best combination and its sum
    combination, total = solve_subset_sum(target=big_number, numbers=small_numbers)

    # Return the formatted result string for the current row
    return (
        f"Row {i+1}:\n"
        f"  Big Number: {big_number}\n"
        f"  Small Numbers (options): {small_numbers}\n"
        f"  Best Combination: {combination} -> Sum: {total}\n"
    )

def process_csv_file(input_path: str, output_path: str) -> None:
    """
    Reads a CSV file, processes each row in parallel to solve the subset sum problem,
    and writes the results to an output file.
    """
    try:
        with open(input_path, mode="r", newline="") as infile:
            reader = csv.reader(infile)
            tasks = list(enumerate(reader))

        print(f"Processing file: {input_path} with parallel workers...")
        with concurrent.futures.ProcessPoolExecutor() as executor, open(output_path, "w") as outfile:
            results = executor.map(process_row_worker, tasks)
            for result in results:
                if result:
                    outfile.write(result + "\n")
        print(f"Results successfully written to {output_path}")

    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    start_time = time.time()
    DATAPATH = Path("data").joinpath("Q1")
    DATAPATH.mkdir(exist_ok=True, parents=True)

    default_input_file = DATAPATH.joinpath("input.csv")
    default_output_file = default_input_file.parent.joinpath("output.txt")

    parser = argparse.ArgumentParser(description="Solve the subset sum problem for each row in a CSV file.")
    parser.add_argument(
        "--input-file",
        type=str,
        default=str(default_input_file),
        help=f"Path to the input CSV file (default: {default_input_file})"
    )

    args = parser.parse_args()
    input_file = Path(args.input_file)
    output_file = input_file.parent.joinpath("output.txt")

    process_csv_file(input_file, output_file)
    end_time = time.time()
    print(f"Processing completed in {(end_time - start_time):,.4f} seconds.")
