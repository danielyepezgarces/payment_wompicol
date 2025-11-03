from . import controllers
from . import models


def post_init_hook(env):
    """Post-init hook to ensure payment provider is properly set up."""
    # In Odoo 19, journal creation is handled differently
    # This hook can be used for any custom initialization if needed
    pass
