import braintree
#
# gateway = braintree.BraintreeGateway(
#     braintree.Configuration(
#         braintree.Environment.Sandbox,
#         merchant_id=os.environ.get('RAINTREE_MERCHANT_ID'),
#         public_key=os.environ.get('BRAINTREE_PUBLIC_KEY'),
#         private_key=os.environ.get('BRAINTREE_PRIVATE_KEY')
#     )
# )
#
# result = gateway.customer.create({
#     "first_name": "Vadym",
#     "last_name": "Romas",
#     "company": "study_payment",
#     "email": "romasvadim10@gmail.com",
#     "phone": "312.555.1234",
#     "fax": "614.555.5678",
#     "website": "www.example.com"
# })


def confirm_gateway():
    braintree_env = braintree.Environment.Sandbox
    RAINTREE_MERCHANT_ID = '29x4tywkxfcyc93z'
    BRAINTREE_PUBLIC_KEY = "xvgmwd69rmh9x8ws"
    BRAINTREE_PRIVATE_KEY = "d44cb66ff68c29bc0d78a92e473afb5a"

    # Configure Braintree
    braintree.Configuration.configure(
        braintree.Environment.Sandbox,
        merchant_id=RAINTREE_MERCHANT_ID,
        public_key=BRAINTREE_PUBLIC_KEY,
        private_key=BRAINTREE_PRIVATE_KEY
    )
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id=RAINTREE_MERCHANT_ID,
            public_key=BRAINTREE_PUBLIC_KEY,
            private_key=BRAINTREE_PRIVATE_KEY
        )
    )
    result = gateway.customer.create({
        "first_name": "Vadym",
        "last_name": "Romas",
        "company": "study_payment",
        "email": "romasvadim10@gmail.com",
        "phone": "312.555.1234",
        "fax": "614.555.5678",
        "website": "www.example.com"
    })

    return result
