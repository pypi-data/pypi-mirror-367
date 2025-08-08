# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerEvaluationValueSet(models.Model):
    _name = "partner_evaluation_value_set"
    _inherit = ["mixin.master_data"]
    _description = "Partner Evaluation Value Set"

    value_ids = fields.One2many(
        string="Values",
        comodel_name="partner_evaluation_value_set.item",
        inverse_name="set_id",
    )
