import logging
import math
import lxml
from werkzeug import urls

from odoo.addons.payment.tests.common import PaymentCommon
from odoo.tests import tagged


_logger = logging.getLogger(__name__)
class WompicolCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wompicol = cls.env.ref('payment_wompicol.payment_provider_wompicol')
        cls.wompicol.write({
            'wompicol_private_key': 'dummy',
            'wompicol_public_key': 'dummy',
            'wompicol_test_private_key': 'dummy',
            'wompicol_test_public_key': 'dummy',
            'state': 'test',
        })
        cls.currency_col = cls.env.ref('base.COP')
        cls.amount = 44900.23


@tagged('post_install', '-at_install', 'external', '-standard', 'wompicol')
class WompicolForm(WompicolCommon):

    def test_10_wompicol_form_render(self):
        '''Check the form is rendering correctly'''
        self.assertEqual(self.wompicol.state, 'test', 'test without test environment')

        # ----------------------------------------
        # Test: button direct rendering
        # ----------------------------------------

        tx = self.env['payment.transaction'].create({
            'reference': 'wompi_test_transaction',
            'amount': self.amount,
            'currency_id': self.currency_col.id,
            'provider_id': self.wompicol.id,
            'partner_id': self.partner.id
        })

        # Get rendering values
        rendering_values = tx._get_processing_values()

        base_url = self.env[
                'ir.config_parameter'
                ].sudo().get_param('web.base.url')

        # check form values
        self.assertEqual(
                rendering_values.get('publickey'),
                self.wompicol.wompicol_test_public_key,
                'wompicol: wrong form render publicKey')
        
        # Proper amount in cents only 00 at the end
        amount_cents = rendering_values.get('amountcents')
        self.assertTrue(str(amount_cents)[-2:] == '00',
                'wompicol: wrong amount %s, only 00 allowed as last two digits.'
                % amount_cents)
        
        # Proper amount in cents
        self.assertEqual(
                amount_cents,
                math.ceil(self.amount) * 100,
                'wompicol: wrong amount of cents rendered')
        
        # Proper currency value
        self.assertEqual(
                rendering_values.get('currency'),
                'COP',
                'wompicol: Wrong currency only COP is supported')

    def test_20_wompicol_form_management(self):
        self.assertEqual(self.wompicol.state, 'test', 'wompicol: test without test environment')

        # typical data posted by wompi after client has successfully paid
        wompi_event_post = {
              "event": "transaction.updated",
              "data": {
                "transaction": {
                    "id": "01-1532941443-49201",
                    "amount_in_cents": 4490100,
                    "reference": "wompi_test_transaction",
                    "customer_email": "juan.perez@gmail.com",
                    "currency": "COP",
                    "payment_method_type": "NEQUI",
                    "redirect_url": "https://mitienda.com.co/pagos/redireccion",
                    "status": "APPROVED",
                    "shipping_address": None,
                    "payment_link_id": None,
                    "payment_source_id": None
                  }
              },
              "sent_at":  "2018-07-20T16:45:05.000Z",
              "noconfirm": 1, # Avoids calling wompi api with false id
            }

        # create tx
        tx = self.env['payment.transaction'].create({
            'reference': 'wompi_test_transaction',
            'amount': self.amount,
            'currency_id': self.currency_col.id,
            'provider_id': self.wompicol.id,
            'partner_id': self.partner.id,
            'partner_name': 'Norbert Buyer',
            'partner_country_id': self.env.ref('base.fr').id,
        })

        # validate transaction
        tx._handle_notification_data('wompicol', wompi_event_post)
        
        # Check the transaction is set to done when APPROVED is received.
        self.assertEqual(
                tx.state,
                'done',
                'wompicol: wrong state after receiving a valid approved notification')
        # Check if the created provider reference is equal to what wompi sent
        self.assertEqual(
                tx.provider_reference,
                '01-1532941443-49201',
                'wompicol: wrong txn_id after receiving a valid event notification')

        # update transaction
        tx.write({
            'state': 'draft',
            'provider_reference': False})

        # Now test with a pending
        wompi_event_post["data"]["transaction"]["status"] = 'PENDING'

        # validate transaction now with new state
        tx._handle_notification_data('wompicol', wompi_event_post)

        # Check the transaction is set to pending when PENDING is received.
        self.assertEqual(
                tx.state,
                'pending',
                'wompicol: wrong state after receiving a valid pending notification')
        # Check if the created provider reference is equal to what wompi sent
        self.assertEqual(
                tx.provider_reference,
                '01-1532941443-49201',
                'wompicol: wrong txn_id after receiving a valid event notification')
