# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class GitRepoType(models.Model):
    _name = "git_repo_type"
    _inherit = ["mixin.master_data"]
    _description = "Git Repository Type"

    can_cloning = fields.Boolean(
        string="Can Cloning",
        help="If checked, this repository type can be cloned.",
        default=False,
    )
    repo_type = fields.Selection(
        string="Repo Type",
        selection=[
            ("public", "Public"),
            ("private", "Private"),
        ],
        default="public",
        required=True,
    )
