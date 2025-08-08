# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PartnerEvaluationItem(models.Model):
    _name = "partner_evaluation_result"
    _description = "Partner Evaluation Result"
    _inherit = [
        "mixin.master_data",
    ]
