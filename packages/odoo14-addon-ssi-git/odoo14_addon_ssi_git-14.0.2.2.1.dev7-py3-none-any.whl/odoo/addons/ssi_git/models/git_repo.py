# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
import os
import shutil
from datetime import timezone
from urllib.parse import quote

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import git
except ImportError:
    _logger.debug("GitPython is required. Install it with: 'pip install GitPython'")

try:
    pass
except ImportError:
    _logger.debug("GitPython is required. Install it with: 'pip install pytz'")


class GitRepo(models.Model):
    _name = "git_repo"
    _inherit = ["mixin.master_data"]
    _description = "Git Repository"

    type_id = fields.Many2one(
        string="Type",
        comodel_name="git_repo_type",
        required=True,
    )
    repo_type = fields.Selection(
        related="type_id.repo_type",
    )
    git_user_id = fields.Many2one(
        string="User",
        comodel_name="git_user",
        required=False,
    )
    can_cloning = fields.Boolean(
        related="type_id.can_cloning",
    )
    url = fields.Char(
        string="Git URL",
        required=True,
    )
    repo_path = fields.Char(
        string="Repository Path",
        required=True,
        readonly=False,
    )
    full_path = fields.Char(
        string="Repository Full Path",
        required=False,
        readonly=True,
    )
    branch_ids = fields.One2many(
        string="Branches",
        comodel_name="git_branch",
        inverse_name="repo_id",
        readonly=True,
        copy=False,
    )
    script_ids = fields.One2many(
        string="Scripts",
        comodel_name="git_script",
        inverse_name="repo_id",
        copy=False,
    )

    def action_populate(self):
        for record in self.sudo():
            record._populate()
            if record.can_cloning:
                record._populate_script()

    def _populate_no_clone(self):
        self.ensure_one()
        full_path = os.path.join(self.repo_path, f"{self.name}")
        self.full_path = full_path

        if os.path.exists(full_path):
            repo = git.Repo(full_path)
            branches = [head for head in repo.heads]
            for branch in branches:
                existing_branch = self._check_branch_object(branch)
                if existing_branch:
                    # Update existing branch
                    self._update_branch(branch, existing_branch)
                else:
                    # Create new branch
                    self._create_branch(branch)

    def _populate_script(self):
        self.ensure_one()

        for branch_id in self.branch_ids:
            files = self.list_files_in_branch(self.full_path, branch_id.name)
            for file_name in files:
                self._create_script(file_name, branch_id.id)

    def _populate_branch(self, repo):
        self.ensure_one()
        all_branches = []

        # Add local branches
        for branch in repo.branches:
            all_branches.append(branch)

        for remote_ref in repo.remotes.origin.refs:
            branch_name = remote_ref.name.replace("origin/", "")
            # Skip HEAD reference
            if branch_name == "HEAD":
                continue
            # Check if local branch already exists
            local_exists = any(b.name == branch_name for b in repo.branches)
            if not local_exists:
                # Create local tracking branch
                try:
                    local_branch = repo.create_head(branch_name, remote_ref)
                    local_branch.set_tracking_branch(remote_ref)
                    all_branches.append(local_branch)
                except Exception:
                    raise UserError(
                        f"Warning: Could not create local branch {branch_name}"
                    )

        if not all_branches:
            raise UserError(_("No branches found in the repository."))

        for branch in all_branches:
            existing_branch = self._check_branch_object(branch.name)
            if existing_branch:
                # Update existing branch
                self._update_branch(branch, existing_branch)
            else:
                # Create new branch
                self._create_branch(branch)

    def _populate(self):
        self.ensure_one()
        token = False
        username = False

        if not self.url:
            msg_error = _("Repository URL is not set.")
            raise UserError(msg_error)

        if not self.can_cloning:
            self._populate_no_clone()
            return True

        if self.repo_type == "private":
            token, username = self._get_authentication()
            auth_url = self._get_auth_url(self.url, token, username)

        # Prepare repository path - use persistent storage instead of temp
        repo_name = os.path.basename(self.url).replace(".git", "")
        full_path = os.path.join(self.repo_path, f"{repo_name}")
        self.full_path = full_path

        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        # Clean up corrupted repo if exists
        self._clean_full_path(full_path)

        try:
            if os.path.exists(full_path):
                repo = git.Repo(full_path)

                # Update remote URL if authentication provided
                if token and username:
                    repo.remotes.origin.set_url(auth_url)

                # Fetch all remote branches and updates
                repo.remotes.origin.fetch()

                # Pull latest changes for current branch
                try:
                    repo.remotes.origin.pull()
                except Exception as pull_error:
                    raise UserError(
                        f"Warning: Could not pull latest changes: {pull_error}"
                    )

            else:
                repo = git.Repo.clone_from(auth_url, full_path)

            # Fetch all remote branches to get complete branch list
            repo.remotes.origin.fetch()

        except Exception as e:
            raise UserError(_("Git operation error: %s") % str(e))

        self._populate_branch(repo)

    def list_files_in_branch(self, full_path, branch_name):
        repo = git.Repo(full_path)
        commit = repo.heads[branch_name].commit
        tree = commit.tree

        file_list = []

        def traverse_tree(tree, prefix=""):
            for item in tree:
                path = f"{prefix}/{item.name}" if prefix else item.name
                if item.type == "blob" and path.endswith(".py"):
                    file_list.append(path)
                elif item.type == "tree":
                    traverse_tree(item, path)

        traverse_tree(tree)
        return file_list

    def _get_authentication(self):
        self.ensure_one()
        token = self.git_user_id.git_token
        username = self.git_user_id.git_username
        if not token and not username:
            _msg_error = _("No Git User Define!")
            raise UserError(_msg_error)

        return token, username

    def _get_auth_url(self, repo_url, token=None, username=None):
        self.ensure_one()
        if token and repo_url.startswith("https://"):
            if username:
                auth_part = f"{quote(username)}:{quote(token)}"
            else:
                auth_part = token
            return repo_url.replace("https://", f"https://{auth_part}@", 1)
        return repo_url

    def _clean_full_path(self, full_path):
        """
        Clean up repository path if needed
        """
        self.ensure_one()
        try:
            if os.path.exists(full_path):
                # Check if it's a valid git repo
                try:
                    test_repo = git.Repo(full_path)
                    # If repo is corrupted, remove it
                    if test_repo.git_dir is None:
                        shutil.rmtree(full_path)
                        return True
                except Exception:
                    # If not a valid repo, remove it
                    shutil.rmtree(full_path)
                    return True
            return False
        except Exception as e:
            raise UserError(f"Warning: Could not clean repo path: {e}")

    def _check_branch_object(self, branch_name):
        """
        Check if branch exists and return the branch object
        """
        self.ensure_one()
        obj_git_branch = self.env["git_branch"]
        criteria = [
            ("name", "=", branch_name),
            ("repo_id", "=", self.id),
        ]
        existing_branch = obj_git_branch.search(criteria, limit=1)
        return existing_branch if existing_branch else False

    def _check_script_object(self, script_name, branch_id):
        """
        Check if script exists and return the script object
        """
        self.ensure_one()
        obj_git_script = self.env["git_script"]
        criteria = [
            ("name", "=", script_name),
            ("repo_id", "=", self.id),
            ("branch_id", "=", branch_id),
        ]
        existing_script = obj_git_script.search(criteria, limit=1)
        return existing_script if existing_script else False

    def _update_branch(self, branch, existing_branch):
        """
        Update existing branch with latest information
        """
        self.ensure_one()
        try:
            # Get latest commit info
            latest_commit = branch.commit

            update_data = {
                "last_commit_sha": latest_commit.hexsha,
                "last_commit_message": latest_commit.message.strip(),
                "last_commit_date": self._convert_to_utc(
                    latest_commit.committed_datetime
                ),
                "last_commit_author": latest_commit.author.name,
            }

            existing_branch.write(update_data)

        except Exception as e:
            raise UserError(f"Warning: Could not update branch {branch.name}: {e}")

    def _convert_to_utc(self, dt):
        """
        Convert datetime to user timezone if available, otherwise UTC
        """
        self.ensure_one()
        if dt is None:
            return None

        try:
            # If datetime is naive (no timezone info)
            if dt.tzinfo is None:
                # No user timezone, assume it's already UTC
                return dt

            # If datetime has timezone info
            if dt.tzinfo is not None:
                # Convert to UTC
                utc_dt = dt.astimezone(timezone.utc)
                # Remove timezone info for Odoo (which expects naive datetime in UTC)
                return utc_dt.replace(tzinfo=None)

            return dt

        except Exception:
            # Fallback: return original datetime if conversion fails
            return dt.replace(tzinfo=None) if dt.tzinfo else dt

    def _prepare_branch_data(self, branch):
        self.ensure_one()
        return {
            "name": branch.name,
            "code": "/",
            "repo_id": self.id,  # Changed from repo_id to repo_id
        }

    def _create_branch(self, branch):
        self.ensure_one()
        try:
            branch_data = self._prepare_branch_data(branch)

            # Add additional commit information
            try:
                latest_commit = branch.commit

                branch_data.update(
                    {
                        "last_commit_sha": latest_commit.hexsha,
                        "last_commit_message": latest_commit.message.strip(),
                        "last_commit_date": self._convert_to_utc(
                            latest_commit.committed_datetime
                        ),
                        "last_commit_author": latest_commit.author.name,
                    }
                )
            except Exception:
                raise UserError(f"Warning: Could not get commit info for {branch.name}")

            self.env["git_branch"].create(branch_data)

        except Exception as e:
            raise UserError(f"Error creating branch {branch.name}: {e}")

    def _prepare_script_data(self, script_name, branch_id):
        self.ensure_one()
        return {
            "name": script_name,
            "code": "/",
            "repo_id": self.id,
            "branch_id": branch_id,
            "file_path": self.full_path + "/" + script_name,
        }

    def _create_script(self, script_name, branch_id):
        self.ensure_one()
        try:
            existing_script = self._check_script_object(script_name, branch_id)
            if not existing_script:
                script_data = self._prepare_script_data(script_name, branch_id)
                self.env["git_script"].create(script_data)
        except Exception as e:
            raise UserError(f"Error creating script {script_name}: {e}")
