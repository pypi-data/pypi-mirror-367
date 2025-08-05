# MarketSwimmer - Owner Earnings Analysis Tool 🏊‍♂️📈

A comprehensive tool for analyzing Warren Buffett's "Owner Earnings" from financial statement data.

## � **v2.1.0 - What's New**

✅ **Complete Data Processing Pipeline**: Automated XLSX-to-CSV conversion for seamless workflow  
✅ **Real Quarterly Data**: Proper quarter-by-quarter financial analysis (not just annual duplicates)  
✅ **Professional Visualizations**: 3 chart types with recent years focus  
✅ **Smart Download Detection**: Automatically detects XLSX files in Downloads folder  
✅ **Clean Color Scheme**: Improved white/blue theme for better readability

## 📦 **Installation**

```bash
pip install marketswimmer
```

## � Quick Start

### Command Line Usage

```bash
# Launch GUI
marketswimmer gui

# Process downloaded data
python process_financial_data.py TICKER

# Create visualizations
marketswimmer visualize --ticker TICKER

# Full analysis
marketswimmer analyze TICKER
```

### GUI Workflow

1. **Launch GUI**: `marketswimmer gui` or double-click `launch_clean_gui.bat`
2. **Select Ticker**: Choose a stock symbol (e.g., AAPL, MSFT, BRK.B)
3. **Download Data**: System opens StockRow page for manual data download
4. **Process Data**: Run `python process_financial_data.py TICKER`
5. **Analyze**: Use GUI "Calculate Owner Earnings" and "Create Visualizations" buttons

## 📊 Output Files

- **Charts**: `charts/[ticker]_*.png` - Visual analysis charts
- **Data**: `data/owner_earnings_*.csv` - Raw analysis data
- **Logs**: `logs/marketswimmer_*.log` - Application logs

## 💡 Owner Earnings Formula

```
Owner Earnings = Net Income + Depreciation/Amortization - CapEx - Working Capital Changes
```

## 🎯 Features

- ✅ Ticker-specific analysis
- ✅ Annual and quarterly data processing
- ✅ Professional visualizations
- ✅ Automated chart generation
- ✅ Clean directory organization
- ✅ Comprehensive logging

## 📋 Requirements

- Python 3.12+
- pandas, matplotlib, seaborn
- PyQt6 (for GUI)
- Internet connection (for data download)
