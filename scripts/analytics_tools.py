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

def get_ev_counts_by_zipcode(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet', county: str = None) -> pd.DataFrame:
    """Return EV count per zip code. If county is provided, filter to that county only."""
    where_clause = f"WHERE County = '{county}'" if county else ""
    query = f"""
        SELECT 
            "Postal Code", 
            COUNT(*) as ev_count 
        FROM '{parquet_path}'
        {where_clause}
        GROUP BY "Postal Code"
        ORDER BY ev_count DESC
    """
    return duckdb.query(query).to_df()

def get_top_makes_and_models(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet', top_n: int = 10) -> pd.DataFrame:
    """Return the most popular EV makes and models."""
    query = f"""
        SELECT 
            Make, 
            Model, 
            COUNT(*) as count 
        FROM '{parquet_path}'
        GROUP BY Make, Model
        ORDER BY count DESC
        LIMIT {top_n}
    """
    return duckdb.query(query).to_df()

def get_bev_vs_phev_breakdown(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet', county: str = None) -> pd.DataFrame:
    """Return count of Battery Electric (BEV) vs Plug-in Hybrid (PHEV)."""
    where_clause = f"WHERE County = '{county}'" if county else ""
    query = f"""
        SELECT 
            "Electric Vehicle Type", 
            COUNT(*) as count 
        FROM '{parquet_path}'
        {where_clause}
        GROUP BY "Electric Vehicle Type"
    """
    return duckdb.query(query).to_df()

def get_cafv_eligibility_summary(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet') -> pd.DataFrame:
    """Return counts for each CAFV eligibility status."""
    query = f"""
        SELECT 
            "Clean Alternative Fuel Vehicle (CAFV) Eligibility" as eligibility, 
            COUNT(*) as count 
        FROM '{parquet_path}'
        GROUP BY eligibility
        ORDER BY count DESC
    """
    return duckdb.query(query).to_df()

def get_ev_range_statistics(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet', make: str = None) -> pd.DataFrame:
    """Return electric range statistics (avg, min, max) by make or overall."""
    where_clause = f"WHERE Make = '{make}'" if make else ""
    query = f"""
        SELECT 
            Make,
            AVG("Electric Range") as avg_range,
            MIN("Electric Range") as min_range,
            MAX("Electric Range") as max_range,
            COUNT(*) as vehicle_count
        FROM '{parquet_path}'
        {where_clause}
        GROUP BY Make
        HAVING avg_range > 0
        ORDER BY avg_range DESC
    """
    return duckdb.query(query).to_df()

def get_newest_registrations(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet', top_n: int = 20) -> pd.DataFrame:
    """Return the most recent model year vehicles."""
    query = f"""
        SELECT 
            Make, 
            Model, 
            "Model Year", 
            County 
        FROM '{parquet_path}'
        ORDER BY "Model Year" DESC
        LIMIT {top_n}
    """
    return duckdb.query(query).to_df()

def get_utility_provider_summary(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet') -> pd.DataFrame:
    """Return EV count grouped by Electric Utility provider."""
    query = f"""
        SELECT 
            "Electric Utility", 
            COUNT(*) as ev_count 
        FROM '{parquet_path}'
        GROUP BY "Electric Utility"
        ORDER BY ev_count DESC
    """
    return duckdb.query(query).to_df()

def get_county_growth_comparison(county1: str, county2: str, parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet') -> pd.DataFrame:
    """Compare adoption timelines of two counties side by side."""
    query = f"""
        SELECT 
            "Model Year", 
            County, 
            COUNT(*) as count 
        FROM '{parquet_path}'
        WHERE County IN ('{county1}', '{county2}')
        GROUP BY "Model Year", County
        ORDER BY "Model Year" ASC
    """
    return duckdb.query(query).to_df()

def get_adoption_growth_rate(parquet_path: str = '../data/processed/Electric_Vehicle_Population_Data.parquet') -> pd.DataFrame:
    """Return the EV adoption growth rate by model year."""
    query = f"""
        SELECT 
            "Model Year", 
            COUNT(*) as annual_registrations
        FROM '{parquet_path}'
        GROUP BY "Model Year"
        ORDER BY "Model Year" ASC
    """
    return duckdb.query(query).to_df()

if __name__ == "__main__":
    # Test our expanded tool suite
    print("--- Top 5 Counties ---")
    print(get_ev_counts_by_county().head())
    
    print("\n--- CAFV Eligibility Summary ---")
    print(get_cafv_eligibility_summary())
    
    print("\n--- Top 5 Makes/Models ---")
    print(get_top_makes_and_models(top_n=5))
    
    print("\n--- Utility Providers ---")
    print(get_utility_provider_summary().head())
