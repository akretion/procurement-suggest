import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-akretion-procurement-suggest",
    description="Meta package for akretion-procurement-suggest Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-procurement_suggest',
        'odoo10-addon-purchase_suggest',
        'odoo10-addon-purchase_suggest_min_qty_on_product',
        'odoo10-addon-stock_orderpoint_min_max_suggest',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 10.0',
    ]
)
