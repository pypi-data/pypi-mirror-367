# Fair Value Estimation Example

MarketSwimmer v2.0.32+ includes fair stock price estimation based on Owner Earnings per Share.

## How It Works

The fair value estimation:

1. **Extracts Shares Outstanding** from financial statements
2. **Calculates Owner Earnings per Share** for each year
3. **Computes Average Owner Earnings per Share** across all available years
4. **Applies Valuation Multiples** to estimate fair price ranges

## Example Output

When you run MarketSwimmer analysis, you'll see:

```
[VALUATION] ESTIMATED FAIR STOCK PRICE:
------------------------------------------------------------
   Based on 7 years of data
   Average Owner Earnings/Share: $8.45
   Methodology: Average Owner Earnings Per Share × Valuation Multiple

[PRICE] Fair Value Estimates:
   Conservative (10x):    $84.50
   Moderate (15x):       $126.75
   Growth (20x):         $169.00
   Aggressive (25x):     $211.25

[DETAIL] Owner Earnings Per Share by Period:
   2024: $12.34/share
   2023: $8.67/share
   2022: $5.23/share
   ...
```

## Methodology

- **Conservative Approach**: Uses Owner Earnings (more conservative than reported net income)
- **Multi-Year Average**: Smooths out yearly fluctuations for stable valuation
- **Multiple Scenarios**: Provides range from conservative to aggressive valuations
- **Historical Basis**: Based on actual financial performance, not projections

## Usage

Simply run your normal MarketSwimmer analysis:

```bash
# Command line
marketswimmer TICKER

# Or programmatically
from marketswimmer.core.owner_earnings import main
main()
```

The fair value estimates will automatically appear at the end of the analysis report if shares outstanding data is available in the financial statements.

## Important Notes

- Fair value estimates are based on historical data and should not be considered investment advice
- Consider current market conditions, growth prospects, and risk factors
- Owner Earnings methodology provides a conservative baseline for valuation
- Multiple scenarios help understand valuation sensitivity to different assumptions
