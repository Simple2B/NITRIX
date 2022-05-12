def mocking_get_current_invoice(monkey):
    """Mocking get_current_invoice() and add_item()"""

    class MockInvoice:
        @staticmethod
        def add_item(*argc, **argv):
            return "Could not add item []"

    def monkey_get_current_invoice(*argc, **argv):
        return MockInvoice()

    monkey.setattr(
        "app.scheduler.methods.get_current_invoice", monkey_get_current_invoice
    )
