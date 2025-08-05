# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class GitScriptParameterValue(models.Model):
    _name = "git_script.parameter_value"
    _description = "Git Script Parameter Value per Server Action"
    _order = "script_id"

    model = fields.Char(
        string="Related Document Model",
        index=True,
    )
    res_id = fields.Integer(
        string="Related Document ID",
        index=True,
    )
    script_id = fields.Many2one(
        string="Script",
        comodel_name="git_script",
        required=True,
        copy=False,
    )
    parameter_id = fields.Many2one(
        string="Parameter",
        comodel_name="git_script.parameter",
        required=True,
        ondelete="cascade",
    )
    type = fields.Selection(
        related="parameter_id.type",
    )
    value = fields.Char(
        string="Parameter Value",
        required=True,
    )

    @api.constrains(
        "value",
        "parameter_id",
    )
    def _check_value_format(self):
        for rec in self:
            t = rec.type
            v = rec.value
            try:
                if t == "int":
                    int(v)
                elif t == "float":
                    float(v)
                elif t == "bool":
                    if v.lower() not in ("1", "0", "true", "false", "yes", "no"):
                        raise ValueError()
                elif t == "json":
                    json.loads(v)
                elif t == "date":
                    datetime.strptime(v, "%Y-%m-%d")
                elif t == "datetime":
                    datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            except Exception:
                raise ValidationError(
                    f"Invalid value format for parameter "
                    f"'{rec.parameter_id.name}' (type {t})."
                )

    def parse_value(self):
        t = self.type
        v = self.value
        try:
            if t == "int":
                return int(v)
            elif t == "float":
                return float(v)
            elif t == "bool":
                return v.lower() in ("1", "true", "yes")
            elif t == "json":
                return json.loads(v)
            elif t == "date":
                return datetime.strptime(v, "%Y-%m-%d").date()
            elif t == "datetime":
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            return v
        except Exception as e:
            raise UserError(
                f"Invalid value for parameter " f"'{self.parameter_id.name}': {e}"
            )
