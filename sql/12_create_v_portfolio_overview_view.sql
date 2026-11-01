CREATE VIEW v_portfolio_overview AS
SELECT dim_date.full_date, dim_date.year, dim_date.quarter, dim_date.month, dim_date.is_trading_day, dim_asset.ticker, dim_asset.company_name, dim_asset.sector, dim_asset.country, fact_daily_prices.close, fact_daily_prices.volume, fact_daily_prices.log_change, fact_daily_prices.volatility_21, fact_daily_prices.drawdown
FROM fact_daily_prices
JOIN dim_date ON dim_date.date_id = fact_daily_prices.date_id
JOIN dim_asset ON dim_asset.asset_id = fact_daily_prices.asset_id;