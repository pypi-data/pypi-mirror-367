import pandas as pd
import matplotlib
# Set non-interactive backend for headless operation - must be before pyplot import
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# Ensure matplotlib is in non-interactive mode
plt.ioff()
import seaborn as sns
import numpy as np
from datetime import datetime
import os
import glob
import re

def setup_plotting_style():
    """Set up a professional plotting style."""
    plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (15, 10)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9

def detect_ticker_symbol():
    """Detect the ticker symbol from the most recent XLSX file."""
    try:
        # Check downloaded_files folder for recent files
        xlsx_files = glob.glob("./downloaded_files/*.xlsx")
        if xlsx_files:
            # Get the most recent file
            latest_file = max(xlsx_files, key=os.path.getmtime)
            filename = os.path.basename(latest_file)
            
            # Extract ticker from filename like "financials_export_brkb_2025_08_02_221804.xlsx"
            if 'financials_export_' in filename:
                parts = filename.split('_')
                if len(parts) >= 3:
                    ticker = parts[2].upper()
                    # Handle special cases like BRK.B
                    if ticker == 'BRKB':
                        ticker = 'BRK.B'
                    return ticker
        
        # Fallback: try to detect from data patterns
        return "TICKER"
    except:
        return "TICKER"

def create_shares_outstanding_analysis(ticker, output_dir='./analysis_output'):
    """
    Create comprehensive analysis of shares outstanding data from downloaded financial statements.
    
    Args:
        ticker (str): Stock ticker symbol
        output_dir (str): Directory to save analysis charts
        
    Returns:
        bool: True if analysis was successful, False otherwise
    """
    def parse_quarter_date(date_str):
        """Convert quarter strings like "Jun '25" to readable format"""
        try:
            if "'" in date_str:
                # Handle formats like "Jun '25", "Mar '24"
                month_abbr, year_abbr = date_str.split(" '")
                year = int("20" + year_abbr) if int(year_abbr) < 50 else int("19" + year_abbr)
                
                # Convert month abbreviation to quarter
                month_to_quarter = {
                    'Mar': 'Q1', 'Jun': 'Q2', 'Sep': 'Q3', 'Dec': 'Q4'
                }
                quarter = month_to_quarter.get(month_abbr, 'Q1')
                return f"{quarter} {year}"
            else:
                return date_str
        except:
            return date_str
    
    try:
        # Find the most recent downloaded file for the ticker
        # Normalize ticker by replacing dots with underscores (e.g., BRK.B -> brk_b)
        normalized_ticker = ticker.lower().replace('.', '_')
        pattern = f'./downloaded_files/*{normalized_ticker}*.xlsx'
        xlsx_files = glob.glob(pattern)
        
        if not xlsx_files:
            print(f"No downloaded files found for ticker {ticker} (searched for pattern: {pattern})")
            return False
            
        # Get the most recent file
        latest_file = max(xlsx_files, key=os.path.getmtime)
        print(f"Analyzing shares data from: {os.path.basename(latest_file)}")
        
        # Read Excel file
        xl = pd.ExcelFile(latest_file)
        
        # Initialize data storage
        shares_data = {}
        issuance_data = {}  # For share issuance (positive bars)
        repurchase_data = {}  # For share repurchase (negative bars)
        debt_issuance_data = {}  # For debt issuance (positive bars)
        debt_repayment_data = {}  # For debt repayment (negative bars)
        debt_metrics_data = {}  # For debt level metrics (lines on debt chart)
        quarterly_data = []
        annual_data = []
        
        # Store stock price data for converting cash flow amounts to share counts
        stock_price_data = {}  # Will store {date: price} mapping
        
        # Process each sheet - Use quarterly balance sheet AND cash flow data
        for sheet_name in xl.sheet_names:
            # Process quarterly balance sheet data for share counts and quarterly cash flow for issuance
            if not ('q' in sheet_name.lower() and ('balance' in sheet_name.lower() or 'cash' in sheet_name.lower())):
                print(f"Skipping sheet '{sheet_name}' - only using quarterly balance sheet and cash flow data")
                continue
                
            try:
                df = pd.read_excel(latest_file, sheet_name=sheet_name)
                print(f"Processing quarterly sheet: {sheet_name}")
                
                # Look for share-related metrics and debt activities in quarterly data
                share_keywords = ['share', 'outstanding', 'diluted', 'basic', 'common', 'weighted', 'stock', 'issuance', 'issued', 'repurchase', 'buyback']
                debt_keywords = ['debt', 'borrowing', 'loan', 'bond', 'credit', 'financing']
                all_keywords = share_keywords + debt_keywords
                exclude_keywords = ['equity', 'liabilit', 'asset', 'book', 'value', 'price', 'market', 'treasury', 'common stock (net)', 'common stock net', 'financing cash flow']
                
                # Find rows with relevant keywords but exclude unwanted metrics
                relevant_rows = df[df.iloc[:, 0].astype(str).str.contains('|'.join(all_keywords), case=False, na=False)]
                if not relevant_rows.empty:
                    # Filter out unwanted metrics
                    filtered_rows = relevant_rows[~relevant_rows.iloc[:, 0].astype(str).str.contains('|'.join(re.escape(word) for word in exclude_keywords), case=False, na=False)]
                    share_rows = filtered_rows
                
                if not share_rows.empty:
                    print(f"Found {len(share_rows)} relevant metrics in {sheet_name}")
                    for idx, row in share_rows.iterrows():
                        metric_name = str(row.iloc[0]).strip()
                        
                        # Additional filtering to ensure we only get relevant metrics
                        if any(exclude_word in metric_name.lower() for exclude_word in ['equity', 'liabilit', 'asset', 'book', 'value', 'price', 'market', 'per share', 'ratio', 'treasury', 'common stock (net)', 'common stock net', 'financing cash flow', 'financing']):
                            continue
                            
                        # Process relevant metric
                        values = row.iloc[1:].dropna()
                        
                        # Determine the type of metric
                        is_share_issuance = any(keyword in metric_name.lower() for keyword in ['issuance', 'issued']) and 'share' in metric_name.lower()
                        is_share_repurchase = any(keyword in metric_name.lower() for keyword in ['repurchase', 'buyback']) and 'share' in metric_name.lower()
                        is_debt_issuance = any(keyword in metric_name.lower() for keyword in ['debt', 'borrowing', 'loan', 'bond']) and any(keyword in metric_name.lower() for keyword in ['issuance', 'issued', 'proceeds'])
                        is_debt_repayment = any(keyword in metric_name.lower() for keyword in ['debt', 'borrowing', 'loan', 'bond']) and any(keyword in metric_name.lower() for keyword in ['repayment', 'payment', 'retire'])
                        is_debt_metric = any(keyword in metric_name.lower() for keyword in ['long term debt', 'current part of debt', 'net debt', 'total debt', 'debt total'])
                        is_share_count = any(keyword in metric_name.lower() for keyword in ['outstanding', 'diluted', 'basic', 'common shares']) and not is_debt_metric
                        
                        # Handle combined metrics like "Issuance/Purchase of Shares" 
                        is_combined_share_activity = 'issuance' in metric_name.lower() and ('purchase' in metric_name.lower() or 'repurchase' in metric_name.lower())
                        
                        # Convert to numeric and store
                        numeric_values = []
                        dates = []
                        
                        for i, val in enumerate(values):
                            try:
                                if pd.notna(val) and str(val) != '—' and str(val) != '':
                                    # Handle different number formats
                                    if isinstance(val, str):
                                        # Remove commas, dollar signs, and other formatting
                                        clean_val = str(val).replace(',', '').replace('$', '').replace('%', '').strip()
                                        if clean_val and clean_val != '—':
                                            numeric_val = float(clean_val)
                                        else:
                                            continue
                                    else:
                                        numeric_val = float(val)
                                    
                                    # Apply appropriate threshold based on metric type
                                    should_include = False
                                    if is_share_issuance or is_share_repurchase:
                                        should_include = abs(numeric_val) > 1  # Very low threshold for share activities
                                    elif is_debt_issuance or is_debt_repayment:
                                        should_include = abs(numeric_val) > 10  # Low threshold for debt activities
                                    elif is_share_count:
                                        should_include = numeric_val > 1000  # Higher threshold for share counts
                                    else:
                                        should_include = numeric_val > 100  # Default threshold
                                    
                                    if should_include:
                                        numeric_values.append(numeric_val)
                                        # Get the actual column header as date
                                        if i + 1 < len(df.columns):
                                            date_str = str(df.columns[i + 1])
                                            # Parse and format the date
                                            formatted_date = parse_quarter_date(date_str)
                                            dates.append(formatted_date)
                                        else:
                                            dates.append(f"Period_{i+1}")
                                        
                            except (ValueError, TypeError):
                                continue
                        
                        if numeric_values:
                            key = f"{sheet_name}_{metric_name}"
                            
                            # Handle combined share activity metrics (like "Issuance/Purchase of Shares")
                            if is_combined_share_activity:
                                # Split positive and negative values based on cash flow direction
                                positive_values = []
                                positive_dates = []
                                negative_values = []
                                negative_dates = []
                                
                                # Note: Share issuance/repurchase bars are currently disabled for cleaner analysis
                                print(f"  Found combined metric '{metric_name}' - bars disabled for cleaner chart")
                                
                                for value, date in zip(numeric_values, dates):
                                    if value > 0:  # Positive = Net Issuance
                                        positive_values.append(value)
                                        positive_dates.append(date)
                                    elif value < 0:  # Negative = Net Repurchase
                                        negative_values.append(abs(value))  # Store as positive amount
                                        negative_dates.append(date)
                                
                                # Store positive cash flows as issuance (for potential future use)
                                if positive_values:
                                    issuance_data[f"{key}_positive"] = {
                                        'values': positive_values,
                                        'dates': positive_dates,
                                        'sheet': sheet_name,
                                        'metric': f"{metric_name} (Issuance)"
                                    }
                                
                                # Store negative cash flows as repurchase (for potential future use)
                                if negative_values:
                                    repurchase_data[f"{key}_negative"] = {
                                        'values': [-v for v in negative_values],  # Make negative for chart display
                                        'dates': negative_dates,
                                        'sheet': sheet_name,
                                        'metric': f"{metric_name} (Repurchase)"
                                    }
                            
                            # Store in appropriate data structure for single-purpose metrics
                            elif is_share_issuance:
                                issuance_data[key] = {
                                    'values': numeric_values,
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            elif is_share_repurchase:
                                repurchase_data[key] = {
                                    'values': [-abs(v) for v in numeric_values],  # Make negative for repurchases
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            elif is_debt_issuance:
                                debt_issuance_data[key] = {
                                    'values': numeric_values,
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            elif is_debt_repayment:
                                debt_repayment_data[key] = {
                                    'values': [-abs(v) for v in numeric_values],  # Make negative for repayments
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            elif is_debt_metric:
                                debt_metrics_data[key] = {
                                    'values': numeric_values,
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            else:
                                shares_data[key] = {
                                    'values': numeric_values,
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            
                            # Store for time series analysis
                            if 'q' in sheet_name.lower():
                                quarterly_data.extend([(d, v, metric_name) for d, v in zip(dates, numeric_values)])
                            else:
                                annual_data.extend([(d, v, metric_name) for d, v in zip(dates, numeric_values)])
                                
            except Exception as e:
                print(f"Warning: Could not process sheet {sheet_name}: {str(e)}")
                continue
        
        if not shares_data and not issuance_data and not repurchase_data and not debt_issuance_data and not debt_repayment_data and not debt_metrics_data:
            print(f"No relevant share or debt data found for {ticker}")
            return False
        
        # Extract stock price data from metrics ratios to convert cash flow amounts to share counts
        try:
            ratios_df = pd.read_excel(latest_file, sheet_name='Metrics Ratios, Q')
            
            # Look for Book value per Share to calculate approximate stock price
            book_value_per_share_row = ratios_df[ratios_df.iloc[:, 0].astype(str).str.contains('Book value per Share', case=False, na=False)]
            pb_ratio_row = ratios_df[ratios_df.iloc[:, 0].astype(str).str.contains('P/B ratio', case=False, na=False)]
            
            if not book_value_per_share_row.empty and not pb_ratio_row.empty:
                # Calculate estimated stock prices for share count conversion
                
                # Extract book value per share data
                bv_row = book_value_per_share_row.iloc[0]
                pb_row = pb_ratio_row.iloc[0]
                
                for i in range(1, len(bv_row)):
                    if pd.notna(bv_row.iloc[i]) and pd.notna(pb_row.iloc[i]):
                        try:
                            book_value = float(str(bv_row.iloc[i]).replace(',', '').replace('$', ''))
                            pb_ratio = float(str(pb_row.iloc[i]).replace(',', '').replace('$', ''))
                            stock_price = book_value * pb_ratio
                            
                            # Get the date for this column
                            date_str = str(ratios_df.columns[i])
                            formatted_date = parse_quarter_date(date_str)
                            stock_price_data[formatted_date] = stock_price
                        except (ValueError, TypeError):
                            continue
                            
                print(f"Extracted stock prices for {len(stock_price_data)} periods")
                if len(stock_price_data) > 0:
                    # Show a few examples of the calculated stock prices
                    sample_dates = list(stock_price_data.keys())[:3]
                    print("Sample stock price calculations:")
                    for date in sample_dates:
                        print(f"  {date}: ${stock_price_data[date]:.2f}")
            else:
                # No stock price data available - proceed without price conversion
                pass
        except Exception as e:
            print(f"Warning: Could not extract stock price data: {str(e)}")
        
        # Create visualizations
        os.makedirs(output_dir, exist_ok=True)
        
        # Create two separate charts: one for shares, one for debt
        plt.style.use('default')  # Clean, professional style
        
        # Sort dates chronologically - create a custom sort function
        def date_sort_key(date_str):
            """Sort dates like Q1 2023, Q2 2023, etc. chronologically"""
            try:
                if 'Q' in date_str and len(date_str.split()) == 2:
                    quarter, year = date_str.split()
                    quarter_num = int(quarter[1])  # Extract number from Q1, Q2, etc.
                    year_num = int(year)
                    return (year_num, quarter_num)
                else:
                    return (2000, 1)  # Default for unparseable dates
            except:
                return (2000, 1)
        
        # CHART 1: SHARES ANALYSIS
        if shares_data or issuance_data or repurchase_data:
            fig1, ax1 = plt.subplots(1, 1, figsize=(16, 10))
            fig1.suptitle(f'{ticker.upper()} - Shares Outstanding Analysis', fontsize=24, fontweight='bold', y=0.98)
            
            # Add more space at the top
            plt.subplots_adjust(top=0.92)
            
            # Find unique dates for shares data only
            shares_dates = set()
            for data_dict in [shares_data, issuance_data, repurchase_data]:
                for data in data_dict.values():
                    shares_dates.update(data['dates'])
            
            shares_timeline = sorted(list(shares_dates), key=date_sort_key)
            shares_date_to_x = {date: i for i, date in enumerate(shares_timeline)}
            
            # Plot share count lines
            colors = plt.cm.Set1(np.linspace(0, 1, min(len(shares_data), 9)))
            
            for i, (key, data) in enumerate(shares_data.items()):
                values = data['values']
                dates = data['dates']
                
                # Convert values to millions and sort by date chronologically
                date_value_pairs = list(zip(dates, [v/1e6 for v in values]))
                date_value_pairs.sort(key=lambda x: date_sort_key(x[0]))
                
                # Create aligned x and y data
                x_positions = []
                y_values = []
                
                for date, value in date_value_pairs:
                    if date in shares_date_to_x:
                        x_positions.append(shares_date_to_x[date])
                        y_values.append(value)
                
                if x_positions and y_values:
                    label = data['metric'][:40] if len(data['metric']) <= 40 else data['metric'][:37] + '...'
                    line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-']
                    line_style = line_styles[i % len(line_styles)]
                    
                    ax1.plot(x_positions, y_values, marker='o', label=label, color=colors[i % len(colors)], 
                           linewidth=3, markersize=6, linestyle=line_style, alpha=0.8)
            
            # Commented out share issuance and repurchase bars for cleaner analysis
            # # Plot share issuance and repurchase bars
            # bar_width = 0.6
            # share_bar_data = {}
            # 
            # # Share issuance (positive, green bars) - Convert from dollars to shares
            # for key, data in issuance_data.items():
            #     for date, value in zip(data['dates'], data['values']):
            #         if date in shares_date_to_x:
            #             x_pos = shares_date_to_x[date]
            #             if x_pos not in share_bar_data:
            #                 share_bar_data[x_pos] = {'issuance': 0, 'repurchase': 0}
            #             
            #             # Convert from dollars to approximate shares using stock price
            #             if date in stock_price_data and stock_price_data[date] > 0:
            #                 shares_issued = value / stock_price_data[date]  # dollars / price per share = shares
            #                 
            #                 # Cap extremely large issuances (likely one-time events like IPO, SPAC, etc.)
            #                 # Flag if issuance would represent more than 25% of outstanding shares (~50M shares)
            #                 if shares_issued > 50e6:  # More than 50 million shares
            #                     print(f"  Large share issuance detected in {date}: ${value/1e6:.0f}M → {shares_issued/1e6:.1f}M shares (capped at 25M)")
            #                     shares_issued = min(shares_issued, 25e6)  # Cap at 25 million shares
            #                 
            #                 share_bar_data[x_pos]['issuance'] += shares_issued / 1e6  # Convert to millions
            #             else:
            #                 # Fallback: treat as millions of dollars if no stock price available
            #                 share_bar_data[x_pos]['issuance'] += value / 1e6
            # 
            # # Share repurchase (negative, red bars) - Convert from dollars to shares
            # for key, data in repurchase_data.items():
            #     for date, value in zip(data['dates'], data['values']):
            #         if date in shares_date_to_x:
            #             x_pos = shares_date_to_x[date]
            #             if x_pos not in share_bar_data:
            #                 share_bar_data[x_pos] = {'issuance': 0, 'repurchase': 0}
            #             
            #             # Convert from dollars to approximate shares using stock price
            #             if date in stock_price_data and stock_price_data[date] > 0:
            #                 shares_repurchased = abs(value) / stock_price_data[date]  # dollars / price per share = shares
            #                 
            #                 # Cap extremely large repurchases (likely one-time events)
            #                 if shares_repurchased > 100e6:  # More than 100 million shares
            #                     print(f"  Large share repurchase detected in {date}: ${abs(value)/1e6:.0f}M → {shares_repurchased/1e6:.1f}M shares (capped at 50M)")
            #                     shares_repurchased = min(shares_repurchased, 50e6)  # Cap at 50 million shares
            #                 
            #                 share_bar_data[x_pos]['repurchase'] += -shares_repurchased / 1e6  # Convert to millions, keep negative
            #             else:
            #                 # Fallback: treat as millions of dollars if no stock price available
            #                 share_bar_data[x_pos]['repurchase'] += value / 1e6
            # 
            # # Plot share bars
            # if share_bar_data:
            #     x_positions = list(share_bar_data.keys())
            #     issuance_vals = [share_bar_data[x]['issuance'] for x in x_positions]
            #     repurchase_vals = [share_bar_data[x]['repurchase'] for x in x_positions]
            #     
            #     # Determine labels based on whether we have stock price data
            #     if stock_price_data:
            #         issuance_label = 'Share Issuance (Est. Shares)'
            #         repurchase_label = 'Share Repurchase (Est. Shares)'
            #     else:
            #         issuance_label = 'Share Issuance ($M)'
            #         repurchase_label = 'Share Repurchase ($M)'
            #     
            #     if any(v != 0 for v in issuance_vals):
            #         ax1.bar(x_positions, issuance_vals, bar_width, label=issuance_label, color='green', alpha=0.7)
            #     if any(v != 0 for v in repurchase_vals):
            #         ax1.bar(x_positions, repurchase_vals, bar_width, label=repurchase_label, color='red', alpha=0.7)
            
            # Configure shares chart
            ax1.set_title('Historical Shares Outstanding (Millions)', fontsize=18, fontweight='bold', pad=30)
            ax1.set_xlabel('Time Period', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Shares (Millions)', fontsize=16, fontweight='bold')
            
            # Fix x-axis for shares
            max_periods = len(shares_timeline)
            ax1.set_xlim(-0.5, max_periods - 0.5)
            
            # Create proper x-tick labels - ensure we show first and last
            if max_periods > 12:
                step = max(1, max_periods // 8)
                tick_positions = list(range(0, max_periods, step))
                # Always include the last tick
                if tick_positions[-1] != max_periods - 1:
                    tick_positions.append(max_periods - 1)
            else:
                tick_positions = list(range(max_periods))
            
            tick_labels = [shares_timeline[i] for i in tick_positions]
            ax1.set_xticks(tick_positions)
            ax1.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            ax1.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12, frameon=True, 
                     fancybox=True, shadow=True)
            ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax1.tick_params(axis='both', which='major', labelsize=12)
            ax1.set_facecolor('#fafafa')
            
            # Save shares chart
            plt.tight_layout()
            shares_chart_path = os.path.join(output_dir, f'{ticker}_shares_analysis.png')
            plt.savefig(shares_chart_path, dpi=300, bbox_inches='tight')
            plt.close(fig1)
            print(f"Shares chart saved to: {shares_chart_path}")
        
        # CHART 2: DEBT ANALYSIS
        if debt_issuance_data or debt_repayment_data or debt_metrics_data:
            fig2, ax2 = plt.subplots(1, 1, figsize=(16, 10))
            fig2.suptitle(f'{ticker.upper()} - Debt Activity Analysis', fontsize=24, fontweight='bold', y=0.98)
            
            # Add subtitle explaining data availability
            fig2.text(0.5, 0.94, 'Note: Lines may start/end at different times based on data availability in financial reports', 
                     ha='center', fontsize=12, style='italic', alpha=0.7)
            
            # Add more space at the top
            plt.subplots_adjust(top=0.90)
            
            # Find unique dates for debt data including debt metrics
            debt_dates = set()
            for data_dict in [debt_issuance_data, debt_repayment_data, debt_metrics_data]:
                for data in data_dict.values():
                    debt_dates.update(data['dates'])
            
            debt_timeline = sorted(list(debt_dates), key=date_sort_key)
            debt_date_to_x = {date: i for i, date in enumerate(debt_timeline)}
            
            # Plot debt level lines first (as background)
            debt_colors = plt.cm.Set2(np.linspace(0, 1, min(len(debt_metrics_data), 8)))
            
            for i, (key, data) in enumerate(debt_metrics_data.items()):
                values = data['values']
                dates = data['dates']
                
                # Convert values to millions and sort by date chronologically
                date_value_pairs = list(zip(dates, [v/1e6 for v in values]))
                date_value_pairs.sort(key=lambda x: date_sort_key(x[0]))
                
                # Create aligned x and y data
                x_positions = []
                y_values = []
                
                for date, value in date_value_pairs:
                    if date in debt_date_to_x:
                        x_positions.append(debt_date_to_x[date])
                        y_values.append(value)
                
                if x_positions and y_values:
                    label = data['metric'][:40] if len(data['metric']) <= 40 else data['metric'][:37] + '...'
                    line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-']
                    line_style = line_styles[i % len(line_styles)]
                    
                    ax2.plot(x_positions, y_values, marker='o', label=label, color=debt_colors[i % len(debt_colors)], 
                           linewidth=3, markersize=6, linestyle=line_style, alpha=0.8)
            
            # Plot debt bars
            bar_width = 0.6
            debt_bar_data = {}
            
            # Debt issuance (positive, blue bars)
            for key, data in debt_issuance_data.items():
                for date, value in zip(data['dates'], data['values']):
                    if date in debt_date_to_x:
                        x_pos = debt_date_to_x[date]
                        if x_pos not in debt_bar_data:
                            debt_bar_data[x_pos] = {'issuance': 0, 'repayment': 0}
                        debt_bar_data[x_pos]['issuance'] += value / 1e6
            
            # Debt repayment (negative, orange bars)
            for key, data in debt_repayment_data.items():
                for date, value in zip(data['dates'], data['values']):
                    if date in debt_date_to_x:
                        x_pos = debt_date_to_x[date]
                        if x_pos not in debt_bar_data:
                            debt_bar_data[x_pos] = {'issuance': 0, 'repayment': 0}
                        debt_bar_data[x_pos]['repayment'] += value / 1e6
            
            # Plot debt bars
            if debt_bar_data:
                x_positions = list(debt_bar_data.keys())
                debt_issuance_vals = [debt_bar_data[x]['issuance'] for x in x_positions]
                debt_repayment_vals = [debt_bar_data[x]['repayment'] for x in x_positions]
                
                if any(v != 0 for v in debt_issuance_vals):
                    ax2.bar(x_positions, debt_issuance_vals, bar_width, label='Debt Issuance', color='blue', alpha=0.7)
                if any(v != 0 for v in debt_repayment_vals):
                    ax2.bar(x_positions, debt_repayment_vals, bar_width, label='Debt Repayment', color='orange', alpha=0.7)
            
            # Configure debt chart
            ax2.set_title('Historical Debt Activity (Millions)', fontsize=18, fontweight='bold', pad=30)
            ax2.set_xlabel('Time Period', fontsize=16, fontweight='bold')
            ax2.set_ylabel('Amount (Millions)', fontsize=16, fontweight='bold')
            
            # Fix x-axis for debt
            max_periods = len(debt_timeline)
            ax2.set_xlim(-0.5, max_periods - 0.5)
            
            # Create proper x-tick labels - ensure we show first and last
            if max_periods > 12:
                step = max(1, max_periods // 8)
                tick_positions = list(range(0, max_periods, step))
                # Always include the last tick
                if tick_positions[-1] != max_periods - 1:
                    tick_positions.append(max_periods - 1)
            else:
                tick_positions = list(range(max_periods))
            
            tick_labels = [debt_timeline[i] for i in tick_positions]
            ax2.set_xticks(tick_positions)
            ax2.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            ax2.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12, frameon=True, 
                     fancybox=True, shadow=True)
            ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax2.tick_params(axis='both', which='major', labelsize=12)
            ax2.set_facecolor('#fafafa')
            
            # Save debt chart
            plt.tight_layout()
            debt_chart_path = os.path.join(output_dir, f'{ticker}_debt_analysis.png')
            plt.savefig(debt_chart_path, dpi=300, bbox_inches='tight')
            plt.close(fig2)
            print(f"Debt chart saved to: {debt_chart_path}")
        
        # Print detailed summary to console
        print(f"\n=== {ticker.upper()} SHARES OUTSTANDING SUMMARY ===")
        
        # Group by sheet type for better organization
        balance_sheet_data = {}
        income_statement_data = {}
        other_data = {}
        
        for key, data in shares_data.items():
            sheet = data['sheet'].lower()
            metric = data['metric']
            current = data['values'][0] if data['values'] else 0
            
            if 'balance' in sheet:
                balance_sheet_data[metric] = current
            elif 'income' in sheet:
                income_statement_data[metric] = current
            else:
                other_data[metric] = current
        
        if balance_sheet_data:
            print("\nBalance Sheet (Shares Outstanding):")
            for metric, value in balance_sheet_data.items():
                print(f"  {metric}: {value:,.0f} shares ({value/1e6:.1f}M)")
        
        if income_statement_data:
            print("\nIncome Statement (Weighted Average Shares):")
            for metric, value in income_statement_data.items():
                print(f"  {metric}: {value:,.0f} shares ({value/1e6:.1f}M)")
        
        if other_data:
            print("\nOther Share Metrics:")
            for metric, value in other_data.items():
                print(f"  {metric}: {value:,.0f} shares ({value/1e6:.1f}M)")
        
        # Key insights
        print(f"\n=== KEY INSIGHTS ===")
        if balance_sheet_data and income_statement_data:
            balance_max = max(balance_sheet_data.values()) if balance_sheet_data else 0
            income_max = max(income_statement_data.values()) if income_statement_data else 0
            
            if balance_max > income_max * 1.1:  # More than 10% difference
                print(f"NOTICE: Balance sheet shows {balance_max/1e6:.1f}M shares outstanding")
                print(f"        Income statement shows {income_max/1e6:.1f}M weighted average shares")
                print(f"        Difference: {(balance_max-income_max)/1e6:.1f}M shares ({((balance_max-income_max)/income_max*100):.1f}%)")
                print("        This suggests significant share issuance during reporting periods")
        
        return True
        
    except Exception as e:
        print(f"Error in shares outstanding analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def load_data(ticker=None):
    """Load both annual and quarterly CSV data for a specific ticker."""
    try:
        import glob
        import os
        
        # Use provided ticker or detect it
        if not ticker:
            ticker = detect_ticker_symbol()
        
        # Clean ticker for filename
        clean_ticker = ticker.lower().replace('.', '') if ticker and ticker != "TICKER" else None
        
        # Search for annual data files - prioritize specific ticker files
        annual_files = []
        if clean_ticker:
            specific_patterns = [
                f'data/owner_earnings_annual_{clean_ticker}.csv',
                f'owner_earnings_annual_{clean_ticker}.csv',
                f'./data/owner_earnings_annual_{clean_ticker}.csv',
                f'../data/owner_earnings_annual_{clean_ticker}.csv',
                f'marketswimmer/gui/data/owner_earnings_annual_{clean_ticker}.csv'
            ]
            
            for pattern in specific_patterns:
                files = glob.glob(pattern)
                if files:
                    annual_files.extend(files)
                    print(f"[DEBUG] Found ticker-specific files with pattern '{pattern}': {files}")
                    break  # Use first match for specific ticker
        
        # If no specific files found, search for any files
        if not annual_files:
            general_patterns = [
                'data/owner_earnings_annual_*.csv',
                'owner_earnings_annual_*.csv', 
                './data/owner_earnings_annual_*.csv',
                '../data/owner_earnings_annual_*.csv',
                'marketswimmer/gui/data/owner_earnings_annual_*.csv'
            ]
            
            for pattern in general_patterns:
                files = glob.glob(pattern)
                if files:
                    annual_files.extend(files)
                    print(f"[DEBUG] General pattern '{pattern}' found: {files}")
        
        # Remove duplicates and sort by modification time (most recent first)
        annual_files = list(set(annual_files))
        if annual_files:
            annual_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Fallback to old filename format
        if not annual_files:
            fallback_patterns = [
                'data/owner_earnings_financials_annual.csv',
                'owner_earnings_financials_annual.csv'
            ]
            for pattern in fallback_patterns:
                files = glob.glob(pattern)
                annual_files.extend(files)
        
        if not annual_files:
            print("[ERROR] No annual data files found in any location")
            print(f"[DEBUG] Current directory contents: {os.listdir('.')}")
            if os.path.exists('data'):
                print(f"[DEBUG] Data directory contents: {os.listdir('data')}")
            return None, None
        
        annual_path = annual_files[0]  # Use the most recent file
        print(f"[DEBUG] Found annual files: {annual_files}")
        print(f"[DEBUG] Using most recent annual file: {annual_path}")
        
        annual_df = pd.read_csv(annual_path)
        print(f"[OK] Loaded annual data: {len(annual_df)} years from {annual_path}")
        
        # Search for quarterly data files - prioritize specific ticker files
        quarterly_files = []
        if clean_ticker:
            specific_patterns = [
                f'data/owner_earnings_quarterly_{clean_ticker}.csv',
                f'owner_earnings_quarterly_{clean_ticker}.csv',
                f'./data/owner_earnings_quarterly_{clean_ticker}.csv',
                f'../data/owner_earnings_quarterly_{clean_ticker}.csv',
                f'marketswimmer/gui/data/owner_earnings_quarterly_{clean_ticker}.csv'
            ]
            
            for pattern in specific_patterns:
                files = glob.glob(pattern)
                if files:
                    quarterly_files.extend(files)
                    print(f"[DEBUG] Found quarterly ticker-specific files with pattern '{pattern}': {files}")
                    break  # Use first match for specific ticker
        
        # If no specific files found, search for any quarterly files
        if not quarterly_files:
            general_patterns = [
                'data/owner_earnings_quarterly_*.csv',
                'owner_earnings_quarterly_*.csv',
                './data/owner_earnings_quarterly_*.csv',
                '../data/owner_earnings_quarterly_*.csv',
                'marketswimmer/gui/data/owner_earnings_quarterly_*.csv'
            ]
            
            for pattern in general_patterns:
                files = glob.glob(pattern)
                if files:
                    quarterly_files.extend(files)
                    print(f"[DEBUG] Quarterly general pattern '{pattern}' found: {files}")
        
        # Remove duplicates and sort by modification time
        quarterly_files = list(set(quarterly_files))
        if quarterly_files:
            quarterly_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Fallback to old filename format
        if not quarterly_files:
            fallback_patterns = [
                'data/owner_earnings_financials_quarterly.csv',
                'owner_earnings_financials_quarterly.csv'
            ]
            for pattern in fallback_patterns:
                files = glob.glob(pattern)
                quarterly_files.extend(files)
            
        if not quarterly_files:
            print("[ERROR] No quarterly data files found in any location")
            print(f"[DEBUG] Searched quarterly patterns for ticker: {clean_ticker}")
            return None, None
        
        quarterly_path = quarterly_files[0]  # Use the most recent file
        print(f"[DEBUG] Found quarterly files: {quarterly_files}")
        print(f"[DEBUG] Using most recent quarterly file: {quarterly_path}")
        quarterly_df = pd.read_csv(quarterly_path)
        print(f"[OK] Loaded quarterly data: {len(quarterly_df)} quarters from {quarterly_path}")
        
        return annual_df, quarterly_df
        
    except Exception as e:
        print(f"[ERROR] Error loading data: {e}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return None, None
        print(f"[DEBUG] Found quarterly files: {quarterly_files}")
        print(f"[DEBUG] Using most recent quarterly file: {quarterly_path}")
        quarterly_df = pd.read_csv(quarterly_path)
        print(f"[OK] Loaded quarterly data: {len(quarterly_df)} quarters from {quarterly_path}")
        
        return annual_df, quarterly_df
    
    except FileNotFoundError as e:
        print(f"[ERROR] Error loading CSV files: {e}")
        print("[INFO] Make sure to run owner_earnings_fixed.py first to generate the CSV files")
        print("[INFO] CSV files should be in the 'data/' directory")
        return None, None

def prepare_quarterly_data(df):
    """Prepare quarterly data for plotting."""
    # Convert period to datetime for better plotting
    df = df.copy()
    
    print(f"[DEBUG] Raw quarterly data shape: {df.shape}")
    print(f"[DEBUG] Period column sample values: {df['Period'].head().tolist()}")
    print(f"[DEBUG] Period column data types: {df['Period'].dtype}")
    
    # Ensure Period column is string type for string operations
    df['Period'] = df['Period'].astype(str)
    print(f"[DEBUG] Period column after string conversion: {df['Period'].head().tolist()}")
    
    # Check if this is actually annual data masquerading as quarterly data
    period_values = df['Period'].unique()
    is_annual_data = all(len(p) == 4 and p.isdigit() for p in period_values)
    
    if is_annual_data:
        print(f"[WARNING] Detected annual data in quarterly file - treating as annual")
        # This is annual data, so just parse as years
        df['year'] = df['Period'].astype(int)
        df['quarter'] = 2  # Use Q2 as a middle-of-year approximation
        df['date'] = pd.to_datetime(df[['year']].assign(month=7, day=1))  # July 1st
        print(f"[DEBUG] Converted annual-as-quarterly data: {df['date'].head().tolist()}")
    else:
        # Extract year and quarter from Period (format should be like "2024Q1")
        try:
            # Handle different Period formats more robustly
            print(f"[DEBUG] Attempting to parse quarterly Period values: {df['Period'].unique()}")
            
            if df['Period'].str.contains('Q').any():
                # Format like "2024Q1"
                df['year'] = df['Period'].str[:4].astype(int)
                df['quarter'] = df['Period'].str[-1].astype(int)
            elif df['Period'].str.contains('-').any():
                # Format like "2024-Q1" or "Q1-2024"
                # Try to extract 4-digit year and 1-digit quarter
                year_pattern = df['Period'].str.extract(r'(\d{4})')
                quarter_pattern = df['Period'].str.extract(r'Q(\d)')
                df['year'] = year_pattern[0].astype(int)
                df['quarter'] = quarter_pattern[0].astype(int)
            else:
                # Fallback: try to parse as much as possible
                print(f"[WARNING] Unknown Period format, attempting generic parsing")
                # Try to extract any 4-digit number as year
                year_match = df['Period'].str.extract(r'(\d{4})')
                if not year_match[0].isna().all():
                    df['year'] = year_match[0].astype(int)
                else:
                    df['year'] = 2024  # Default year
                
                # Try to extract quarter number
                quarter_match = df['Period'].str.extract(r'(\d)')
                if not quarter_match[0].isna().all():
                    df['quarter'] = quarter_match[0].astype(int)
                else:
                    df['quarter'] = 1  # Default quarter
            
            print(f"[DEBUG] Extracted years: {df['year'].tolist()}")
            print(f"[DEBUG] Extracted quarters: {df['quarter'].tolist()}")
            
            # Validate extracted values
            if df['year'].isna().any() or df['quarter'].isna().any():
                raise ValueError("Failed to extract valid year/quarter values")
            if (df['quarter'] < 1).any() or (df['quarter'] > 4).any():
                print(f"[WARNING] Invalid quarter values found: {df['quarter'].unique()}")
                df['quarter'] = df['quarter'].clip(1, 4)  # Clamp to valid range
                
        except Exception as e:
            print(f"[ERROR] Failed to extract year/quarter: {e}")
            print(f"[DEBUG] Period values causing issues: {df['Period'].unique()}")
            # Create fallback values to prevent complete failure
            df['year'] = 2024
            df['quarter'] = 1
            print(f"[WARNING] Using fallback year/quarter values")
        
        # Create a proper date column
        try:
            df['date'] = pd.to_datetime(df[['year']].assign(month=(df['quarter']-1)*3+1, day=1))
            print(f"[DEBUG] Successfully created date column: {df['date'].head().tolist()}")
        except Exception as e:
            print(f"[ERROR] Failed to create date column: {e}")
            print(f"[DEBUG] Year values: {df['year'].tolist()}")
            print(f"[DEBUG] Quarter values: {df['quarter'].tolist()}")
            # Create a simple date column based on just the year
            df['date'] = pd.to_datetime(df['year'], format='%Y')
            print(f"[WARNING] Using year-only dates: {df['date'].head().tolist()}")
    
    # Convert to millions for better readability - use the actual CSV column names
    financial_cols_map = {
        'Net Income': 'net_income',
        'Depreciation': 'depreciation', 
        'CapEx': 'capex',
        'Working Capital Change': 'working_capital_change',
        'Owner Earnings': 'owner_earnings'
    }
    
    for csv_col, standard_col in financial_cols_map.items():
        if csv_col in df.columns:
            df[f'{standard_col}_millions'] = df[csv_col] / 1_000_000
    
    # Sort by date for proper chronological plotting
    df = df.sort_values('date')
    
    return df

def prepare_annual_data(df):
    """Prepare annual data for plotting with robust error handling."""
    df = df.copy()
    
    print(f"[DEBUG] Annual Period column: {df['Period'].head().tolist()}")
    print(f"[DEBUG] Annual Period dtypes: {df['Period'].dtype}")
    
    # Try different date parsing approaches
    try:
        # First try: assume it's just years like "2024"
        df['date'] = pd.to_datetime(df['Period'], format='%Y')
        print(f"[DEBUG] Successfully parsed annual dates as years")
    except ValueError as e:
        print(f"[DEBUG] Year format failed: {e}")
        try:
            # Second try: generic datetime parsing
            df['date'] = pd.to_datetime(df['Period'], errors='coerce')
            print(f"[DEBUG] Successfully parsed annual dates with generic parser")
        except Exception as e2:
            print(f"[ERROR] All annual date parsing failed: {e2}")
            print(f"[DEBUG] Problematic Period values: {df['Period'].unique()}")
            # Create a dummy date column to prevent crashes
            df['date'] = pd.to_datetime('2020-01-01')
            print(f"[WARNING] Using dummy dates for annual data")
    
    # Convert to millions for better readability - use the actual CSV column names
    financial_cols_map = {
        'Net Income': 'net_income',
        'Depreciation': 'depreciation', 
        'CapEx': 'capex',
        'Working Capital Change': 'working_capital_change',
        'Owner Earnings': 'owner_earnings'
    }
    
    for csv_col, standard_col in financial_cols_map.items():
        if csv_col in df.columns:
            df[f'{standard_col}_millions'] = df[csv_col] / 1_000_000
    
    # Sort by date for proper chronological plotting (oldest to newest)
    df = df.sort_values('date')
    
    return df

def create_owner_earnings_comparison(annual_df, quarterly_df, ticker):
    """Create a comparison chart of annual vs quarterly owner earnings."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Annual chart
    annual_df.plot(x='date', y='owner_earnings_millions', kind='line', 
                   ax=ax1, marker='o', linewidth=2, markersize=6, color='#1f77b4')
    ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax1.set_title(f'{ticker} Annual Owner Earnings (2015-2024)', fontweight='bold', fontsize=16)
    ax1.set_ylabel('Owner Earnings ($ Millions)')
    ax1.set_xlabel('Year')
    ax1.grid(True, alpha=0.3)
    ax1.legend(['Owner Earnings', 'Break-even'], loc='upper left')
    
    # Add annotations for key points
    max_annual = annual_df.loc[annual_df['owner_earnings_millions'].idxmax()]
    min_annual = annual_df.loc[annual_df['owner_earnings_millions'].idxmin()]
    
    ax1.annotate(f'Best: ${max_annual["owner_earnings_millions"]:.0f}M\n({max_annual["Period"]})', 
                xy=(max_annual['date'], max_annual['owner_earnings_millions']),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    ax1.annotate(f'Worst: ${min_annual["owner_earnings_millions"]:.0f}M\n({min_annual["Period"]})', 
                xy=(min_annual['date'], min_annual['owner_earnings_millions']),
                xytext=(10, -20), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    # Quarterly chart
    quarterly_df.plot(x='date', y='owner_earnings_millions', kind='line', 
                      ax=ax2, marker='s', linewidth=1.5, markersize=4, color='#ff7f0e', alpha=0.8)
    ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax2.set_title(f'{ticker} Quarterly Owner Earnings (2015-2025)', fontweight='bold', fontsize=16)
    ax2.set_ylabel('Owner Earnings ($ Millions)')
    ax2.set_xlabel('Date')
    ax2.grid(True, alpha=0.3)
    ax2.legend(['Owner Earnings', 'Break-even'], loc='upper left')
    
    # Add annotations for quarterly extremes
    max_quarterly = quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmax()]
    min_quarterly = quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmin()]
    
    ax2.annotate(f'Best: ${max_quarterly["owner_earnings_millions"]:.0f}M\n({max_quarterly["Period"]})', 
                xy=(max_quarterly['date'], max_quarterly['owner_earnings_millions']),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    ax2.annotate(f'Worst: ${min_quarterly["owner_earnings_millions"]:.0f}M\n({min_quarterly["Period"]})', 
                xy=(min_quarterly['date'], min_quarterly['owner_earnings_millions']),
                xytext=(10, -20), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.tight_layout()
    return fig

def create_components_breakdown(annual_df, quarterly_df, ticker):
    """Create waterfall charts showing the components of owner earnings."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 14))
    
    # Annual components waterfall
    create_annual_waterfall_chart(ax1, annual_df, ticker)
    
    # Quarterly components (most recent 20 quarters for readability)
    # Since data is now sorted chronologically, get the last 20 quarters
    quarterly_recent = quarterly_df.tail(20).copy()
    
    # Create waterfall chart for quarterly data
    create_waterfall_chart(ax2, quarterly_recent, ticker)
    
    # Rotate x-axis labels for better readability
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig
    
    plt.tight_layout()
    return fig

def create_annual_waterfall_chart(ax, df, ticker):
    """Create a waterfall chart showing annual owner earnings components for all years."""
    
    # Use all years instead of limiting to recent ones
    recent_years = df.copy()
    
    # Set up the chart dimensions - adjust bar width based on number of years
    n_years = len(recent_years)
    bar_width = max(0.08, min(0.15, 2.0 / n_years))  # Dynamic bar width
    
    # Create positions for each year
    year_positions = np.arange(n_years)
    
    # Colors for each component
    colors = {
        'Net Income': '#2E86AB',
        'Depreciation': '#A23B72', 
        'CapEx': '#F18F01',
        'WC Changes': '#C73E1D',
        'Owner Earnings': '#4CAF50'
    }
    
    # Create grouped waterfall charts for each year
    for i, (_, year) in enumerate(recent_years.iterrows()):
        period = year['Period']
        
        # Component values
        net_income = year['net_income_millions']
        depreciation = year['depreciation_millions']
        capex = year['capex_millions']
        wc_change = year['working_capital_change_millions']
        owner_earnings = year['owner_earnings_millions']
        
        # Calculate cumulative positions for waterfall
        cumulative = [0]
        cumulative.append(net_income)
        cumulative.append(cumulative[-1] + depreciation)
        cumulative.append(cumulative[-1] + capex)
        cumulative.append(cumulative[-1] + wc_change)
        
        # X position for this year's bars
        x_base = i
        
        # Net Income (starts from 0)
        ax.bar(x_base - 2*bar_width, net_income, bar_width, 
               bottom=0, color=colors['Net Income'], alpha=0.8, 
               edgecolor='black', linewidth=0.3,
               label='Net Income' if i == 0 else "")
        
        # Depreciation (stacks on Net Income)
        ax.bar(x_base - bar_width, depreciation, bar_width,
               bottom=cumulative[1], color=colors['Depreciation'], alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='+ Depreciation' if i == 0 else "")
        
        # CapEx (negative, stacks on previous)
        ax.bar(x_base, capex, bar_width,
               bottom=cumulative[2], color=colors['CapEx'], alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='- CapEx' if i == 0 else "")
        
        # Working Capital Changes (can be positive or negative)
        wc_color = colors['WC Changes'] if wc_change < 0 else '#90EE90'
        ax.bar(x_base + bar_width, wc_change, bar_width,
               bottom=cumulative[3], color=wc_color, alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='WC Changes' if i == 0 else "")
        
        # Owner Earnings (final result)
        oe_color = colors['Owner Earnings'] if owner_earnings >= 0 else '#F44336'
        ax.bar(x_base + 2*bar_width, owner_earnings, bar_width,
               bottom=0, color=oe_color, alpha=0.8,
               edgecolor='black', linewidth=0.5,
               label='Owner Earnings' if i == 0 else "")
        
        # Add value labels for Owner Earnings (in billions for annual)
        oe_billions = owner_earnings / 1000
        ax.text(x_base + 2*bar_width, owner_earnings/2, f'${oe_billions:.1f}B',
               ha='center', va='center', fontweight='bold', fontsize=9, rotation=90)
        
        # Add connecting line to show the flow to final result
        if owner_earnings >= 0:
            ax.plot([x_base + bar_width + bar_width/2, x_base + 2*bar_width - bar_width/2], 
                   [cumulative[4], owner_earnings/2], 'k--', alpha=0.3, linewidth=1)
    
    # Formatting
    ax.set_xticks(year_positions)
    ax.set_xticklabels([str(int(y['Period'])) for _, y in recent_years.iterrows()])
    ax.set_title(f'{ticker} Annual Owner Earnings Waterfall - All Years', fontweight='bold', fontsize=16)
    ax.set_ylabel('Amount ($ Millions)')
    
    # Create custom legend to show both positive and negative WC changes and Owner Earnings
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E86AB', alpha=0.8, label='Net Income'),
        Patch(facecolor='#A23B72', alpha=0.8, label='+ Depreciation'),
        Patch(facecolor='#F18F01', alpha=0.8, label='- CapEx'),
        Patch(facecolor='#C73E1D', alpha=0.8, label='WC Changes (-)'),
        Patch(facecolor='#90EE90', alpha=0.8, label='WC Changes (+)'),
        Patch(facecolor='#4CAF50', alpha=0.8, label='Owner Earnings (+)'),
        Patch(facecolor='#F44336', alpha=0.8, label='Owner Earnings (-)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8)

def create_waterfall_chart(ax, df, ticker):
    """Create a waterfall chart showing owner earnings components for all quarters."""
    
    # Use all quarters instead of limiting to recent ones
    recent_quarters = df.copy()
    
    # Set up the chart dimensions - adjust bar width based on number of quarters
    n_quarters = len(recent_quarters)
    bar_width = max(0.08, min(0.15, 3.0 / n_quarters))  # Dynamic bar width
    
    # Create positions for each quarter
    quarter_positions = np.arange(n_quarters)
    
    # Colors for each component
    colors = {
        'Net Income': '#2E86AB',
        'Depreciation': '#A23B72', 
        'CapEx': '#F18F01',
        'WC Changes': '#C73E1D',
        'Owner Earnings': '#4CAF50'
    }
    
    # Create grouped waterfall charts for each quarter
    for i, (_, quarter) in enumerate(recent_quarters.iterrows()):
        period = quarter['Period']
        
        # Component values
        net_income = quarter['net_income_millions']
        depreciation = quarter['depreciation_millions']
        capex = quarter['capex_millions']
        wc_change = quarter['working_capital_change_millions']
        owner_earnings = quarter['owner_earnings_millions']
        
        # Calculate cumulative positions for waterfall
        cumulative = [0]
        cumulative.append(net_income)
        cumulative.append(cumulative[-1] + depreciation)
        cumulative.append(cumulative[-1] + capex)
        cumulative.append(cumulative[-1] + wc_change)
        
        # X position for this quarter's bars
        x_base = i
        
        # Net Income (starts from 0)
        ax.bar(x_base - 2*bar_width, net_income, bar_width, 
               bottom=0, color=colors['Net Income'], alpha=0.8, 
               edgecolor='black', linewidth=0.3,
               label='Net Income' if i == 0 else "")
        
        # Depreciation (stacks on Net Income)
        ax.bar(x_base - bar_width, depreciation, bar_width,
               bottom=cumulative[1], color=colors['Depreciation'], alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='+ Depreciation' if i == 0 else "")
        
        # CapEx (negative, stacks on previous)
        ax.bar(x_base, capex, bar_width,
               bottom=cumulative[2], color=colors['CapEx'], alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='- CapEx' if i == 0 else "")
        
        # Working Capital Changes (can be positive or negative)
        wc_color = colors['WC Changes'] if wc_change < 0 else '#90EE90'
        ax.bar(x_base + bar_width, wc_change, bar_width,
               bottom=cumulative[3], color=wc_color, alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='WC Changes' if i == 0 else "")
        
        # Owner Earnings (final result)
        oe_color = colors['Owner Earnings'] if owner_earnings >= 0 else '#F44336'
        ax.bar(x_base + 2*bar_width, owner_earnings, bar_width,
               bottom=0, color=oe_color, alpha=0.8,
               edgecolor='black', linewidth=0.5,
               label='Owner Earnings' if i == 0 else "")
        
        # Add value labels for Owner Earnings
        ax.text(x_base + 2*bar_width, owner_earnings/2, f'${owner_earnings:,.0f}M',
               ha='center', va='center', fontweight='bold', fontsize=8, rotation=90)
        
        # Add connecting line to show the flow to final result
        if owner_earnings >= 0:
            ax.plot([x_base + bar_width + bar_width/2, x_base + 2*bar_width - bar_width/2], 
                   [cumulative[4], owner_earnings/2], 'k--', alpha=0.3, linewidth=1)
    
    # Formatting
    ax.set_xticks(quarter_positions)
    quarter_labels = [q['Period'] for _, q in recent_quarters.iterrows()]
    
    # If too many quarters, show every 4th label (yearly intervals) for readability
    if len(quarter_labels) > 16:
        display_labels = []
        for i, label in enumerate(quarter_labels):
            if i % 4 == 0 or label.endswith('Q4'):  # Show every 4th or year-end quarters
                display_labels.append(label)
            else:
                display_labels.append('')
        ax.set_xticklabels(display_labels, rotation=45, ha='right')
    else:
        ax.set_xticklabels(quarter_labels, rotation=45, ha='right')
    
    ax.set_title(f'{ticker} Owner Earnings Waterfall - All Quarters', fontweight='bold', fontsize=14)
    ax.set_ylabel('Amount ($ Millions)')
    
    # Create custom legend to show both positive and negative WC changes
    # Create custom legend to show all components including negative owner earnings
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E86AB', alpha=0.8, label='Net Income'),
        Patch(facecolor='#A23B72', alpha=0.8, label='+ Depreciation'),
        Patch(facecolor='#F18F01', alpha=0.8, label='- CapEx'),
        Patch(facecolor='#C73E1D', alpha=0.8, label='WC Changes (-)'),
        Patch(facecolor='#90EE90', alpha=0.8, label='WC Changes (+)'),
        Patch(facecolor='#4CAF50', alpha=0.8, label='Owner Earnings (+)'),
        Patch(facecolor='#F44336', alpha=0.8, label='Owner Earnings (-)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
    
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8)

def create_volatility_analysis(quarterly_df, ticker):
    """Create charts showing the volatility and trends in owner earnings."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Check if we have enough data for volatility analysis
    if len(quarterly_df) < 4:
        # Not enough data for proper quarterly analysis
        ax1.text(0.5, 0.5, f'Insufficient data for volatility analysis\n({len(quarterly_df)} periods available)', 
                ha='center', va='center', transform=ax1.transAxes, fontsize=12)
        ax2.text(0.5, 0.5, 'Need at least 4 quarters\nfor meaningful analysis', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax3.text(0.5, 0.5, 'Quarterly data required', 
                ha='center', va='center', transform=ax3.transAxes, fontsize=12)
        ax4.text(0.5, 0.5, 'Analysis not available', 
                ha='center', va='center', transform=ax4.transAxes, fontsize=12)
        
        for ax in [ax1, ax2, ax3, ax4]:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title(f'{ticker} Volatility Analysis - Insufficient Data', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    # 1. Rolling average to show trend
    quarterly_df['rolling_4q'] = quarterly_df['owner_earnings_millions'].rolling(window=4, center=True).mean()
    quarterly_df['rolling_8q'] = quarterly_df['owner_earnings_millions'].rolling(window=8, center=True).mean()
    
    ax1.plot(quarterly_df['date'], quarterly_df['owner_earnings_millions'], 
             'o-', alpha=0.6, label='Quarterly', linewidth=1, markersize=3)
    ax1.plot(quarterly_df['date'], quarterly_df['rolling_4q'], 
             '-', linewidth=2, label='4Q Rolling Avg', color='red')
    ax1.plot(quarterly_df['date'], quarterly_df['rolling_8q'], 
             '-', linewidth=2, label='8Q Rolling Avg', color='green')
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.7)
    ax1.set_title(f'{ticker} Owner Earnings Trend Analysis', fontweight='bold')
    ax1.set_ylabel('Owner Earnings ($ Millions)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Year-over-year comparison (same quarter)
    quarterly_df['year'] = quarterly_df['date'].dt.year
    quarterly_df['quarter'] = quarterly_df['date'].dt.quarter
    
    # Create pivot for YoY comparison
    try:
        pivot_data = quarterly_df.pivot(index='quarter', columns='year', values='owner_earnings_millions')
        recent_years = [col for col in pivot_data.columns if col >= 2020]  # Focus on recent years
        
        # Check if we actually have quarterly data (not just annual data)
        unique_quarters = quarterly_df['quarter'].unique()
        if len(unique_quarters) == 1:
            # This is annual data masquerading as quarterly - show a different chart
            ax2.bar(quarterly_df['year'], quarterly_df['owner_earnings_millions'], alpha=0.7, color='skyblue')
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.7)
            ax2.set_title('Annual Owner Earnings (labeled as quarterly)', fontweight='bold')
            ax2.set_xlabel('Year')
            ax2.set_ylabel('Owner Earnings ($ Millions)')
            ax2.grid(True, alpha=0.3)
        else:
            # Real quarterly data - show quarters
            for year in recent_years:
                if year in pivot_data.columns:
                    quarters = [1,2,3,4]
                    values = [pivot_data.loc[q, year] if q in pivot_data.index else None for q in quarters]
                    # Filter out None values
                    valid_quarters = [q for q, v in zip(quarters, values) if v is not None]
                    valid_values = [v for v in values if v is not None]
                    if valid_quarters and valid_values:
                        ax2.plot(valid_quarters, valid_values, 'o-', label=f'{year}', linewidth=2, markersize=6)
            
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.7)
            ax2.set_title('Year-over-Year Quarterly Comparison', fontweight='bold')
            ax2.set_xlabel('Quarter')
            ax2.set_ylabel('Owner Earnings ($ Millions)')
            ax2.set_xticks([1,2,3,4])
            ax2.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
    except Exception as e:
        print(f"[WARNING] Error creating YoY chart: {e}")
        ax2.text(0.5, 0.5, f'YoY Analysis Error:\n{str(e)}', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=10)
        ax2.set_title('Year-over-Year Analysis - Error', fontweight='bold')
    
    # 3. Distribution histogram
    ax3.hist(quarterly_df['owner_earnings_millions'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    ax3.axvline(x=quarterly_df['owner_earnings_millions'].mean(), color='red', 
                linestyle='--', label=f"Mean: ${quarterly_df['owner_earnings_millions'].mean():.0f}M")
    ax3.axvline(x=quarterly_df['owner_earnings_millions'].median(), color='green', 
                linestyle='--', label=f"Median: ${quarterly_df['owner_earnings_millions'].median():.0f}M")
    ax3.set_title('Distribution of Quarterly Owner Earnings', fontweight='bold')
    ax3.set_xlabel('Owner Earnings ($ Millions)')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Positive vs Negative quarters
    positive_quarters = quarterly_df[quarterly_df['owner_earnings_millions'] > 0]
    negative_quarters = quarterly_df[quarterly_df['owner_earnings_millions'] <= 0]
    
    summary_data = {
        'Positive Quarters': [len(positive_quarters), positive_quarters['owner_earnings_millions'].mean() if len(positive_quarters) > 0 else 0],
        'Negative Quarters': [len(negative_quarters), negative_quarters['owner_earnings_millions'].mean() if len(negative_quarters) > 0 else 0]
    }
    
    categories = list(summary_data.keys())
    counts = [summary_data[cat][0] for cat in categories]
    avg_values = [summary_data[cat][1] for cat in categories]
    
    x_pos = np.arange(len(categories))
    
    bars1 = ax4.bar(x_pos - 0.2, counts, 0.4, label='Count', color='lightblue', alpha=0.8)
    ax4_twin = ax4.twinx()
    bars2 = ax4_twin.bar(x_pos + 0.2, avg_values, 0.4, label='Avg Value ($M)', color='lightcoral', alpha=0.8)
    
    ax4.set_title('Positive vs Negative Quarters Summary', fontweight='bold')
    ax4.set_xlabel('Quarter Type')
    ax4.set_ylabel('Number of Quarters', color='blue')
    ax4_twin.set_ylabel('Average Value ($ Millions)', color='red')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(categories)
    
    # Add value labels on bars
    for bar, count in zip(bars1, counts):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(count), ha='center', va='bottom')
    
    for bar, avg_val in zip(bars2, avg_values):
        ax4_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (20 if avg_val > 0 else -40), 
                     f'${avg_val:.0f}M', ha='center', va='bottom' if avg_val > 0 else 'top')
    
    plt.tight_layout()
    return fig

def save_and_show_plots(figures, filenames, ticker):
    """Save plots to files and display them."""
    # Ensure we're using non-interactive backend
    matplotlib.use('Agg')
    plt.ioff()
    
    # Create charts directory if it doesn't exist
    charts_dir = "charts"
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        print(f"[DIR] Created directory: {charts_dir}/")
    
    for fig, filename in zip(figures, filenames):
        # Use the filename as-is since it's already properly formatted
        filepath = os.path.join(charts_dir, f"{filename}.png")
        fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"[CHART] Saved chart: {filepath}")
        # Close the figure to free memory
        plt.close(fig)
    
    # Don't show interactive plots in GUI mode - just save them
    # plt.show()
    print("\n[OK] All charts displayed and saved!")

def main(ticker=None):
    """Main function to create all visualizations."""
    # Use provided ticker or detect it
    if ticker is None:
        ticker = detect_ticker_symbol()
    
    print(f"{ticker} Owner Earnings Visualization Tool")
    print("=" * 50)
    
    # Set up plotting style
    setup_plotting_style()
    
    # Load data with specific ticker
    annual_df, quarterly_df = load_data(ticker)
    if annual_df is None or quarterly_df is None:
        return
    
    # Prepare data
    print("[ANALYSIS] Preparing data for visualization...")
    annual_df = prepare_annual_data(annual_df)
    quarterly_df = prepare_quarterly_data(quarterly_df)
    
    print(f"[CHARTS] Creating visualizations...")
    
    # Create all charts
    figures = []
    filenames = []
    
    # 1. Owner earnings comparison
    fig1 = create_owner_earnings_comparison(annual_df, quarterly_df, ticker)
    figures.append(fig1)
    filenames.append(f"{ticker.lower().replace('.', '')}_owner_earnings_comparison")
    
    # 2. Components breakdown
    fig2 = create_components_breakdown(annual_df, quarterly_df, ticker)
    figures.append(fig2)
    filenames.append(f"{ticker.lower().replace('.', '')}_earnings_components_breakdown")
    
    # 3. Volatility analysis
    fig3 = create_volatility_analysis(quarterly_df, ticker)
    figures.append(fig3)
    filenames.append(f"{ticker.lower().replace('.', '')}_volatility_analysis")
    
    # Save and show all plots
    save_and_show_plots(figures, filenames, ticker)
    
    # Print summary statistics
    print(f"\n[SUMMARY] {ticker} SUMMARY STATISTICS:")
    print(f"Annual Data Range: {annual_df['Period'].min()} to {annual_df['Period'].max()}")
    print(f"Quarterly Data Range: {quarterly_df['Period'].min()} to {quarterly_df['Period'].max()}")
    print(f"Best Annual Owner Earnings: ${annual_df['owner_earnings_millions'].max():.0f}M ({annual_df.loc[annual_df['owner_earnings_millions'].idxmax(), 'Period']})")
    print(f"Worst Annual Owner Earnings: ${annual_df['owner_earnings_millions'].min():.0f}M ({annual_df.loc[annual_df['owner_earnings_millions'].idxmin(), 'Period']})")
    print(f"Best Quarterly Owner Earnings: ${quarterly_df['owner_earnings_millions'].max():.0f}M ({quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmax(), 'Period']})")
    print(f"Worst Quarterly Owner Earnings: ${quarterly_df['owner_earnings_millions'].min():.0f}M ({quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmin(), 'Period']})")
    
    positive_quarters = len(quarterly_df[quarterly_df['owner_earnings_millions'] > 0])
    total_quarters = len(quarterly_df)
    print(f"Positive Quarters: {positive_quarters}/{total_quarters} ({positive_quarters/total_quarters*100:.1f}%)")

if __name__ == "__main__":
    main()
