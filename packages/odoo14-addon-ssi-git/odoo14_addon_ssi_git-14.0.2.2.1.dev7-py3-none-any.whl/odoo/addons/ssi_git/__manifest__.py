# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "Git",
    "version": "14.0.2.2.0",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "ssi_master_data_mixin",
        "ssi_decorator",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/sequence_template_data.xml",
        "menu.xml",
        "templates/mixin_git_script_parameter_value_templates.xml",
        "views/res_config_settings_views.xml",
        "views/git_repo_type_views.xml",
        "views/git_user_views.xml",
        "views/git_repo_views.xml",
        "views/git_branch_views.xml",
        "views/git_script_views.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["pytz", "GitPython"]},
}
