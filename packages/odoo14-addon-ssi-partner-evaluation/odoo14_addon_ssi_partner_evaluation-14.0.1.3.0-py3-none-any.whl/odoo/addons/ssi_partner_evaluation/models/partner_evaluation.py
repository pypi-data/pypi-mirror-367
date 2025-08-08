# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.ssi_decorator import ssi_decorator


class PartnerEvaluation(models.Model):
    _name = "partner_evaluation"
    _description = "Partner Evaluation"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
        "mixin.transaction_open",
        "mixin.transaction_date_duration",
        "mixin.many2one_configurator",
        "mixin.transaction_partner",
        "mixin.localdict",
    ]
    _order = "date desc, id"

    # Multiple Approval Attribute
    _approval_from_state = "open"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _method_to_run_from_wizard = "action_cancel"

    _statusbar_visible_label = "draft,open,confirm,done"
    _policy_field_order = [
        "open_ok",
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]

    _header_button_order = [
        "action_open",
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_open",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    type_id = fields.Many2one(
        comodel_name="partner_evaluation_type",
        string="Type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date = fields.Date(
        string="Date",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    question_ids = fields.One2many(
        comodel_name="partner_evaluation.question",
        inverse_name="evaluation_id",
        string="Questions",
        readonly=True,
        states={"open": [("readonly", False)]},
    )
    automatic_result_id = fields.Many2one(
        string="Automatic Result",
        comodel_name="partner_evaluation_result",
        compute="_compute_automatic_result_id",
        store=True,
        compute_sudo=True,
    )
    manual_result_id = fields.Many2one(
        string="Manual Result",
        comodel_name="partner_evaluation_result",
        readonly=True,
        states={"open": [("readonly", False)]},
    )
    final_result_id = fields.Many2one(
        string="Final Result",
        comodel_name="partner_evaluation_result",
        compute="_compute_final_result_id",
        store=True,
        compute_sudo=True,
    )
    dissenting_opinion = fields.Text(
        string="Dissenting Opinion",
        readonly=True,
        states={"open": [("readonly", False)]},
    )

    @api.depends(
        "question_ids",
        "question_ids.qualitative_value_id",
        "question_ids.quantitative_value",
    )
    def _compute_automatic_result_id(self):
        for record in self:
            result = False
            localdict = record._get_default_localdict()
            try:
                safe_eval(
                    record.type_id.result_computation_code,
                    localdict,
                    mode="exec",
                    nocopy=True,
                )
                result = localdict["result"]
            except Exception:
                result = False

            record.automatic_result_id = result

    @api.depends(
        "automatic_result_id",
        "manual_result_id",
    )
    def _compute_final_result_id(self):
        for record in self:
            result = record.automatic_result_id
            if record.manual_result_id:
                result = record.manual_result_id
            record.final_result_id = result

    @ssi_decorator.post_open_action()
    def _01_create_questions(self):
        self.ensure_one()
        for question in self.type_id.question_ids:
            question._create_evaluation_question(self)

    @ssi_decorator.post_done_action()
    def _01_create_partner_evaluation_result(self):
        self.ensure_one()
        if not self.partner_id._get_partner_evaluation_result(self.type_id):
            data = {
                "partner_id": self.partner_id.id,
                "type_id": self.type_id.id,
            }
            self.env["res.partner.evaluation_result"].create(data)

    @ssi_decorator.post_cancel_action()
    def _01_delete_question(self):
        self.ensure_one()
        self.question_ids.unlink()

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "open_ok",
            "confirm_ok",
            "approve_ok",
            "cancel_ok",
            "done_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
