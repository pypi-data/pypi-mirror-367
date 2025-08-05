# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class GitUser(models.Model):
    _name = "git_user"
    _inherit = ["mixin.master_data"]
    _description = "Git User Definition"

    code = fields.Char(
        default="/",
    )
    git_username = fields.Char(
        string="Username",
        help="Git Username",
        required=True,
        copy=False,
    )
    git_token = fields.Char(
        string="Token",
        help="Git Token",
        required=True,
        copy=False,
    )
