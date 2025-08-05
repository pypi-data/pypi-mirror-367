# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class GitBranch(models.Model):
    _name = "git_branch"
    _inherit = ["mixin.master_data"]
    _description = "Git Branch"

    repo_id = fields.Many2one(
        string="Repo",
        comodel_name="git_repo",
        required=True,
    )
    last_commit_sha = fields.Char(
        string="Last Commit SHA",
    )
    last_commit_message = fields.Char(
        string="Last Commit Message",
    )
    last_commit_date = fields.Datetime(
        string="Last Commit Date",
    )
    last_commit_author = fields.Char(
        string="Last Commit Author",
    )
