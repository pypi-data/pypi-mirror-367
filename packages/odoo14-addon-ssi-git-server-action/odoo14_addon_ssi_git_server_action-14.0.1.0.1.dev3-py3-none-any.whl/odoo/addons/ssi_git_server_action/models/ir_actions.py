# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class IrActionsServer(models.Model):
    _name = "ir.actions.server"
    _inherit = [
        "ir.actions.server",
        "mixin.git_script.parameter_value",
    ]
    _parameter_value_create_page = True
    _parameter_value_page_xpath = "//page[@name='script']"

    state = fields.Selection(
        selection_add=[("run_git_script", "Run Code On Git Repo")],
        ondelete={"run_git_script": "set default"},
    )
    repo_id = fields.Many2one(
        string="Repository",
        comodel_name="git_repo",
        required=False,
        copy=False,
    )
    branch_id = fields.Many2one(
        string="Branch",
        comodel_name="git_branch",
        domain="[('repo_id', '=', repo_id)]",
        required=False,
        copy=False,
    )
    script_id = fields.Many2one(
        string="Script",
        comodel_name="git_script",
        domain="[('branch_id', '=', branch_id)]",
        required=False,
        copy=False,
    )

    def run(self):
        res = super().run()
        for action in self:
            if action.state == "run_git_script" and action.script_id:
                model = self.env[action.model_name]
                active_id = self._context.get("active_id")
                active_ids = self._context.get("active_ids", [])
                context_env = {
                    "self": self,
                    "model": model,
                    "record": model.browse(active_id),
                    "records": model.browse(active_ids),
                    "context": self._context,
                }
                for param in action.parameter_value_ids:
                    context_env[param.parameter_id.name] = param.parse_value()
                res = action.script_id._run(context_env)
        return res
