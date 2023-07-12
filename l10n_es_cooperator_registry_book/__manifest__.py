# Copyright 2023 Criptomart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cooperator Registry Book',
    'description': """
        Generate a PDF report of share movements to be presented to the Spanish Administration.""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Criptomart',
    'website': 'https://criptomart.net',
    'depends': [
        'cooperator'
    ],
    'data': [
        'reports/report_cooperator_registry_book.xml',
        'wizards/cooperator_registry_book.xml',
    ],
    'demo': [
    ],
}
