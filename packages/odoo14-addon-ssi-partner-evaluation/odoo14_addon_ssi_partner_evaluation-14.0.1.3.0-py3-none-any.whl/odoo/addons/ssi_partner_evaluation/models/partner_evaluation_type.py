# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerEvaluationType(models.Model):
    _name = "partner_evaluation_type"
    _description = "Partner Evaluation Type"
    _inherit = [
        "mixin.master_data",
    ]

    result_ids = fields.Many2many(
        string="Allowed Results",
        comodel_name="partner_evaluation_result",
        relation="rel_partner_evaluation_type_2_result",
        column1="type_id",
        column2="result_id",
    )
    result_computation_code = fields.Text(
        string="Result Computation Code",
        required=True,
    )
    question_ids = fields.One2many(
        comodel_name="partner_evaluation_type.question",
        inverse_name="type_id",
        string="Questions",
    )
