from dotenv import dotenv_values

env = dotenv_values(".env")


class Config:
    binance_key = env['binance_key']
    binance_secret_key = env['binance_secret_key']
    redis = env['redis_staging'] if env['redis_staging'] else env['redis_local']
    redis_port = env['redis_port']
    redis_host = env['redis_host']
    # RAINTREE_MERCHANT_ID = env['RAINTREE_MERCHANT_ID']
    # BRAINTREE_PUBLIC_KEY = env['BRAINTREE_PUBLIC_KEY']
    # BRAINTREE_PRIVATE_KEY = env['BRAINTREE_PRIVATE_KEY']
    # AWS_ACCESS_KEY_ID = env['AWS_ACCESS_KEY_ID']
    # AWS_SECRET_ACCESS_KEY = env['AWS_SECRET_ACCESS_KEY']
    # AWS_STORAGE_BUCKET_NAME = env['AWS_STORAGE_BUCKET_NAME']
    # AWS_S3_CUSTOM_DOMAIN = env['AWS_S3_CUSTOM_DOMAIN']
    # AWS_S3_OBJECT_PARAMETERS = env['AWS_S3_OBJECT_PARAMETERS']
    # AWS_LOCATION = env['AWS_LOCATION']
    # STATICFILES_DIRS = env['STATICFILES_DIRS']
    # STATIC_URL = env['STATIC_URL']
    # STATICFILES_STORAGE = env['STATICFILES_STORAGE']






