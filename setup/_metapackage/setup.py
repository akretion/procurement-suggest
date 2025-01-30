import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-akretion-procurement-suggest",
    description="Meta package for akretion-procurement-suggest Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-stock_orderpoint_min_max_suggest>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
