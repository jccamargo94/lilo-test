# Lilo Interview Challenge

This repository contains the solutions for the Lilo take-home interview challenge. P

## How to Run the Solutions

This guide provides step-by-step instructions to set up the environment and run the solutions for both questions.

### Prerequisites

*   **Python 3.12**
*   **uv**: A fast Python package installer and resolver. If you don't have it, you can install it by running the appropriate command for your system:
    *   **macOS / Linux:**
        ```shell
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
    *   **Windows (PowerShell):**
        ```powershell
        irm https://astral.sh/uv/install.ps1 | iex
        ```

### Setup

1.  **Navigate to the project directory:**
    Open your terminal or command prompt and change to the directory containing the project files (`Q1.py`, `Q2.py`, etc.).

2.  **Create a virtual environment:**
    With UV already installed, configured and added to path, you can create a virtual environment using the following command:
    ```shell
    uv venv .venv --python 3.12
    ```

3.  **Activate the virtual environment:**
    *   **macOS / Linux (bash/zsh):**
        ```shell
        source .venv/bin/activate
        ```
    *   **Windows (Command Prompt):**
        ```cmd
        .venv\Scripts\activate.bat
        ```
    *   **Windows (PowerShell):**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```

4.  **Install dependencies:**
    Install the required Python packages using `uv` and sync it with `uv.lock`
    ```shell
    uv sync
    ```

### Running the Solutions

#### Question 1

The script `Q1.py` reads data from `input.csv`, processes each row in parallel, and prints the result to the console.

1.  Ensure the `input.csv` file is in the folder `data/Q1/` located in the same directory as `Q1.py`, if not, you can provide the path to the file in the script using `--input-file` flag
2.  Run the script from your activated virtual environment:
    if `input.csv` is in the `data/Q1/` folder run
    ```shell
    python Q1.py
    ```
    otherwise, if the file is in another directory, provide the path using `--input-file` flag.

    ```shell
    python Q1.py --input-file /path/to/your/input.csv
    ```

3.  The output will be saved in `output.txt` file in the same folder where `input.csv` file is located

#### Question 2

The script `Q2.py` runs the NYC Taxi Trips analysis, and saves the output

1.  **Data Download:** Download the data in any path, by default I'll assume data will be placed at `data/Q2/`
2.  Run the script from your activated virtual environment:
    ```shell
    python Q2.py
    ```
    If you have placed the data in a different directory, provide the path using `--data-path` flag.
    ```shell
    python Q2.py --data-path /path/to/your/data/folder/
    ```
3.  **Output:** The script will print its progress to the console. Upon completion, it will generate output files in the `data-path` directory.

---
## Test, Questions and Answers
Please find below 2 questions that we would like for you to solve. We care more about how you think/get to the answers. You have 72 hours from receiving this email.

Next steps, if you do well, are an interview with our CTO and if that goes well, the final interview is with the PM you will be working with.

Best of luck!

### Question 1:
You’ve just joined a fast-paced startup known for solving complex problems with elegant, efficient solutions. Your CEO has given you your first challenge:

#### Problem Statement
You will receive a CSV file where each row contains a list of numbers. The first number in each row is the “big number”. The remaining numbers in the row (up to 12) are “small numbers”.

Your task is to write a program (in any language) that, for each row, finds the combination of small numbers whose sum is as close as possible to the big number without exceeding it. You may use any number of small numbers from the list.
After implementing your solution, write a paragraph explaining:
Why you think your approach is the best for this problem
What its advantages are
What limitations it might have

Requirements:
Input: A CSV file where each row is formatted as described above.
Output: For each row, print the list of selected small numbers and their sum.

#### Answer:
This approach is effective because it guarantees finding the optimal solution, as it explores all possible combinations through an exhaustive search. Its main advantage is simplicity; the implementation is straightforward and easy to understand. In order to improve time and performance, a parallel approach has been implemented due to their potential inefficiency, especially with larger datasets, as the number of combinations grows exponentially for larger datasets. For the current implementation, the focus has been on ensuring correctness and clarity, while maintaining performance; for latter iterations, further optimizations could be explored such as greedy-algorithm or other heuristic approaches.

### Question 2:

One of the main challenges in the taxi industry is that pricing often does not accurately reflect the true costs of each trip, even with the existence of different rate codes. Your task is as follows:
Download several months of NYC Taxi Trips Data (link).

Design and calculate an overall unit-economic metric that helps to understand how much taxis are actually charging per unit (e.g., per mile or per minute). Clearly define your chosen unit and methodology.

Analyze how this unit-economic metric varies across each Rate Code.
Submit your code (in  your preferred stack) and any tables or charts you create.
Write a short paragraph explaining why you think your approach is effective, its advantages and limitations, and what you would propose for the next iteration.

#### Answer:
This approach focuses on calculating the median cost-per-mile for taxi trips, which provides a robust measure of central tendency that is less affected by outliers compared to the mean. This is particularly important in the context of taxi trips, where extreme values can skew the average. By analyzing the unit economics across different Rate Codes, we gain insights into how pricing strategies vary. The advantages of this method include its simplicity and interpretability, making it easy to communicate findings to stakeholders.

I've used two main approaches here:
- The first approach involves a straightforward calculation of the median cost-per-mile and cost-per-minute for each Rate Code, using the available trip data. This provides a clear and easily interpretable metric for understanding pricing variations.
- The second approach incorporates an ElasticNet regression model to predict the cost-per-mile and cost-per-minute based on both trip distance and duration. This approach improves our understanding of the factors driving pricing.

In the first approach, I computed the median cost-per-mile for each Rate Code by aggregating the trip data and computing the median value. This provided a clear and easily interpretable metric for understanding pricing variations across different segments of the taxi market, but it may not fully capture the complexity of the pricing dynamics. The latter approach builds on this by using a regression model to account for variables, it allows for a more fine-grained analysis of how different factors impact pricing.

Limitations include the exclusion of other potentially relevant factors such as time of day, trip duration, and passenger count, which could also influence pricing. For future iterations, I would propose incorporating these additional variables with a more advanced technique (e.g., RandomForest model) in combination with a ML explaination technique (e.g., SHAP or LIME).
