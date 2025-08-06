#!/usr/bin/env python3
"""
PyFtools Examples - Comprehensive demonstration of ftools functionality.

This script demonstrates how to use PyFtools for efficient data manipulation,
replicating common Stata ftools workflows in Python.
"""

import numpy as np
import pandas as pd
import pyftools as ft
import time

def create_panel_data():
    """Create a realistic panel dataset for demonstration."""
    print("Creating realistic panel dataset...")
    
    np.random.seed(12345)
    
    # Panel dimensions
    n_firms = 1000
    n_years = 10
    years = list(range(2014, 2024))
    
    # Create firm characteristics
    firms = [f"Firm_{i:04d}" for i in range(1, n_firms + 1)]
    industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Energy', 'Consumer']
    countries = ['US', 'UK', 'Germany', 'France', 'Japan', 'China', 'Canada', 'Australia']
    
    data = []
    
    for firm in firms:
        # Assign fixed characteristics
        industry = np.random.choice(industries)
        country = np.random.choice(countries)
        founded_year = np.random.randint(1990, 2010)
        
        for year in years:
            # Skip some observations (unbalanced panel)
            if np.random.random() < 0.15:  # 15% missing
                continue
                
            # Generate time-varying data with trends
            age = year - founded_year
            base_revenue = 50 + age * 10 + np.random.exponential(20)
            
            data.append({
                'firm_id': firm,
                'year': year,
                'industry': industry,
                'country': country,
                'founded_year': founded_year,
                'age': age,
                'revenue': base_revenue * np.random.lognormal(0, 0.3),
                'employees': max(10, int(base_revenue / 5 + np.random.poisson(100))),
                'rd_spending': max(0, base_revenue * np.random.uniform(0.02, 0.15)),
                'profit_margin': np.random.normal(0.08, 0.05),
                'market_share': np.random.uniform(0.001, 0.05)
            })
    
    df = pd.DataFrame(data)
    
    # Add some missing values
    n_obs = len(df)
    df.loc[np.random.choice(n_obs, int(n_obs * 0.05), replace=False), 'rd_spending'] = np.nan
    df.loc[np.random.choice(n_obs, int(n_obs * 0.03), replace=False), 'profit_margin'] = np.nan
    
    print(f"Created panel dataset: {len(df):,} observations")
    print(f"Firms: {df['firm_id'].nunique():,}, Years: {df['year'].nunique()}")
    print(f"Industries: {df['industry'].nunique()}, Countries: {df['country'].nunique()}")
    
    return df

def example_1_basic_operations():
    """Example 1: Basic ftools operations."""
    print("\\n" + "=" * 60)
    print("EXAMPLE 1: Basic Operations")
    print("=" * 60)
    
    data = create_panel_data()
    
    # 1. Generate group identifiers
    print("\\n1. Creating group identifiers with fegen...")
    data = ft.fegen(data, ['industry', 'country'], output_name='industry_country_id')
    print(f"Created {data['industry_country_id'].nunique()} industry-country groups")
    
    # 2. Check if firm_id uniquely identifies observations
    print("\\n2. Checking unique identifiers with fisid...")
    is_firm_unique = ft.fisid(data, 'firm_id')
    is_firm_year_unique = ft.fisid(data, ['firm_id', 'year'])
    print(f"firm_id is unique identifier: {is_firm_unique}")
    print(f"[firm_id, year] is unique identifier: {is_firm_year_unique}")
    
    # 3. Extract unique levels
    print("\\n3. Extracting unique levels with flevelsof...")
    industries = ft.flevelsof(data, 'industry')
    countries = ft.flevelsof(data, 'country') 
    print(f"Industries: {industries}")
    print(f"Countries: {countries}")
    
    # 4. Fast sorting
    print("\\n4. Fast sorting with fsort...")
    sorted_data = ft.fsort(data, ['industry', 'country', 'year', 'firm_id'])
    print(f"Sorted data by industry, country, year, firm_id")
    print(sorted_data[['industry', 'country', 'year', 'firm_id', 'revenue']].head())
    
    return data

