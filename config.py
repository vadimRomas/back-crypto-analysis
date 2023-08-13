from dotenv import dotenv_values

env = dotenv_values(".env")


class Config:
    binance_key = env['binance_key']
    binance_secret_key = env['binance_secret_key']
    redis = env['redis_staging'] if env['redis_staging'] else env['redis_local']
    redis_port = env['redis_port']
    redis_host = env['redis_host']
    telegram_token = env['telegram_token']







