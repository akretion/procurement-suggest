import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-akretion-procurement-suggest",
    description="Meta package for akretion-procurement-suggest Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-stock_orderpoint_min_max_suggest',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