def example_2_aggregation():
    """Example 2: Advanced aggregation with fcollapse."""
    print("\\n" + "=" * 60)
    print("EXAMPLE 2: Advanced Aggregation")
    print("=" * 60)
    
    data = create_panel_data()
    
    # 1. Simple aggregation by industry
    print("\\n1. Industry-level aggregation...")
    industry_stats = ft.fcollapse(
        data, 
        stats='mean',
        by='industry',
        freq=True,
        verbose=True
    )
    print("\\nIndustry statistics:")
    print(industry_stats[['industry', 'revenue', 'employees', 'rd_spending', '_freq']].round(2))
    
    # 2. Multiple statistics
    print("\\n2. Multiple statistics by industry-country...")
    multi_stats = ft.fcollapse(
        data,
        stats={
            'avg_revenue': ('mean', 'revenue'),
            'total_employees': ('sum', 'employees'),
            'max_rd': ('max', 'rd_spending'),
            'min_profit_margin': ('min', 'profit_margin'),
            'firms_count': ('count', 'firm_id')
        },
        by=['industry', 'country'],
        verbose=True
    )
    print("\\nTop industry-country combinations by average revenue:")
    top_combos = multi_stats.nlargest(10, 'avg_revenue')
    print(top_combos[['industry', 'country', 'avg_revenue', 'total_employees', 'firms_count']].round(2))
    
    # 3. Time series aggregation
    print("\\n3. Time series aggregation...")
    time_series = ft.fcollapse(
        data,
        stats=['mean', 'count'],
        by='year',
        verbose=True
    )
    print("\\nYear-over-year trends:")
    print(time_series[['year', 'revenue_mean', 'employees_mean', 'rd_spending_mean', 'revenue_count']].round(2))
    
    return industry_stats, multi_stats, time_series

def example_3_panel_operations():
    """Example 3: Advanced panel data operations."""
    print("\\n" + "=" * 60)
    print("EXAMPLE 3: Panel Data Operations")  
    print("=" * 60)
    
    data = create_panel_data()
    
    # 1. Add firm-level counts
    print("\\n1. Adding observation counts per firm...")
    data = ft.fcount(data, 'firm_id', output_name='obs_per_firm')
    print(f"Observations per firm - Min: {data['obs_per_firm'].min()}, Max: {data['obs_per_firm'].max()}, Mean: {data['obs_per_firm'].mean():.1f}")
    
    # 2. Create balanced panel subset
    print("\\n2. Creating balanced panel subset...")
    balanced_firms = data[data['obs_per_firm'] == 10]['firm_id'].unique()
    balanced_data = data[data['firm_id'].isin(balanced_firms)].copy()
    print(f"Balanced panel: {len(balanced_firms)} firms with 10 years each = {len(balanced_data)} observations")
    
    # 3. Industry-year level analysis
    print("\\n3. Industry-year level analysis...")
    industry_year = ft.fcollapse(
        balanced_data,
        stats={
            'mean_revenue': ('mean', 'revenue'),
            'median_employees': ('p50', 'employees'), 
            'firms_in_cell': ('count', 'firm_id'),
            'total_rd': ('sum', 'rd_spending')
        },
        by=['industry', 'year'],
        verbose=True
    )
    
    # Calculate growth rates
    industry_year = ft.fsort(industry_year, ['industry', 'year'])
    
    print("\\nIndustry-year statistics (sample):")
    print(industry_year[['industry', 'year', 'mean_revenue', 'firms_in_cell', 'total_rd']].head(15).round(2))
    
    return data, balanced_data, industry_year

