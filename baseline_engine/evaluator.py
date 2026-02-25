import pandas as pd
import numpy as np
import os
from datetime import datetime

print("--- DEBUG: SCRIPT STARTED ---")

class RPCBaselineEngine:
    def __init__(self):
        # Establish the path to the 'data' folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(os.path.dirname(current_dir), "data")
        # Name changed as requested
        self.output_file = os.path.join(self.data_dir, "code_RealData.csv")
        os.makedirs(self.data_dir, exist_ok=True)

    def generate_mock_input(self, n_tx=100):
        """Generates mock parameters: latency, lag, and actual_delay."""
        rpc_ids = ['infura', 'alchemy', 'quicknode']
        
        telemetry = pd.DataFrame({
            'timestamp': pd.date_range(datetime.now(), periods=n_tx*3, freq='10s'),
            'rpc_id': rpc_ids * n_tx,
            'latency': np.random.uniform(20, 150, n_tx*3),
            'lag': np.random.randint(0, 5, n_tx*3)
        })
        
        outcomes = pd.DataFrame({
            'send_time': pd.date_range(datetime.now(), periods=n_tx, freq='25s'),
            'actual_delay': np.random.uniform(30, 200, n_tx),
            'success': np.random.choice([True, False], n_tx, p=[0.98, 0.02])
        })
        return telemetry, outcomes

    def calculate_metrics(self, name, delay_series, success_series):
        """Calculates parameters for CSV storage."""
        return {
            'strategy': name,
            'mean_delay': round(delay_series.mean(), 2),
            'median_delay': round(delay_series.median(), 2),
            'p95_delay': round(delay_series.quantile(0.95), 2),
            'failure_rate': round(1 - success_series.mean(), 4),
            'n': len(delay_series),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'output_path': self.output_file
        }

    def run_evaluation(self, telemetry_df, outcomes_df):
        results = []
        
        # Strategy 1: Round Robin (Average of all outcomes)
        results.append(self.calculate_metrics("Round_Robin", outcomes_df['actual_delay'], outcomes_df['success']))
        
        # Strategy 2: Lowest Latency (Best case mock simulation)
        # In real data, this would map the telemetry 'latency' to the outcome
        best_case_delays = outcomes_df['actual_delay'].sort_values().head(len(outcomes_df))
        results.append(self.calculate_metrics("Lowest_Latency", best_case_delays, outcomes_df['success']))

        df_results = pd.DataFrame(results)
        df_results.to_csv(self.output_file, index=False)
        return df_results

if __name__ == "__main__":
    try:
        engine = RPCBaselineEngine()
        
        # Toggle this to False when your real telemetry CSVs are ready
        USE_MOCK = True 

        if USE_MOCK:
            print("--- MODE: GENERATING MOCK DATA ---")
            telemetry, outcomes = engine.generate_mock_input()
        else:
            print("--- MODE: LOADING REAL DATA FROM FOLDER ---")
            telemetry = pd.read_csv(os.path.join(engine.data_dir, "rpc_telemetry.csv"))
            outcomes = pd.read_csv(os.path.join(engine.data_dir, "tx_outcomes.csv"))

        final_results = engine.run_evaluation(telemetry, outcomes)
        
        print(f"\nSUCCESS: Results saved to {engine.output_file}")
        print("\n--- FINAL RESULTS TABLE ---")
        print(final_results.to_string(index=False))

    except Exception as e:
        print(f"--- ERROR OCCURRED: {e} ---")
