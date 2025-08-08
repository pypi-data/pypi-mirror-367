# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerEvaluationQuestionType(models.Model):
    _name = "partner_evaluation_question_type"
    _description = "Partner Evaluation - Question"
    _inherit = [
        "mixin.master_data",
    ]

    type = fields.Selection(
        string="Type",
        selection=[
            ("qualitative", "Qualitative"),
            ("quantitative", "Quantitative"),
        ],
        required=True,
        default="qualitative",
    )
    set_id = fields.Many2one(
        string="Value Set",
        comodel_name="partner_evaluation_value_set",
        readonly=False,
    )
    mode = fields.Selection(
        string="Mode",
        selection=[
            ("manual", "Manual"),
            ("auto", "Automatic"),
        ],
        required=True,
        default="manual",
    )
    computation_code = fields.Text(
        string="Computation Code",
    )
