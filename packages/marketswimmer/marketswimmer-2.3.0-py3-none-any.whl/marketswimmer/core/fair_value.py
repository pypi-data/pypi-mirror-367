"""
Fair Value Calculator for MarketSwimmer

Implements a conservative fair value approach using:
1. 10-year average Owner Earnings as perpetual cash flow
2. 10-year Treasury rate as discount rate
3. Balance sheet adjustments (cash, investments, debt)
4. Per-share intrinsic value calculation
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict, Optional, Tuple
from pathlib import Path


class FairValueCalculator:
    """
    Calculate fair value using Owner Earnings and balance sheet analysis.
    
    Methodology:
    - Use 10-year average Owner Earnings as annual cash flow
    - Discount using 10-year Treasury rate
    - Add net cash and investment assets
    - Subtract debt to get enterprise value
    - Divide by shares outstanding for per-share value
    """
    
    def __init__(self):
        """Initialize the fair value calculator."""
        self.treasury_rate = None
        self.owner_earnings_data = None
        self.balance_sheet_data = None
        self.shares_outstanding = None
        self.company_name = None
        
    def get_10_year_treasury_rate(self) -> float:
        """
        Fetch current 10-year Treasury rate from FRED API.
        Falls back to reasonable default if API unavailable.
        
        Returns:
            float: 10-year Treasury rate as decimal (e.g., 0.045 for 4.5%)
        """
        try:
            # Try to fetch from Federal Reserve Economic Data (FRED)
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': 'DGS10',  # 10-Year Treasury Constant Maturity Rate
                'api_key': 'YOUR_FRED_API_KEY',  # Would need API key for production
                'limit': 1,
                'sort_order': 'desc',
                'file_type': 'json'
            }
            
            # For now, use a reasonable default since we don't have API key
            # In production, would implement proper API call
            default_rate = 0.045  # 4.5% as reasonable current estimate
            print(f"[RATE] Using default 10-year Treasury rate: {default_rate:.2%}")
            print(f"[INFO] To use live rates, configure FRED API key")
            
            self.treasury_rate = default_rate
            return default_rate
            
        except Exception as e:
            print(f"[WARNING] Could not fetch Treasury rate: {e}")
            default_rate = 0.045  # 4.5% fallback
            print(f"[RATE] Using fallback Treasury rate: {default_rate:.2%}")
            self.treasury_rate = default_rate
            return default_rate
    
    def load_owner_earnings_data(self, csv_file_path: str) -> bool:
        """
        Load owner earnings data from MarketSwimmer CSV output.
        
        Args:
            csv_file_path: Path to owner earnings CSV file
            
        Returns:
            bool: True if data loaded successfully
        """
        try:
            df = pd.read_csv(csv_file_path)
            print(f"[DATA] Loaded owner earnings from: {Path(csv_file_path).name}")
            print(f"[INFO] Data shape: {df.shape}")
            print(f"[INFO] Columns: {list(df.columns)}")
            
            # Ensure we have the required columns
            required_cols = ['Period', 'Owner Earnings']
            if not all(col in df.columns for col in required_cols):
                print(f"[ERROR] Missing required columns. Need: {required_cols}")
                return False
            
            # Clean and sort data
            df = df.dropna(subset=['Owner Earnings'])
            df = df.sort_values('Period', ascending=False)  # Most recent first
            
            self.owner_earnings_data = df
            print(f"[OK] Loaded {len(df)} periods of owner earnings data")
            
            # Show recent data for verification
            print(f"[PREVIEW] Recent owner earnings:")
            for _, row in df.head(5).iterrows():
                period = row['Period']
                earnings = row['Owner Earnings']
                if pd.notna(earnings):
                    print(f"   {period}: ${earnings:,.0f}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load owner earnings data: {e}")
            return False
    
    def calculate_average_owner_earnings(self, years: int = 10) -> Optional[float]:
        """
        Calculate average owner earnings over specified years.
        
        Args:
            years: Number of recent years to average
            
        Returns:
            float: Average annual owner earnings, or None if insufficient data
        """
        if self.owner_earnings_data is None:
            print(f"[ERROR] No owner earnings data loaded")
            return None
        
        # Get recent years of data
        recent_data = self.owner_earnings_data.head(years)
        valid_earnings = recent_data['Owner Earnings'].dropna()
        
        if len(valid_earnings) < 3:
            print(f"[ERROR] Insufficient data: only {len(valid_earnings)} valid periods")
            return None
        
        average_earnings = valid_earnings.mean()
        
        print(f"\n[ANALYSIS] Owner Earnings Analysis ({len(valid_earnings)} periods):")
        print(f"   Average: ${average_earnings:,.0f}")
        print(f"   Median:  ${valid_earnings.median():,.0f}")
        print(f"   Min:     ${valid_earnings.min():,.0f}")
        print(f"   Max:     ${valid_earnings.max():,.0f}")
        print(f"   Std Dev: ${valid_earnings.std():,.0f}")
        
        # Show the data used in calculation
        print(f"\n[DATA] Periods used in average:")
        for _, row in recent_data.iterrows():
            period = row['Period']
            earnings = row['Owner Earnings']
            if pd.notna(earnings):
                print(f"   {period}: ${earnings:,.0f}")
        
        return average_earnings
    
    def extract_balance_sheet_data(self, ticker: str) -> Dict[str, float]:
        """
        Automatically extract balance sheet data from downloaded XLSX files.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            dict: Balance sheet data with keys 'cash', 'debt', 'shares'
        """
        from pathlib import Path
        import pandas as pd
        
        balance_sheet_data = {
            'cash_and_equivalents': 0,
            'short_term_investments': 0,
            'total_debt': 0,
            'shares_outstanding': 0,
            'market_cap': 0
        }
        
        try:
            # Look for downloaded XLSX files for this ticker
            downloaded_files = Path("downloaded_files")
            if not downloaded_files.exists():
                print(f"[WARNING] No downloaded_files directory found")
                return balance_sheet_data
            
            # Find most recent file for this ticker
            ticker_files = list(downloaded_files.glob(f"*{ticker.lower()}*.xlsx"))
            if not ticker_files:
                print(f"[WARNING] No XLSX files found for ticker {ticker}")
                return balance_sheet_data
            
            # Use most recent file
            xlsx_file = sorted(ticker_files, key=lambda x: x.stat().st_mtime)[-1]
            print(f"[DATA] Extracting balance sheet data from: {xlsx_file.name}")
            
            # Create ExcelFile object to access all sheet names
            xl = pd.ExcelFile(xlsx_file)
            
            # Load balance sheet data
            try:
                # Try to load the balance sheet
                balance_sheet = pd.read_excel(xlsx_file, sheet_name='Balance Sheet, A')
                print(f"[OK] Loaded balance sheet with shape: {balance_sheet.shape}")
                
                # Extract cash and cash equivalents
                cash_terms = [
                    'cash and cash equivalents', 'cash & cash equivalents', 
                    'cash and short term investments', 'total cash'
                ]
                cash_value = self._extract_financial_item_from_df(balance_sheet, cash_terms)
                if cash_value:
                    balance_sheet_data['cash_and_equivalents'] = cash_value
                    print(f"[CASH] Found cash and equivalents: ${cash_value:,.0f}")
                
                # Extract short-term investments
                investment_terms = [
                    'short term investments', 'short-term investments',
                    'marketable securities', 'current investments'
                ]
                investment_value = self._extract_financial_item_from_df(balance_sheet, investment_terms)
                if investment_value:
                    balance_sheet_data['short_term_investments'] = investment_value
                    print(f"[INVESTMENTS] Found short-term investments: ${investment_value:,.0f}")
                
                # Extract total debt
                debt_terms = [
                    'total debt', 'long term debt (total)', 'long term debt',
                    'total borrowings', 'debt total'
                ]
                debt_value = self._extract_financial_item_from_df(balance_sheet, debt_terms)
                if debt_value:
                    balance_sheet_data['total_debt'] = debt_value
                    print(f"[DEBT] Found total debt: ${debt_value:,.0f}")
                
            except Exception as e:
                print(f"[WARNING] Could not load balance sheet: {e}")
            
            # Try to extract shares outstanding from multiple possible sheets
            try:
                shares_outstanding_found = False
                
                # FIRST try Balance Sheet - this has actual shares outstanding (not weighted averages)
                # Prioritize quarterly (most recent) over annual data
                for sheet_name in xl.sheet_names:
                    if 'balance sheet' in sheet_name.lower() and ', q' in sheet_name.lower():  # Quarterly first
                        balance_df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
                        print(f"[OK] Loaded balance sheet: {sheet_name}")
                        
                        shares_terms = [
                            'shares (common)', 'common shares', 'shares outstanding',
                            'common stock shares', 'outstanding shares'
                        ]
                        shares_value = self._extract_financial_item_from_df(balance_df, shares_terms)
                        if shares_value:
                            # Convert to actual shares (assuming millions)
                            if shares_value < 100_000:  # Likely in millions
                                shares_value = shares_value * 1_000_000
                            balance_sheet_data['shares_outstanding'] = shares_value
                            print(f"[SHARES] Found shares outstanding in quarterly balance sheet: {shares_value:,.0f}")
                            shares_outstanding_found = True
                            break
                
                # If not found in quarterly, try annual balance sheet
                if not shares_outstanding_found:
                    for sheet_name in xl.sheet_names:
                        if 'balance sheet' in sheet_name.lower() and ', a' in sheet_name.lower():  # Annual fallback
                            balance_df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
                            print(f"[OK] Loaded balance sheet: {sheet_name}")
                            
                            shares_terms = [
                                'shares (common)', 'common shares', 'shares outstanding',
                                'common stock shares', 'outstanding shares'
                            ]
                            shares_value = self._extract_financial_item_from_df(balance_df, shares_terms)
                            if shares_value:
                                # Convert to actual shares (assuming millions)
                                if shares_value < 100_000:  # Likely in millions
                                    shares_value = shares_value * 1_000_000
                                balance_sheet_data['shares_outstanding'] = shares_value
                                print(f"[SHARES] Found shares outstanding in annual balance sheet: {shares_value:,.0f}")
                                shares_outstanding_found = True
                                break
                
                # If not found in balance sheet, fall back to Income Statement (weighted averages)
                if not shares_outstanding_found:
                    for sheet_name in xl.sheet_names:
                        if 'income statement' in sheet_name.lower() and ', a' in sheet_name.lower():
                            income_df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
                            print(f"[OK] Loaded income statement sheet: {sheet_name}")
                            
                            shares_terms = [
                                'shares (diluted, weighted)', 'shares (basic, weighted)', 
                                'shares (diluted, average)', 'weighted average shares outstanding',
                                'shares outstanding', 'common shares outstanding'
                            ]
                            shares_value = self._extract_financial_item_from_df(income_df, shares_terms)
                            if shares_value:
                                # Convert to actual shares (assuming millions)
                                if shares_value < 100_000:  # Likely in millions
                                    shares_value = shares_value * 1_000_000
                                balance_sheet_data['shares_outstanding'] = shares_value
                                print(f"[SHARES] Found shares outstanding in income statement (fallback): {shares_value:,.0f}")
                                shares_outstanding_found = True
                                break
                                break
                
                # If still not found, try metrics ratios sheet
                if not shares_outstanding_found:
                    for sheet_name in xl.sheet_names:
                        if 'metrics' in sheet_name.lower() and ', a' in sheet_name.lower():
                            metrics_df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
                            print(f"[OK] Loaded metrics sheet: {sheet_name}")
                            
                            shares_terms = [
                                'shares outstanding', 'shares (diluted)', 'weighted shares outstanding',
                                'shares outstanding (millions)', 'common shares outstanding'
                            ]
                            shares_value = self._extract_financial_item_from_df(metrics_df, shares_terms)
                            if shares_value:
                                # Convert to actual shares (assuming millions)
                                if shares_value < 100_000:  # Likely in millions
                                    shares_value = shares_value * 1_000_000
                                balance_sheet_data['shares_outstanding'] = shares_value
                                print(f"[SHARES] Found shares outstanding in metrics: {shares_value:,.0f}")
                                shares_outstanding_found = True
                                break
                
            except Exception as e:
                print(f"[WARNING] Could not load metrics sheet: {e}")
            
            # Calculate net cash position
            net_cash = (balance_sheet_data['cash_and_equivalents'] + 
                       balance_sheet_data['short_term_investments'] - 
                       balance_sheet_data['total_debt'])
            
            print(f"\n[SUMMARY] Balance Sheet Summary:")
            print(f"   Cash & Equivalents: ${balance_sheet_data['cash_and_equivalents']:,.0f}")
            print(f"   Short-term Investments: ${balance_sheet_data['short_term_investments']:,.0f}")
            print(f"   Total Debt: ${balance_sheet_data['total_debt']:,.0f}")
            print(f"   Net Cash Position: ${net_cash:,.0f}")
            if balance_sheet_data['shares_outstanding']:
                print(f"   Shares Outstanding: {balance_sheet_data['shares_outstanding']:,.0f}")
            if balance_sheet_data['market_cap']:
                print(f"   Market Cap: ${balance_sheet_data['market_cap']:,.0f}")
            
            return balance_sheet_data
            
        except Exception as e:
            print(f"[ERROR] Failed to extract balance sheet data: {e}")
            return balance_sheet_data
    
    def _extract_financial_item_from_df(self, df: pd.DataFrame, search_terms: list) -> Optional[float]:
        """
        Extract a financial item from a DataFrame using search terms.
        
        Args:
            df: DataFrame to search
            search_terms: List of terms to search for
            
        Returns:
            float: Most recent value found, or None
        """
        if df is None or df.empty:
            return None
        
        # Try different approaches to find the data
        for search_term in search_terms:
            # Search in first column (typically contains line item names)
            if len(df.columns) > 0:
                first_col = df.iloc[:, 0]
                for idx, item in enumerate(first_col):
                    if pd.notna(item) and search_term.lower() in str(item).lower():
                        # Found the row, get the most recent value (typically FIRST data column, not last)
                        row_data = df.iloc[idx]
                        
                        # Look for numeric columns starting from LEFT (most recent data)
                        for col in df.columns[1:]:  # Start from first data column (skip labels)
                            value = row_data[col]
                            if pd.notna(value) and value != '—':
                                if isinstance(value, (int, float)):
                                    return float(value)
                                elif isinstance(value, str):
                                    # Try to parse string value
                                    clean_value = str(value).replace(',', '').replace('$', '').strip()
                                    if clean_value.replace('.', '').replace('-', '').isdigit():
                                        return float(clean_value)
        
        return None

    def get_balance_sheet_adjustments(self, balance_sheet_file: Optional[str] = None) -> Dict[str, float]:
        """
        Extract balance sheet items for fair value adjustments.
        
        Args:
            balance_sheet_file: Optional path to balance sheet data
            
        Returns:
            dict: Balance sheet adjustments with keys like 'cash', 'investments', 'debt'
        """
        adjustments = {
            'cash_and_equivalents': 0,
            'short_term_investments': 0,
            'equity_investments': 0,
            'total_debt': 0,
            'net_adjustments': 0
        }
        
        if balance_sheet_file and Path(balance_sheet_file).exists():
            try:
                # Implementation would parse balance sheet data
                # For now, return placeholder structure
                print(f"[INFO] Balance sheet analysis not yet implemented")
                print(f"[TIP] Manually input cash, investments, and debt values")
            except Exception as e:
                print(f"[WARNING] Could not load balance sheet data: {e}")
        
        return adjustments
    
    def calculate_fair_value_auto(self, 
                                 ticker: str,
                                 average_owner_earnings: float,
                                 discount_rate: Optional[float] = None,
                                 growth_rate: float = 0.02,
                                 years_to_project: int = 10,
                                 terminal_multiple: float = 15.0) -> Dict[str, float]:
        """
        Calculate fair value with automatic balance sheet data extraction.
        
        Args:
            ticker: Stock ticker symbol
            average_owner_earnings: Annual owner earnings to project
            discount_rate: Discount rate (uses 10Y Treasury if None)
            growth_rate: Annual growth rate for owner earnings
            years_to_project: Years to project cash flows
            terminal_multiple: P/E multiple for terminal value
            
        Returns:
            dict: Valuation components and final fair value
        """
        print(f"\n[AUTO] Extracting balance sheet data for {ticker.upper()}...")
        balance_data = self.extract_balance_sheet_data(ticker)
        
        # Calculate total cash and investments
        total_cash = balance_data['cash_and_equivalents'] + balance_data['short_term_investments']
        total_debt = balance_data['total_debt']
        shares_outstanding = balance_data['shares_outstanding'] if balance_data['shares_outstanding'] > 0 else None
        
        print(f"[AUTO] Using extracted data:")
        print(f"   Total Cash & Investments: ${total_cash:,.0f}")
        print(f"   Total Debt: ${total_debt:,.0f}")
        if shares_outstanding:
            print(f"   Shares Outstanding: {shares_outstanding:,.0f}")
        else:
            print("[WARNING] Shares outstanding not found in downloaded data")
            print("Per-share fair value will not be calculated")
        
        # Use the regular fair value calculation with extracted data
        return self.calculate_fair_value(
            average_owner_earnings=average_owner_earnings,
            discount_rate=discount_rate,
            growth_rate=growth_rate,
            years_to_project=years_to_project,
            terminal_multiple=terminal_multiple,
            cash_and_investments=total_cash,
            total_debt=total_debt,
            shares_outstanding=shares_outstanding
        )
    
    def calculate_fair_value(self, 
                           average_owner_earnings: float,
                           discount_rate: Optional[float] = None,
                           growth_rate: float = 0.0,
                           years_to_project: int = 10,
                           terminal_multiple: float = 15.0,
                           cash_and_investments: float = 0,
                           total_debt: float = 0,
                           shares_outstanding: Optional[float] = None) -> Dict[str, float]:
        """
        Calculate fair value using DCF methodology.
        
        Args:
            average_owner_earnings: Annual owner earnings to project
            discount_rate: Discount rate (uses 10Y Treasury if None)
            growth_rate: Annual growth rate for owner earnings
            years_to_project: Years to project cash flows
            terminal_multiple: P/E multiple for terminal value
            cash_and_investments: Net cash and investment assets
            total_debt: Total debt to subtract
            shares_outstanding: Shares outstanding for per-share value
            
        Returns:
            dict: Valuation components and final fair value
        """
        if discount_rate is None:
            discount_rate = self.get_10_year_treasury_rate()
        
        print(f"\n[VALUATION] Fair Value Calculation")
        print(f"=" * 50)
        print(f"Base Owner Earnings: ${average_owner_earnings:,.0f}")
        print(f"Growth Rate: {growth_rate:.1%}")
        print(f"Discount Rate: {discount_rate:.2%}")
        print(f"Projection Period: {years_to_project} years")
        print(f"Terminal Multiple: {terminal_multiple}x")
        
        # Project future cash flows
        cash_flows = []
        for year in range(1, years_to_project + 1):
            future_earnings = average_owner_earnings * ((1 + growth_rate) ** year)
            present_value = future_earnings / ((1 + discount_rate) ** year)
            cash_flows.append({
                'year': year,
                'future_earnings': future_earnings,
                'present_value': present_value
            })
        
        # Calculate terminal value
        terminal_earnings = average_owner_earnings * ((1 + growth_rate) ** years_to_project)
        terminal_value = terminal_earnings * terminal_multiple
        terminal_pv = terminal_value / ((1 + discount_rate) ** years_to_project)
        
        # Sum up enterprise value
        cash_flow_pv = sum(cf['present_value'] for cf in cash_flows)
        enterprise_value = cash_flow_pv + terminal_pv
        
        # Adjust for balance sheet items
        equity_value = enterprise_value + cash_and_investments - total_debt
        
        print(f"\n[CASH FLOWS] Projected Owner Earnings:")
        for cf in cash_flows[:5]:  # Show first 5 years
            print(f"   Year {cf['year']}: ${cf['future_earnings']:,.0f} (PV: ${cf['present_value']:,.0f})")
        if len(cash_flows) > 5:
            print(f"   ... {len(cash_flows) - 5} more years")
        
        print(f"\n[TERMINAL] Terminal Value:")
        print(f"   Terminal Earnings: ${terminal_earnings:,.0f}")
        print(f"   Terminal Value: ${terminal_value:,.0f}")
        print(f"   Terminal PV: ${terminal_pv:,.0f}")
        
        print(f"\n[ENTERPRISE] Enterprise Value:")
        print(f"   Cash Flow PV: ${cash_flow_pv:,.0f}")
        print(f"   Terminal PV: ${terminal_pv:,.0f}")
        print(f"   Enterprise Value: ${enterprise_value:,.0f}")
        
        print(f"\n[ADJUSTMENTS] Balance Sheet:")
        print(f"   Cash & Investments: +${cash_and_investments:,.0f}")
        print(f"   Total Debt: -${total_debt:,.0f}")
        print(f"   Equity Value: ${equity_value:,.0f}")
        
        # Calculate per-share value if shares provided
        per_share_value = None
        if shares_outstanding and shares_outstanding > 0:
            per_share_value = equity_value / shares_outstanding
            print(f"\n[PER SHARE] Valuation:")
            print(f"   Shares Outstanding: {shares_outstanding:,.0f}")
            print(f"   Fair Value per Share: ${per_share_value:,.2f}")
        
        return {
            'average_owner_earnings': average_owner_earnings,
            'discount_rate': discount_rate,
            'growth_rate': growth_rate,
            'cash_flow_pv': cash_flow_pv,
            'terminal_pv': terminal_pv,
            'enterprise_value': enterprise_value,
            'cash_and_investments': cash_and_investments,
            'total_debt': total_debt,
            'equity_value': equity_value,
            'shares_outstanding': shares_outstanding,
            'fair_value_per_share': per_share_value,
            'terminal_multiple': terminal_multiple,
            'years_projected': years_to_project
        }
    
    def create_scenario_analysis(self, 
                               average_owner_earnings: float,
                               shares_outstanding: Optional[float] = None,
                               cash_and_investments: float = 0,
                               total_debt: float = 0) -> pd.DataFrame:
        """
        Create scenario analysis with different growth rates and discount rates.
        
        Args:
            average_owner_earnings: Base annual owner earnings
            shares_outstanding: Shares outstanding for per-share calculations
            cash_and_investments: Net cash and investments
            total_debt: Total debt
            
        Returns:
            DataFrame: Scenario analysis results
        """
        scenarios = []
        
        # Define scenarios
        scenario_configs = [
            {'name': 'Conservative', 'growth': 0.0, 'discount': 0.06, 'terminal_multiple': 12},
            {'name': 'Base Case', 'growth': 0.02, 'discount': 0.045, 'terminal_multiple': 15},
            {'name': 'Optimistic', 'growth': 0.04, 'discount': 0.04, 'terminal_multiple': 18},
            {'name': 'Pessimistic', 'growth': -0.01, 'discount': 0.07, 'terminal_multiple': 10}
        ]
        
        print(f"\n[SCENARIOS] Fair Value Scenario Analysis")
        print(f"=" * 60)
        
        for config in scenario_configs:
            result = self.calculate_fair_value(
                average_owner_earnings=average_owner_earnings,
                discount_rate=config['discount'],
                growth_rate=config['growth'],
                terminal_multiple=config['terminal_multiple'],
                cash_and_investments=cash_and_investments,
                total_debt=total_debt,
                shares_outstanding=shares_outstanding
            )
            
            scenario = {
                'Scenario': config['name'],
                'Growth Rate': f"{config['growth']:.1%}",
                'Discount Rate': f"{config['discount']:.1%}",
                'Terminal Multiple': f"{config['terminal_multiple']}x",
                'Enterprise Value': result['enterprise_value'],
                'Equity Value': result['equity_value']
            }
            
            if result['fair_value_per_share']:
                scenario['Fair Value per Share'] = result['fair_value_per_share']
            
            scenarios.append(scenario)
            
            print(f"\n{config['name'].upper()} SCENARIO:")
            print(f"   Growth: {config['growth']:.1%}, Discount: {config['discount']:.1%}, Terminal: {config['terminal_multiple']}x")
            print(f"   Equity Value: ${result['equity_value']:,.0f}")
            if result['fair_value_per_share']:
                print(f"   Per Share: ${result['fair_value_per_share']:,.2f}")
        
        return pd.DataFrame(scenarios)
    
    def save_valuation_report(self, 
                            valuation_results: Dict,
                            scenario_df: pd.DataFrame,
                            output_file: str):
        """
        Save comprehensive valuation report to file.
        
        Args:
            valuation_results: Base case valuation results
            scenario_df: Scenario analysis DataFrame
            output_file: Output file path
        """
        try:
            with open(output_file, 'w') as f:
                f.write("MARKETSWIMMER FAIR VALUE ANALYSIS\n")
                f.write("=" * 50 + "\n\n")
                
                # Base case summary
                f.write("BASE CASE VALUATION:\n")
                f.write(f"Average Owner Earnings: ${valuation_results['average_owner_earnings']:,.0f}\n")
                f.write(f"Discount Rate: {valuation_results['discount_rate']:.2%}\n")
                f.write(f"Growth Rate: {valuation_results['growth_rate']:.1%}\n")
                f.write(f"Enterprise Value: ${valuation_results['enterprise_value']:,.0f}\n")
                f.write(f"Equity Value: ${valuation_results['equity_value']:,.0f}\n")
                
                if valuation_results.get('fair_value_per_share'):
                    f.write(f"Fair Value per Share: ${valuation_results['fair_value_per_share']:,.2f}\n")
                else:
                    f.write("Fair Value per Share: Not available (shares outstanding not provided)\n")
                
                f.write("\n\nSCENARIO ANALYSIS:\n")
                f.write(scenario_df.to_string(index=False))
                f.write("\n\n")
                
                # Methodology notes
                f.write("METHODOLOGY:\n")
                f.write("1. Calculate 10-year average of Owner Earnings\n")
                f.write("2. Project future cash flows with growth assumptions\n")
                f.write("3. Discount to present value using 10-year Treasury rate\n")
                f.write("4. Add terminal value using earnings multiple\n")
                f.write("5. Adjust for net cash and debt\n")
                f.write("6. Calculate per-share fair value\n")
            
            print(f"\n[SAVE] Valuation report saved to: {output_file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to save report: {e}")


def main():
    """Example usage of FairValueCalculator."""
    calculator = FairValueCalculator()
    
    # Example with dummy data
    print("MarketSwimmer Fair Value Calculator")
    print("=" * 40)
    
    # This would normally load from MarketSwimmer output
    # calculator.load_owner_earnings_data("data/owner_earnings_annual_AAPL.csv")
    
    # Example calculation
    example_earnings = 50_000_000_000  # $50B annual owner earnings
    example_shares = 15_000_000_000    # 15B shares
    example_cash = 100_000_000_000     # $100B cash
    example_debt = 20_000_000_000      # $20B debt
    
    results = calculator.calculate_fair_value(
        average_owner_earnings=example_earnings,
        shares_outstanding=example_shares,
        cash_and_investments=example_cash,
        total_debt=example_debt
    )
    
    scenarios = calculator.create_scenario_analysis(
        average_owner_earnings=example_earnings,
        shares_outstanding=example_shares,
        cash_and_investments=example_cash,
        total_debt=example_debt
    )
    
    print(f"\nFinal Fair Value: ${results['fair_value_per_share']:,.2f} per share")


if __name__ == "__main__":
    main()
