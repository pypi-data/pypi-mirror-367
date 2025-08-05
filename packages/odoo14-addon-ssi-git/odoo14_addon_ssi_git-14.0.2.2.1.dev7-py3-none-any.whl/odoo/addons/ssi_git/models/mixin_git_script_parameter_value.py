# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class MixinGitScriptParameterValue(models.AbstractModel):
    _name = "mixin.git_script.parameter_value"
    _inherit = [
        "mixin.decorator",
    ]
    _description = "Mixin Object for Git Script Parameter Value"
    _parameter_value_create_page = False
    _parameter_value_page_xpath = "//page[last()]"

    parameter_value_ids = fields.One2many(
        string="Parameter Values",
        comodel_name="git_script.parameter_value",
        inverse_name="res_id",
        domain=lambda self: [("model", "=", self._name)],
        auto_join=True,
    )

    @ssi_decorator.insert_on_form_view()
    def _parameter_value_insert_form_element(self, view_arch):
        # raise UserError("Masuk")
        if self._parameter_value_create_page:
            view_arch = self._add_view_element(
                view_arch=view_arch,
                qweb_template_xml_id="ssi_git.parameter_value",
                xpath=self._parameter_value_page_xpath,
                position="after",
            )
        return view_arch

    def has_git_script_relation(self):
        self.ensure_one()
        git_script_fields = []
        model_fields = self._fields

        for field_name, field_obj in model_fields.items():
            if hasattr(field_obj, "comodel_name"):
                comodel_name = field_obj.comodel_name
                if comodel_name == "git_script":
                    git_script_fields.append(field_name)

        return git_script_fields

    def action_populate_parameter_value_ids(self):
        for record in self:
            record._populate_parameter_value_ids()

    def _sync_parameter_value_ids(self):
        self.ensure_one()

        git_script_fields = self.has_git_script_relation()

        if git_script_fields:
            valid_parameter_ids = set()

            for field_name in git_script_fields:
                field_value = getattr(self, field_name, False)
                if field_value:
                    git_script = field_value if hasattr(field_value, "_name") else False
                    if git_script and git_script._name == "git_script":
                        valid_parameter_ids.update(git_script.parameter_ids.ids)

            invalid_parameter_values = self.parameter_value_ids.filtered(
                lambda pv: pv.parameter_id.id not in valid_parameter_ids
            )
            if invalid_parameter_values:
                invalid_parameter_values.unlink()
        else:
            self.parameter_value_ids.unlink()

    def _populate_parameter_value_ids(self):
        self.ensure_one()
        obj_parameter_value = self.env["git_script.parameter_value"]
        created_parameter_values = self.env["git_script.parameter_value"]

        # Menghapus parameter dari parent apabila ada parameter yang dihapus
        self._sync_parameter_value_ids()

        existing_parameter_ids = set(self.parameter_value_ids.mapped("parameter_id.id"))

        git_script_fields = self.has_git_script_relation()

        if git_script_fields:
            for field_name in git_script_fields:
                field_value = getattr(self, field_name, False)
                if field_value:
                    git_script = field_value if hasattr(field_value, "_name") else False
                    if git_script and git_script._name == "git_script":
                        for parameter in git_script.parameter_ids:
                            if parameter.id not in existing_parameter_ids:
                                created_parameter_values += obj_parameter_value.create(
                                    {
                                        "model": self._name,
                                        "res_id": self.id,
                                        "script_id": git_script.id,
                                        "parameter_id": parameter.id,
                                        "value": parameter.default_value or "",
                                    }
                                )
                                existing_parameter_ids.add(parameter.id)

        return created_parameter_values
