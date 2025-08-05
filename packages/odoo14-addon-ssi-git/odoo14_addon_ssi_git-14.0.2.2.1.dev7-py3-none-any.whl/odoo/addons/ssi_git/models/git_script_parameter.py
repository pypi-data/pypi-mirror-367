# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class GitScriptParameter(models.Model):
    _name = "git_script.parameter"
    _description = "Git Script Parameter Definition"

    script_id = fields.Many2one(
        string="#Script ID",
        comodel_name="git_script",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Parameter Name",
        required=True,
        help="Name of the parameter."
        "This is used to identify the parameter in the script.",
    )
    type = fields.Selection(
        string="Parameter Type",
        selection=[
            ("char", "String"),
            ("int", "Integer"),
            ("float", "Float"),
            ("bool", "Boolean"),
            ("json", "JSON Object"),
            ("date", "Date"),
            ("datetime", "Datetime"),
        ],
        default="char",
        required=True,
        help="Type of the parameter."
        "This determines how the parameter is processed in the script.",
    )
    description = fields.Text(
        string="Description",
        help="Detailed description of the parameter."
        "This is used to provide additional context or usage information.",
    )
    default_value = fields.Char(
        string="Default Value", help="Default value for the parameter."
    )
