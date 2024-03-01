# Copyright 2023 Criptomart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models, api, fields
import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)


class CooperatorRegistryBook(models.TransientModel):
    _name = "cooperator.registry.book"
    _description = "Wizard Cooperators Registry Book"

    name = fields.Char(string="name")
    summary = {}

    def _get_cooperators_data(self, query):

        partners = self.env["res.partner"].search_read(
            [query],
            [
                "name",
                "barcode_base",
                "amount_subscription",
                "fundraising_partner_type_ids",
                "vat",
                "country_id",
                "joining_date",
                "leaving_date",
                "street",
                "zip",
                "city",
                "state_id",
                "invoice_ids",
            ],
            order="barcode_base",
        )

        if query[0] == "is_member":
            self.summary["cooperators"] = len(partners)
        else:
            self.summary["old_cooperators"] = len(partners)

        for coop in partners:
            sub_req = self.env["account.invoice"].search_read(
                [
                    ("id", "in", coop["invoice_ids"]),
                    ("state", "not in", ["draft", "cancelled"]),
                    ("is_capital_fundraising", "=", True),
                ],
                [
                    "date_invoice",
                    "invoice_line_ids",
                    "partner_owned_share_id",
                    "fundraising_category_id",
                    "amount_total_signed",
                    "state",
                ],
                order="date",
            )
            for req in sub_req:
                self.summary["total_capital_subscriptions"] += req[
                    "amount_total_signed"
                ]
                self.summary["amount_per_type"][
                    req["fundraising_category_id"][1]
                ] += req["amount_total_signed"]
                req["quantity"] = 0
                lines = self.env["account.invoice.line"].browse(req["invoice_line_ids"])
                for line in lines:
                    req["quantity"] += line.quantity
                    if req["amount_total_signed"] > 0:
                        self.summary["total_shares"] += line.quantity
                    else:
                        self.summary["total_shares"] -= line.quantity

            coop["sub_req"] = sub_req
        return partners

    def print_cooperator_registry_book(self):
        self.summary = {
            "total_capital_subscriptions": 0,
            "total_shares": 0,
            "cooperators": 0,
            "old_cooperators": 0,
            "amount_per_type": defaultdict(int),
        }
        query = ("is_member", "=", True)
        coop_data = self._get_cooperators_data(query)
        query = ("is_former_member", "=", True)
        old_coop_data = self._get_cooperators_data(query)
        data = {"coops": coop_data, "old_coops": old_coop_data, "summary": self.summary}
        action = self.env.ref(
            "coop_membership_registry_book.action_report_cooperator_registry_book"
        ).report_action(None, data=data)
        action.update({"close_on_report_download": True})
        return action
