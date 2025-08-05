# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
import os
from datetime import date, datetime, time

from odoo import fields, models
from odoo.exceptions import UserError, ValidationError

try:
    import git
except ImportError:
    raise ImportError("GitPython is required. Install it with: pip install GitPython")


class GitScript(models.Model):
    _name = "git_script"
    _inherit = ["mixin.master_data"]
    _description = "Git Script Repository"

    code = fields.Char(
        default="/",
    )
    repo_id = fields.Many2one(
        string="Git Repository",
        comodel_name="git_repo",
        required=True,
    )
    branch_id = fields.Many2one(
        string="Git Branch",
        comodel_name="git_branch",
        required=True,
    )
    file_path = fields.Char(
        required=True,
        help="Path to the script file in the repository, e.g., 'scripts/my_script.py'. "
        "This is relative to the root of the repository.",
    )
    parameter_ids = fields.One2many(
        string="Parameters",
        comodel_name="git_script.parameter",
        inverse_name="script_id",
    )

    def _run(self, context_dict=None):
        self.ensure_one()

        # Get repository path from repo_id
        full_path = self.repo_id.full_path
        if not full_path or not os.path.exists(full_path):
            raise UserError(
                f"Repository path {full_path} not found. Please populate the repository first."
            )

        try:
            # Initialize git repository
            repo = git.Repo(full_path)

            # Get current branch
            current_branch = repo.active_branch.name
            target_branch = self.branch_id.name

            # Checkout to the target branch if different
            if current_branch != target_branch:
                try:
                    # Check if branch exists locally
                    if target_branch in [branch.name for branch in repo.branches]:
                        repo.git.checkout(target_branch)
                    else:
                        # Try to checkout remote branch
                        repo.git.checkout(f"origin/{target_branch}", b=target_branch)
                except Exception as checkout_error:
                    raise UserError(
                        f"Failed to checkout branch {target_branch}: {checkout_error}"
                    )

            if not os.path.exists(self.file_path):
                raise UserError(
                    f"File {self.file_path} not found in branch {target_branch}."
                )

            # Read and execute the script
            with open(self.file_path, "r") as f:
                code = compile(f.read(), self.file_path, "exec")
                exec_env = {
                    "env": self.env,
                    "UserError": UserError,
                    "ValidationError": ValidationError,
                    "datetime": datetime,
                    "date": date,
                    "time": time,
                    "log": logging.getLogger(__name__),
                    "logger": logging.getLogger(__name__),
                }
                if context_dict:
                    exec_env.update(context_dict)
                    exec(code, exec_env)
                    return exec_env.get("action")

        except git.exc.GitError as git_error:
            raise UserError(f"Git operation error: {git_error}")
        except Exception as e:
            raise UserError(f"Git script execution error: {e}")