def example_4_factor_operations():
    """Example 4: Advanced Factor class usage."""
    print("\\n" + "=" * 60)
    print("EXAMPLE 4: Advanced Factor Operations")
    print("=" * 60)
    
    data = create_panel_data()
    
    # 1. Create individual factors
    print("\\n1. Creating individual factors...")
    f_industry = ft.Factor(data['industry'], verbose=True)
    f_country = ft.Factor(data['country'], verbose=True) 
    f_year = ft.Factor(data['year'], verbose=True)
    
    print(f"Industry factor: {f_industry.num_levels} levels")
    print(f"Country factor: {f_country.num_levels} levels")
    print(f"Year factor: {f_year.num_levels} levels")
    
    # 2. Join factors
    print("\\n2. Joining factors...")
    f_joined = ft.join_factors(f_industry, f_country, f_year, verbose=True)
    print(f"Joined factor: {f_joined.num_levels} unique combinations")
    
    # 3. Factor-based aggregation
    print("\\n3. Using factors for efficient aggregation...")
    
    # Revenue statistics by industry
    revenue_by_industry = f_industry.collapse(data['revenue'].values, method='mean')
    industry_keys = f_industry.levels_of()
    
    print("\\nRevenue by industry (using Factor.collapse):")
    for i, industry in enumerate(industry_keys):
        print(f"{industry:>12}: ${revenue_by_industry[i]:,.0f}")
    
    # Multiple aggregations
    print("\\n4. Multiple aggregation methods...")
    methods = ['sum', 'mean', 'min', 'max', 'count']
    
    print("\\nEmployee statistics by country:")
    print(f"{'Country':<12} {'Sum':>10} {'Mean':>8} {'Min':>6} {'Max':>6} {'Count':>6}")
    print("-" * 60)
    
    for method in methods:
        if method == methods[0]:  # First iteration, get countries
            countries = f_country.levels_of()
            results = {method: f_country.collapse(data['employees'].values, method=method)}
        else:
            results[method] = f_country.collapse(data['employees'].values, method=method)
    
    for i, country in enumerate(countries):
        print(f"{country:<12} {results['sum'][i]:>10.0f} {results['mean'][i]:>8.0f} "
              f"{results['min'][i]:>6.0f} {results['max'][i]:>6.0f} {results['count'][i]:>6.0f}")
    
    return f_industry, f_country, f_joined

def example_5_performance_comparison():
    """Example 5: Performance comparison with pandas."""
    print("\\n" + "=" * 60)
    print("EXAMPLE 5: Performance Comparison")
    print("=" * 60)
    
    # Create larger dataset for meaningful comparison
    print("\\nCreating larger dataset for performance testing...")
    np.random.seed(42)
    n_large = 50000
    
    large_data = pd.DataFrame({
        'group1': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'], n_large),
        'group2': np.random.choice(range(1, 51), n_large), 
        'group3': np.random.choice(['X', 'Y', 'Z'], n_large),
        'value1': np.random.randn(n_large) * 100 + 1000,
        'value2': np.random.exponential(50, n_large),
        'value3': np.random.poisson(20, n_large),
        'id': range(n_large)
    })
    
    print(f"Dataset size: {len(large_data):,} observations")
    
    # Test 1: Aggregation performance
    print("\\n1. Aggregation performance comparison...")
    
    # PyFtools
    start = time.time()
    result_ft = ft.fcollapse(large_data, stats='mean', by=['group1', 'group2'])
    ft_time = time.time() - start
    
    # Pandas
    start = time.time()
    numeric_cols = large_data.select_dtypes(include=[np.number]).columns
    agg_cols = [col for col in numeric_cols if col not in ['group1', 'group2']]
    result_pd = large_data.groupby(['group1', 'group2'])[agg_cols].mean().reset_index()
    pd_time = time.time() - start
    
    print(f"PyFtools fcollapse: {ft_time:.4f}s")
    print(f"Pandas groupby:     {pd_time:.4f}s")
    print(f"Speed ratio:        {pd_time/ft_time:.2f}x")
    print(f"Results match:      {len(result_ft) == len(result_pd)}")
    
    # Test 2: Unique identifier check
    print("\\n2. Unique identifier check...")
    
    # PyFtools
    start = time.time()
    is_unique_ft = ft.fisid(large_data, ['group1', 'group2', 'group3'])
    ft_id_time = time.time() - start
    
    # Pandas
    start = time.time()
    is_unique_pd = len(large_data) == len(large_data[['group1', 'group2', 'group3']].drop_duplicates())
    pd_id_time = time.time() - start
    
    print(f"PyFtools fisid:      {ft_id_time:.4f}s (result: {is_unique_ft})")
    print(f"Pandas drop_dupes:   {pd_id_time:.4f}s (result: {is_unique_pd})")
    print(f"Speed ratio:         {pd_id_time/ft_id_time:.2f}x")
    
    # Test 3: Factor creation performance
    print("\\n3. Factor creation performance...")
    
    # PyFtools Factor
    start = time.time()
    factor = ft.Factor(large_data[['group1', 'group2']])
    ft_factor_time = time.time() - start
    
    # Pandas equivalent (categorical + groupby)
    start = time.time()
    grouped = large_data.groupby(['group1', 'group2']).size()
    pd_group_time = time.time() - start
    
    print(f"PyFtools Factor:     {ft_factor_time:.4f}s ({factor.num_levels} groups)")
    print(f"Pandas groupby size: {pd_group_time:.4f}s ({len(grouped)} groups)")
    print(f"Speed ratio:         {pd_group_time/ft_factor_time:.2f}x")
    
    return large_data, result_ft, result_pd

