##############################################################################
#
#    Copyright (C) 2017 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
import logging

from werkzeug.utils import escape

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.model
    def process_wp_confirmed_donation(self, donnation_infos, **kwargs):
        """
        Utility to process the donation done via WordPress.
        :return:
        """
        _logger.info("Processing donation from WordPress %s", str(donnation_infos))
        for key in donnation_infos:
            donnation_infos[key] = escape(donnation_infos[key])

        match_obj = self.env["res.partner.match.wp"]

        # Extract the partner infos
        partner_fields = {  # wp_field : odoo_field
            "email": "email",
            "name": "name",
            "street": "street",
            "zipcode": "zip",
            "city": "city",
            "language": "lang",
            "partner_ref": "ref",
            "child_id": "child_id",
        }
        partner_infos = {"company_id": self.env.user.company_id.id}
        for wp_field, odoo_field in list(partner_fields.items()):
            partner_infos[odoo_field] = donnation_infos[wp_field]

        # Find the matching odoo country
        partner_infos["country_id"] = match_obj.match_country(
            donnation_infos["country"], partner_infos["lang"]
        ).id

        # Find matching partner
        partner = match_obj.match_values_to_partner(partner_infos)

        # Insert the donation details to the database.
        pf_brand = donnation_infos["pf_brand"]
        pf_pm = donnation_infos["pf_pm"]
        if pf_brand != pf_pm:
            payment_mode = "{}_{}".format(pf_brand, pf_pm)
        else:
            payment_mode = pf_brand

        return self.create_from_wordpress(
            partner.id,
            donnation_infos["orderid"],
            donnation_infos["amount"],
            donnation_infos["fund"],
            donnation_infos["child_id"],
            donnation_infos["pf_payid"],
            payment_mode.strip(),
            donnation_infos["utm_source"],
            donnation_infos["utm_medium"],
            donnation_infos["utm_campaign"],
            donnation_infos["time"],
        )

    @api.model
    def create_from_wordpress(
        self,
        partner_id,
        wp_origin,
        amount,
        fund,
        child_code,
        pf_payid,
        payment_mode_name,
        utm_source,
        utm_medium,
        utm_campaign,
        time,
    ):
        """
         Utility for invoice donation creation.
        :param partner_id: odoo partner_id
        :param wp_origin: the fund code in WordPress
        :param amount: amount of donation
        :param fund: the fund code in WordPress
        :param child_code: child local_id
        :param pf_payid: postfinance transaction number
        :param payment_mode_name: the payment_mode identifier from postfinance
        :param utm_source: the utm identifier in WordPress
        :param utm_medium: the utm identifier in WordPress
        :param utm_campaign: the utm identifier in WordPress
        :param time: datetime of donation
        :return: invoice_id
        """
        _logger.info(
            "New donation of CHF %s from WordPress for partner %s and child %s",
            amount,
            partner_id,
            child_code,
        )
        partner = self.env["res.partner"].browse(partner_id)
        if partner.contact_type == "attached":
            if partner.type == "email_alias":
                # In this case we want to link to the main partner
                partner = partner.contact_id
                partner_id = partner.id
            else:
                # We unarchive the partner to make it visible
                partner.write({"active": True, "contact_id": False})
        payment_mode = self.env["account.payment.mode"].search(
            [("name", "=", payment_mode_name), ("active", "=", True)]
        )
        if not payment_mode:
            # Credit Card Journal
            journal = self.env["account.journal"].search(
                [
                    ("code", "=", "CCRED"),
                    ("company_id", "=", partner.company_id.id),
                ],
                limit=1,
            )
            payment_mode.create(
                {
                    "name": payment_mode_name,
                    "payment_method_id": 1,  # Manual inbound
                    "payment_type": "inbound",
                    "bank_account_link": "fixed",
                    "fixed_journal_id": journal.id,
                    "active": True,
                }
            )
        ref = "WP " + wp_origin + " " + str(pf_payid)
        payment_term_id = self.env.ref("account.account_payment_term_immediate").id
        date_invoice = fields.Datetime.from_string(time)
        invoice = self.search(
            [
                ("payment_reference", "=", str(pf_payid)),
                ("partner_id", "=", partner_id),
            ],
            limit=1,
        )
        if invoice:
            # Normally we should only have one invoice with a given PF_reference.
            # In that case we return this invoice without doing anything,
            # because probably another process is dealing with it.
            return invoice.id
        invoice = self.create(
            {
                "partner_id": partner_id,
                "payment_mode_id": payment_mode.id,
                "ref": ref,
                "payment_reference": str(pf_payid),
                "invoice_date": date_invoice.date(),
                # "auto_cancel_date": date_invoice + timedelta(minutes=30),
                "currency_id": 6,  # Always in CHF
                "move_type": "out_invoice",
                "invoice_payment_term_id": payment_term_id,
            }
        )
        invoice.with_delay().pay_wordpress_invoice(
            fund, child_code, wp_origin, amount, utm_source, utm_medium, utm_campaign
        )
        return invoice.id

    def pay_wordpress_invoice(
        self, fund, child_code, wp_origin, amount, utm_source, utm_medium, utm_campaign
    ):
        """Create invoice lines and payment for a WordPress donation.
        :param fund: the fund code in WordPress
        :param child_code: the child reference (local_id)
        :param wp_origin: the fund code in WordPress
        :param amount: the donation amount
        :param utm_source: tracking utm from WordPress
        :param utm_medium: tracking utm from WordPress
        :param utm_campaign: tracking utm from WordPress
        :return: True
        """
        self.ensure_one()
        product = self.env["product.product"]
        if fund:
            product = product.search([("default_code", "=", fund)], limit=1)
        analytic_id = (
            self.env["account.analytic.default"].account_get(product.id).analytic_id.id
        )
        analytic_tag_ids = (
            self.env["account.analytic.default"]
            .account_get(product.id)
            .analytic_tag_ids.ids
        )
        gift_account = self.env["account.account"].search([("code", "=", "6003")])
        sponsorship = self.env["recurring.contract"]
        if child_code:
            sponsorship = sponsorship.search(
                [
                    "|",
                    ("partner_id", "=", self.partner_id.id),
                    ("correspondent_id", "=", self.partner_id.id),
                    ("child_code", "=", child_code),
                ],
                order="id desc",
                limit=1,
            )
        internet_id = self.env.ref("utm.utm_medium_website").id
        inv_line_ids = (
            self.env["account.move.line"]
            .with_context(
                check_move_validity=False,
            )
            .create(
                {
                    "move_id": self.id,
                    "product_id": product.id,
                    "account_id": product.property_account_income_id.id
                    or gift_account.id,
                    "contract_id": sponsorship.id,
                    "name": product.name or "Online donation for " + wp_origin,
                    "quantity": 1,
                    "price_unit": float(amount),
                    "price_subtotal": float(amount),
                    "analytic_account_id": analytic_id,
                    "analytic_tag_ids": [(6, 0, analytic_tag_ids)],
                }
            )
        )
        self.invoice_line_ids = inv_line_ids
        self.source_id = (
            self.env["utm.source"].search([("name", "=", utm_source)], limit=1).id
        )
        self.medium_id = (
            self.env["utm.medium"].search([("name", "=", utm_medium)], limit=1).id
            or internet_id
        )
        self.campaign_id = (
            self.env["utm.campaign"].search([("name", "=", utm_campaign)], limit=1).id
        )
        if not self.partner_id.legal_agreement_date:
            self.partner_id.legal_agreement_date = self.invoice_date
        self.action_post()
        payment_vals = {
            "journal_id": self.env["account.journal"]
            .search(
                [
                    ("name", "=", "Web"),
                    ("company_id", "=", self.company_id.id),
                ]
            )
            .id,
            "payment_method_id": self.env["account.payment.method"]
            .search([("code", "=", "sepa_direct_debit")])
            .id,
            "date": self.date,
            "payment_reference": self.payment_reference,
            "payment_type": "inbound",
            "amount": self.amount_total,
            "currency_id": self.currency_id.id,
            "partner_id": self.partner_id.id,
            "partner_type": "customer",
        }
        account_payment = self.env["account.payment"].create(payment_vals)
        account_payment.action_post()
        for account in account_payment.line_ids.account_id:
            (account_payment.line_ids + self.line_ids).filtered_domain(
                [("account_id", "=", account.id), ("reconciled", "=", False)]
            ).reconcile()

        return True
