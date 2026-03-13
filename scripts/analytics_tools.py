import pandas as pd
import duckdb

def get_ev_counts_by_county(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet') -> pd.DataFrame:
    """
    Deterministically retrieve the number of EVs in each county.
    Uses DuckDB to run highly efficient SQL directly on the Parquet file.
    """
    query = f"""
        SELECT 
            County, 
            COUNT(*) as ev_count 
        FROM '{parquet_path}'
        GROUP BY County
        ORDER BY ev_count DESC
    """
    # DuckDB seamlessly queries parquet without loading it all into memory first
    return duckdb.query(query).to_df()

def get_adoption_growth_rate(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet', zipcode: str = None) -> pd.DataFrame:
    """
    Calculate adoption velocity or distribution over time.
    """
    # Note: Column names with spaces need to be enclosed in double quotes in DuckDB SQL
    where_clause = f"WHERE \"Postal Code\" = '{zipcode}'" if zipcode else ""
    query = f"""
        SELECT
            "Model Year",
            COUNT(*) as vehicle_count
        FROM '{parquet_path}'
        {where_clause}
        GROUP BY "Model Year"
        ORDER BY "Model Year" ASC
    """
    return duckdb.query(query).to_df()

if __name__ == "__main__":
    # Test our deterministic tools
    print("Top 5 Counties by EV Count:")
    try:
        print(get_ev_counts_by_county().head())
    except Exception as e:
        print(f"Error executing sample queries: {e}")
