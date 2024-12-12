# Trend and Momentum Features

## 1. Exponential Moving Average (EMA)
### Formula:
$$
EMA_t = Price_t \cdot \left(\frac{2}{n + 1}\right) + EMA_{t-1} \cdot \left(1 - \frac{2}{n + 1}\right)
$$

### Description:
A weighted moving average that gives more importance to recent prices.

### Column Names:
- `ema_10` (10-period EMA)
- `ema_20` (20-period EMA)

---

## 2. Momentum Indicator
### Formula:
$$
Momentum = Price_t - Price_{t-n}
$$

### Description:
Measures the speed of price changes over a given period.

### Column Name:
- `momentum`

---

## 3. Relative Strength Index (RSI)
### Formula:
$$
RS = \frac{\text{Average Gain}}{\text{Average Loss}}
$$
$$
RSI = 100 - \frac{100}{1 + RS}
$$

### Description:
Identifies overbought or oversold conditions in the market.

### Column Name:
- `rsi`

---

## 4. Average True Range (ATR)
### Formula:
$$
TR = \max(High - Low, |High - Close_{t-1}|, |Low - Close_{t-1}|)
$$
$$
ATR = \frac{\sum_{i=1}^{n} TR_i}{n}
$$

### Description:
Measures market volatility.

### Column Name:
- `atr`

---

## 5. Directional Movement Index (DMI)
### Formula:
$$
+DM_t = \max(High_t - High_{t-1}, 0)
$$
$$
-DM_t = \max(Low_{t-1} - Low_t, 0)
$$
$$
+DI = 100 \cdot \frac{+DM}{ATR}, \quad -DI = 100 \cdot \frac{-DM}{ATR}
$$
$$
ADX = 100 \cdot \frac{|+DI - -DI|}{+DI + -DI}
$$

### Description:
Determines the direction and strength of a trend.

### Column Names:
- `plus_di` (+DI)
- `minus_di` (-DI)
- `adx` (ADX)

---

## 6. Donchian Channel
### Formula:
$$
\text{Upper Band} = \max(High_{t-n})
$$
$$
\text{Lower Band} = \min(Low_{t-n})
$$

### Description:
Identifies potential breakouts by tracking the highest high and lowest low over a period.

### Column Names:
- `donchian_upper`
- `donchian_lower`

---

## 7. Trend Persistence
### Description:
Counts the number of consecutive rising or falling periods.

### Column Names:
- `trend_rising`: Count of consecutive rising periods.
- `trend_falling`: Count of consecutive falling periods.

---

## 8. Rate of Change (ROC)
### Formula:
$$
ROC = \frac{Price_t - Price_{t-n}}{Price_{t-n}} \cdot 100
$$

### Description:
Measures the rate at which prices change over a given period.

### Column Name:
- `roc`

---

## 9. Commodity Channel Index (CCI)
### Formula:
$$
TP = \frac{High + Low + Close}{3}
$$
$$
CCI = \frac{TP - SMA(TP)}{0.015 \cdot MAD(TP)}
$$

### Description:
Identifies cyclical price patterns and overbought/oversold conditions.

### Column Name:
- `cci`

---

## 10. Kaufman’s Adaptive Moving Average (KAMA)
### Formula:
$$
KAMA = KAMA_{t-1} + SC \cdot (Price - KAMA_{t-1})
$$

Where \( SC \) is the smoothing constant based on the efficiency ratio.

### Description:
Adapts to market volatility by dynamically adjusting its smoothing factor.

### Column Name:
- `kama`

---

## 11. Stochastic Oscillator
### Formula:
$$
K = \frac{\text{Close} - \text{Low}}{\text{High} - \text{Low}} \cdot 100
$$

$$
D = \text{SMA}(K)
$$

### Description:
Compares the current price to its range over a specific period to measure momentum.

### Column Names:
- `stoch_k` (\%K)
- `stoch_d` (\%D)

---

## 12. Momentum Divergence
### Formula:
$$
Momentum\ Divergence = Momentum - ROC
$$

### Description:
Measures the difference between momentum and rate of change to identify divergences.

### Column Name:
- `momentum_divergence`

---

## 13. Chande Momentum Oscillator (CMO)
### Formula:
$$
CMO = 100 \cdot \frac{\text{Sum of Gains} - \text{Sum of Losses}}{\text{Sum of Gains} + \text{Sum of Losses}}
$$

### Description:
Evaluates the strength of momentum and identifies overbought/oversold conditions.

### Column Name:
- `cmo`