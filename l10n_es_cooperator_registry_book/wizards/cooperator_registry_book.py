# Copyright 2023 Criptomart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models, api, fields
from collections import defaultdict


class CooperatorRegistryBook(models.TransientModel):
    _name = 'cooperator.registry.book'
    _description = 'Wizard Cooperators Registry Book'

    name = fields.Char(string="name")
    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    summary = {
        "total_capital_subscriptions": 0,
        "total_shares": 0,
        "cooperators": 0,
        "old_cooperators": 0,
        "amount_per_type": defaultdict(int)
    }


    @api.model
    def _get_cooperators_data(self, query):

        partners = self.env['res.partner'].search_read(
            [query],
            ['name', 'cooperator_register_number', 'cooperator_type', 'vat', 'country_id',
             'effective_date', 'street', 'zip', 'city', 'state_id', 'subscription_request_ids', 'total_value'],
            order="cooperator_register_number"
        )

        if query[0] == "member":
            self.summary["cooperators"] = len(partners)
        else:
            self.summary["old_cooperators"] = len(partners)

        for coop in partners:
            sub_req = self.env['subscription.request'].search_read(
                [("id", "in", coop["subscription_request_ids"]),
                 ("state", "not in", ["draft", "cancelled"])],
                ['date', 'ordered_parts', 'share_product_id', 'subscription_amount', 'state', 'state', 'type'],
                order="date"
            )
            for req in sub_req:
                self.summary["total_capital_subscriptions"] += req["subscription_amount"]
                self.summary["total_shares"] += req["ordered_parts"]
                self.summary["amount_per_type"][req['share_product_id'][1]] += req["subscription_amount"]
            coop["sub_req"] = sub_req
        return partners

    def print_cooperator_registry_book(self):

        query = ("member", "=", True)
        coop_data = self._get_cooperators_data(query)
        query = ('old_member', '=', True)
        old_coop_data = self._get_cooperators_data(query)

        data = {
            "coops": coop_data,
            "old_coops": old_coop_data,
            "summary": self.summary
        }
        return self.env.ref('l10n_es_cooperator_registry_book.action_report_cooperator_registry_book').report_action(None, data=data)
