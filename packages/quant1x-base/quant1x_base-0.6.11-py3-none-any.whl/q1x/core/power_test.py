# control_degree_analyzer.py
import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
from q1x.base import cache


class EnhancedControlDegreeFramework:
    def __init__(self):
        self.results = {}
        self.signals = pd.DataFrame()
        self.backtest_results = {}

    def analyze_single_stock(self, code, name=None, data=None, **kwargs):
        if data is None or len(data) < 100:
            print(f"[{code}] 数据不足，跳过")
            return None

        df = data.copy()
        results = pd.DataFrame(index=df.index)

        # 参数
        window = kwargs.get('window', 60)
        overbought_quantile = kwargs.get('overbought_quantile', 0.95)
        oversold_quantile = kwargs.get('oversold_quantile', 0.05)
        min_interval = kwargs.get('min_interval', 10)

        # === 1. 筹码集中度 ===
        df['avg_price'] = (df['high'] + df['low'] + df['close']) / 3
        cost_mean = df['avg_price'].rolling(window, min_periods=1).mean()
        results['profit_ratio'] = (df['close'] - cost_mean) / (cost_mean + 1e-6)

        vol_ma_250 = df['volume'].rolling(250, min_periods=20).mean()
        turnover = df['volume'] / (vol_ma_250 + 1e-6)
        turnover_volatility = turnover.rolling(window, min_periods=1).std()
        results['chip_concentration'] = 1 / (turnover_volatility + 1e-6)

        price_range = (df['high'].rolling(window, min_periods=1).max() -
                       df['low'].rolling(window, min_periods=1).min() + 1e-6)
        chip_position = (df['close'] - df['low'].rolling(window, min_periods=1).min()) / price_range
        results['chip_position_adj'] = 1 - abs(chip_position - 0.5)

        results['chip_score'] = (
                (results['profit_ratio'] + 1).clip(lower=0.1) * 0.4 +
                results['chip_concentration'].clip(upper=10) * 0.3 +
                results['chip_position_adj'] * 0.3
        )

        # === 2. 量价关系 ===
        short_window, long_window = 5, 20
        price_ma_short = df['close'].rolling(short_window, min_periods=1).mean()
        price_ma_long = df['close'].rolling(long_window, min_periods=1).mean()
        price_trend = price_ma_short / (price_ma_long + 1e-6)

        vol_ma_short = df['volume'].rolling(short_window, min_periods=1).mean()
        vol_ma_long = df['volume'].rolling(long_window, min_periods=1).mean()
        volume_trend = vol_ma_short / (vol_ma_long + 1e-6)

        ret_5 = df['close'].pct_change(periods=5)
        turnover_5 = turnover.rolling(5, min_periods=1).mean()
        control_coef = ret_5 / (turnover_5 + 1e-6)

        results['vp_score'] = np.where(
            (price_trend > 1) & (volume_trend < 1),
            control_coef,
            -abs(control_coef)
        )

        # === 3. 主力资金活跃度 ===
        vol_ma_20 = df['volume'].rolling(20, min_periods=1).mean()
        is_large = df['volume'] > vol_ma_20 * 0.8
        large_flow = np.where(
            df['close'] >= df['open'],
            df['volume'] * is_large,
            -df['volume'] * is_large
        )
        results['main_capital_score'] = pd.Series(large_flow).rolling(5, min_periods=1).sum()

        # === 4. 技术形态 ===
        upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20)
        boll_width = (upper - lower) / (middle + 1e-6)
        long_positive = (df['close'] - df['open']) / (df['high'] - df['low'] + 1e-6)

        results['tech_score'] = (
                (1 / (boll_width + 1e-6)) * 0.5 +
                long_positive.fillna(0) * 0.5
        )

        # === 5. 综合控盘度 ===
        weights = {
            'chip_score': 0.3,
            'vp_score': 0.3,
            'main_capital_score': 0.2,
            'tech_score': 0.2
        }

        def safe_z(x):
            if len(x) < 2: return 0.0
            return (x[-1] - np.mean(x)) / (np.std(x) + 1e-6)

        final_score = pd.Series(0.0, index=df.index)
        for col in weights.keys():
            if col not in results: continue
            raw_series = results[col].replace([np.inf, -np.inf], np.nan).fillna(0)
            z_series = raw_series.rolling(window=60, min_periods=10).apply(safe_z, raw=True)
            final_score += z_series * weights[col]

        control_degree_raw = 50 + 50 * np.tanh(final_score)
        control_degree = control_degree_raw.fillna(50).clip(0, 100)

        # === 6. 动态阈值（修复版）===
        roll = control_degree.rolling(60, min_periods=20)
        oversold = roll.quantile(oversold_quantile)      # Series
        overbought = roll.quantile(overbought_quantile)  # Series

        # 填充缺失
        oversold = oversold.fillna(method='bfill').fillna(40)
        overbought = overbought.fillna(method='bfill').fillna(80)

        # === 7. 生成信号 ===
        signal = pd.DataFrame(index=df.index)
        signal['code'] = code
        signal['name'] = name or cache.stock_name(code) or code
        signal['close'] = df['close']
        signal['control_degree'] = control_degree
        signal['overbought'] = overbought.values
        signal['oversold'] = oversold.values
        signal['prev_cd'] = signal['control_degree'].shift(1)

        # 信号判断
        signal['buy_signal'] = (signal['prev_cd'] <= signal['oversold']) & (signal['control_degree'] > signal['oversold'])
        signal['sell_signal'] = (signal['prev_cd'] >= signal['overbought']) & (signal['control_degree'] < signal['overbought'])

        # 冷却期
        signal['final_signal'] = 0
        last_signal_pos = None
        for i in range(1, len(signal)):
            if signal['buy_signal'].iloc[i]:
                if last_signal_pos is None or (i - last_signal_pos) >= min_interval:
                    signal.iloc[i, signal.columns.get_loc('final_signal')] = 1
                    last_signal_pos = i
            elif signal['sell_signal'].iloc[i]:
                if last_signal_pos is None or (i - last_signal_pos) >= min_interval:
                    signal.iloc[i, signal.columns.get_loc('final_signal')] = -1
                    last_signal_pos = i

        # 保存
        self.results[code] = {
            'data': df,
            'control_degree': control_degree,
            'full_results': signal.copy()
        }

        return signal

    def analyze_batch(self, stock_list, **kwargs):
        signals = []
        for item in tqdm(stock_list, desc="Analyzing Stocks"):
            if isinstance(item, (list, tuple)):
                code, name = item
            else:
                code, name = item, None

            try:
                klines = cache.klines(code)
                df = cache.convert_klines_trading(klines, period='d')
                df.index = pd.to_datetime(df.index)  # 关键：转为日期
                if len(df) > 400:
                    df = df.tail(400)

                sig = self.analyze_single_stock(code, name=name, data=df, **kwargs)
                if sig is not None:
                    signals.append(sig.reset_index())
            except Exception as e:
                print(f"[{code}] 分析失败: {str(e)}")

        if signals:
            self.signals = pd.concat(signals, ignore_index=True)
            self.signals['date'] = pd.to_datetime(self.signals['index'])
            self.signals.set_index('date', inplace=True)

        return self.signals

    def backtest(self, holding_days=10):
        if self.signals.empty:
            raise ValueError("No signals to backtest")

        trades = []
        for code in self.signals['code'].unique():
            stock_data = self.signals[self.signals['code'] == code].copy()
            buy_signals = stock_data[stock_data['final_signal'] == 1]

            for idx, row in buy_signals.iterrows():
                future = stock_data.loc[idx:].head(holding_days + 1)
                if len(future) < holding_days + 1:
                    continue
                entry_price = row['close']
                exit_price = future.iloc[-1]['close']
                ret = (exit_price - entry_price) / entry_price
                trades.append({
                    'code': code,
                    'name': row['name'],
                    'entry_date': idx,
                    'exit_date': future.index[-1],
                    'holding_days': holding_days,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'return': ret
                })

        self.trades = pd.DataFrame(trades)
        win_rate = (self.trades['return'] > 0).mean() if len(self.trades) > 0 else np.nan
        avg_return = self.trades['return'].mean() if len(self.trades) > 0 else np.nan
        annualized = (1 + avg_return) ** (252 / holding_days) - 1 if avg_return > 0 else np.nan

        self.backtest_results = {
            'total_trades': len(self.trades),
            'win_rate': win_rate,
            'avg_return': avg_return,
            'annualized_return': annualized,
            'trades': self.trades
        }

        return self.backtest_results

    def plot_stock(self, code):
        if code not in self.results:
            print(f"[{code}] 没有分析结果")
            return

        result = self.results[code]
        df = result['data']
        signal = result['full_results']

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

        ax1.plot(df.index, df['close'], label='Price', color='black', linewidth=1.2)
        buys = signal[signal['final_signal'] == 1]
        sells = signal[signal['final_signal'] == -1]
        ax1.scatter(buys.index, df.loc[buys.index]['close'], color='green', label='Buy', marker='^', s=100, zorder=5)
        ax1.scatter(sells.index, df.loc[sells.index]['close'], color='red', label='Sell', marker='v', s=100, zorder=5)
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, axis='y', alpha=0.3)

        ax2.plot(signal.index, signal['control_degree'], label='Control Degree', color='blue')
        ax2.plot(signal.index, signal['overbought'], color='red', linestyle='--', label='Overbought')
        ax2.plot(signal.index, signal['oversold'], color='green', linestyle='--', label='Oversold')
        ax2.fill_between(signal.index, signal['control_degree'], signal['overbought'],
                         where=(signal['control_degree'] > signal['overbought']),
                         color='red', alpha=0.2)
        ax2.fill_between(signal.index, signal['control_degree'], signal['oversold'],
                         where=(signal['control_degree'] < signal['oversold']),
                         color='green', alpha=0.2)
        ax2.set_ylabel('Control Degree')
        ax2.legend()
        ax2.grid(True, axis='y', alpha=0.3)

        plt.suptitle(f'{code} - Control Degree Analysis (Dynamic Threshold)', fontsize=14)
        plt.xlabel('Date')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def export_results(self, output_dir='output'):
        os.makedirs(output_dir, exist_ok=True)
        self.signals.to_csv(f'{output_dir}/all_signals.csv', encoding='utf-8-sig')
        if hasattr(self, 'backtest_results') and self.backtest_results:
            pd.Series(self.backtest_results).drop('trades', errors='ignore').to_json(
                f'{output_dir}/backtest_summary.json', force_ascii=False)
            if 'trades' in self.backtest_results:
                self.backtest_results['trades'].to_csv(f'{output_dir}/trades.csv', index=False, encoding='utf-8-sig')
        print(f"✅ 结果已导出到目录: {output_dir}")

if __name__ == "__main__":
    stock_list = ['sh603488', 'sz000158']

    framework = EnhancedControlDegreeFramework()
    signals = framework.analyze_batch(
        stock_list=stock_list,
        window=60,
        oversold_quantile=0.05,
        overbought_quantile=0.95,
        min_interval=10
    )

    bt_result = framework.backtest(holding_days=10)
    print("📊 回测结果:", bt_result)

    framework.plot_stock('sz000158')
    framework.export_results()