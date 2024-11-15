from odoo import fields, models
from odoo.exceptions import UserError


class Loan(models.Model):
    _name = "loan.loan"
    _description = "Loan Records"

    title = fields.Char(string="Title", required=True)
    amount = fields.Monetary(
        string="Amount", currency_field="currency_id", required=True
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    time_needed = fields.Date(string="Time needed", required=True)
    state = fields.Selection(
        [
            ("review", "Under Review"),
            ("cancel", "Request Canceled"),
            ("approved", "Request Approved"),
            ("rejected", "Request Rejected"),
            ("paid", "Loan Paid"),
        ],
        string="State",
        default="review",
        required=True,
    )
    description = fields.Text(string="Description")
    approved_ids = fields.Many2many("res.users", string="Approved Users")

    def cancel_request(self):
        if self.state == "review" or self.state == "approved":
            self.write({"state": "cancel"})
        else:
            raise UserError("You can't cancel this Request")

    def approve_request(self):
        if self.env.user not in self.approved_ids and self.state == "review":
            self.write({"approved_ids": [(4, self.env.user.id)]})

            loan_management_group = self.env["res.groups"].search(
                [("name", "=", "loan_management")], limit=1
            )
            if loan_management_group and len(self.approved_ids) == len(
                loan_management_group.users
            ):
                self.write({"state": "approved"})
        else:
            raise UserError("You can't approve this Request")

    def reject_request(self):
        if self.env.user not in self.approved_ids and self.state == "review":
            self.write({"state": "rejected"})
        else:
            raise UserError("You can't reject this Request")

    def pay_loan(self):
        if self.state == "approved":
            self.write({"state": "paid"})
        else:
            raise UserError("You can't pay this Request")