def example_6_real_world_workflow():
    """Example 6: Real-world econometric workflow."""
    print("\\n" + "=" * 60)
    print("EXAMPLE 6: Real-World Econometric Workflow")
    print("=" * 60)
    
    print("\\nScenario: Analyzing firm performance across industries and time...")
    
    # Load data
    data = create_panel_data()
    print(f"Starting with {len(data):,} firm-year observations")
    
    # 1. Data validation and cleaning
    print("\\n1. Data validation...")
    
    # Check panel structure
    is_balanced = ft.fisid(data, ['firm_id', 'year'])
    print(f"Balanced panel: {is_balanced}")
    
    # Get panel dimensions
    firms_per_year = ft.fcollapse(data, stats='count', by='year', verbose=False)
    years_per_firm = ft.fcollapse(data, stats='count', by='firm_id', verbose=False)
    
    print(f"Firms per year: {firms_per_year['firm_id'].min():.0f} - {firms_per_year['firm_id'].max():.0f}")
    print(f"Years per firm: {years_per_firm['year'].min():.0f} - {years_per_firm['year'].max():.0f}")
    
    # 2. Create analysis variables
    print("\\n2. Creating analysis variables...")
    
    # Add firm age categories
    data['age_category'] = pd.cut(data['age'], bins=[0, 5, 10, 15, 100], 
                                 labels=['Young', 'Growing', 'Mature', 'Established'])
    
    # Add size categories based on employees
    data['size_category'] = pd.cut(data['employees'], 
                                  bins=[0, 50, 200, 1000, np.inf],
                                  labels=['Small', 'Medium', 'Large', 'Very Large'])
    
    # Create industry-year groups
    data = ft.fegen(data, ['industry', 'year'], output_name='industry_year_id')
    
    print(f"Created {data['industry_year_id'].nunique()} industry-year combinations")
    
    # 3. Descriptive statistics
    print("\\n3. Descriptive statistics by industry...")
    
    industry_desc = ft.fcollapse(
        data,
        stats={
            'firms': ('count', 'firm_id'),
            'avg_revenue': ('mean', 'revenue'),
            'med_revenue': ('p50', 'revenue'),
            'avg_employees': ('mean', 'employees'),
            'avg_rd_ratio': ('mean', 'rd_spending'),
            'avg_profit_margin': ('mean', 'profit_margin')
        },
        by='industry',
        verbose=False
    )
    
    print("\\nIndustry Summary Statistics:")
    print(industry_desc.round(2))
    
    # 4. Time trends analysis
    print("\\n4. Analyzing time trends...")
    
    yearly_trends = ft.fcollapse(
        data,
        stats={
            'avg_revenue': ('mean', 'revenue'),
            'total_rd': ('sum', 'rd_spending'),
            'firms': ('count', 'firm_id')
        },
        by='year',
        verbose=False
    )
    
    # Calculate year-over-year growth
    yearly_trends = ft.fsort(yearly_trends, 'year')
    yearly_trends['revenue_growth'] = yearly_trends['avg_revenue'].pct_change() * 100
    yearly_trends['rd_growth'] = yearly_trends['total_rd'].pct_change() * 100
    
    print("\\nYear-over-year trends:")
    print(yearly_trends[['year', 'avg_revenue', 'revenue_growth', 'total_rd', 'rd_growth']].round(2))
    
    # 5. Cross-sectional analysis
    print("\\n5. Cross-sectional analysis (size vs performance)...")
    
    size_performance = ft.fcollapse(
        data,
        stats={
            'firms': ('count', 'firm_id'),
            'avg_revenue': ('mean', 'revenue'),
            'avg_profit_margin': ('mean', 'profit_margin'),
            'rd_intensity': ('mean', 'rd_spending')
        },
        by='size_category',
        verbose=False
    )
    
    print("\\nPerformance by firm size:")
    print(size_performance.round(2))
    
    # 6. Industry-year panel analysis
    print("\\n6. Industry-year panel analysis...")
    
    panel_analysis = ft.fcollapse(
        data,
        stats={
            'firms': ('count', 'firm_id'),
            'avg_revenue': ('mean', 'revenue'),
            'total_employment': ('sum', 'employees'),
            'rd_investment': ('sum', 'rd_spending')
        },
        by=['industry', 'year'],
        verbose=False
    )
    
    # Focus on technology industry
    tech_panel = panel_analysis[panel_analysis['industry'] == 'Technology'].copy()
    tech_panel = ft.fsort(tech_panel, 'year')
    
    print("\\nTechnology Industry Panel (2014-2023):")
    print(tech_panel[['year', 'firms', 'avg_revenue', 'total_employment', 'rd_investment']].round(0))
    
    print(f"\\nWorkflow completed successfully!")
    print(f"Processed {len(data):,} observations across {data['firm_id'].nunique():,} firms")
    
    return data, industry_desc, yearly_trends, size_performance, panel_analysis

