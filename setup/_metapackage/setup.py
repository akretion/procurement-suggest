import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-akretion-procurement-suggest",
    description="Meta package for akretion-procurement-suggest Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-purchase_suggest',
        'odoo9-addon-purchase_suggest_min_qty_on_product',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
