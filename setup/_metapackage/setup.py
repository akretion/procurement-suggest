import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-akretion-procurement-suggest",
    description="Meta package for akretion-procurement-suggest Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-procurement_suggest',
        'odoo12-addon-stock_orderpoint_min_max_suggest',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