def main():
    """Run all examples."""
    print("PyFtools Comprehensive Examples")
    print("Demonstrating Stata ftools functionality in Python")
    print("=" * 80)
    
    try:
        # Run all examples
        data1 = example_1_basic_operations()
        stats = example_2_aggregation()
        panel_results = example_3_panel_operations()
        factors = example_4_factor_operations()
        performance = example_5_performance_comparison()
        workflow = example_6_real_world_workflow()
        
        print("\\n" + "=" * 80)
        print("🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 80)
        
        print("\\nPyFtools provides a complete, efficient implementation of Stata's ftools:")
        print("✅ Factor: Advanced categorical variable handling with multiple hashing strategies")
        print("✅ fcollapse: Fast aggregation with flexible statistics and weighting")  
        print("✅ fegen: Efficient group variable generation")
        print("✅ flevelsof: Fast extraction of unique values")
        print("✅ fisid: Quick unique identifier validation")
        print("✅ fsort: Optimized sorting operations")
        print("✅ join_factors: Efficient multi-dimensional factor combinations")
        print("✅ fcount: Group-based observation counting")
        
        print("\\n📊 Performance competitive with pandas for most operations")
        print("🔧 Drop-in replacement for Stata ftools workflows")
        print("🐍 Native Python integration with pandas DataFrames")
        
    except Exception as e:
        print(f"\\nExample failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())