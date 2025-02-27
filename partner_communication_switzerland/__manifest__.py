##############################################################################
#
#       ______ Releasing children from poverty      _
#      / ____/___  ____ ___  ____  ____ ___________(_)___  ____
#     / /   / __ \/ __ `__ \/ __ \/ __ `/ ___/ ___/ / __ \/ __ \
#    / /___/ /_/ / / / / / / /_/ / /_/ (__  |__  ) / /_/ / / / /
#    \____/\____/_/ /_/ /_/ .___/\__,_/____/____/_/\____/_/ /_/
#                        /_/
#                            in Jesus' name
#
#    Copyright (C) 2016-2021 Compassion CH (http://www.compassion.ch)
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# pylint: disable=C8101
{
    "name": "Compassion CH Partner Communications",
    "version": "14.0.1.1.0",
    "category": "Other",
    "author": "Compassion CH",
    "license": "AGPL-3",
    "website": "https://github.com/CompassionCH/compassion-switzerland",
    "depends": [
        "hr",
        "website_form",
        "report_compassion",
        "partner_communication_compassion",
        "label",
        "child_sync_wp",
        "sms_939",  # compassion-modules
        "auth_signup",  # source/addons
        "recurring_contract",  # compassion-accounting
        "survival_sponsorship_compassion",
        "link_tracker",
    ],
    "external_dependencies": {
        "python": ["wand", "bs4", "pdf2image", "babel", "PyPDF2", "pyquery"]
    },
    "data": [
        "security/ir.model.access.csv",
        "security/access_rules.xml",
        "data/activity_data.xml",
        "data/other_emails.xml",
        "data/form_data.xml",
        "data/sponsorship_planned_emails.xml",
        "data/tax_receipt_emails.xml",
        "data/manual_emails.xml",
        "data/communication_config.xml",
        "data/sponsorship_communications_cron.xml",
        "data/ir.advanced.translation.csv",
        "data/queue_job.xml",
        "data/sponsorship_action_rules.xml",
        "report/onboarding_photo_by_post.xml",
        "data/onboarding_process.xml",
        "data/onboarding_survey.xml",
        "data/onboarding_new_donors_process.xml",
        "data/onboarding_wrpr.xml",
        "data/wrpr_feedback_survey.xml",
        "data/wrpr_onboarding_survey.xml",
        "data/wrpr_journey.xml",
        "data/end_reasons.xml",
        "report/csp_picture.xml",
        "views/assets.xml",
        "views/communication_job_view.xml",
        "views/download_child_pictures_view.xml",
        "views/end_contract_wizard_view.xml",
        "views/disaster_alert_view.xml",
        "views/partner_compassion_view.xml",
        "views/contract_view.xml",
        "views/correspondence_view.xml",
        "views/staff_notifications_settings_view.xml",
        "views/res_partner_zoom_session.xml",
        "views/field_office_view.xml",
        "views/communication_test_case_view.xml",
        "views/notification_settings_view.xml",
        "views/onboarding_settings_view.xml",
        "views/res_partner_create_portal_wizard.xml",
        "views/link_tracker.xml",
        "templates/zoom_registration_form.xml",
        "templates/onboarding_unsubscribe.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
