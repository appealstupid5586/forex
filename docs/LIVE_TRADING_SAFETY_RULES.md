# LIVE TRADING SAFETY RULES

## Luật khóa vốn thật

1. Không bật `ALLOW_LIVE_EXECUTION=true` nếu chưa qua backtest, walk-forward, paper trading và small-live.
2. Mọi order phải có `robot_id`, `cycle_id`, `magic_number`, `broker_order_id`.
3. Risk Guard luôn chạy trước Execution Adapter.
4. Nếu drawdown vượt ngưỡng: chuyển `FREEZE`.
5. Nếu spread bất thường: `PAUSE_NEW_ENTRY`.
6. Nếu mất dữ liệu nguồn độc lập: `PAUSE_EXECUTION`.
7. Nếu order không thuộc robot/cycle: Sweep Agent xử lý.
8. Không cho agent tự ý tăng lot, tăng leverage hoặc thay đổi max drawdown khi đang live.

## Promotion ladder

Backtest → Walk-forward → Paper → Small Live → Scale Live.
