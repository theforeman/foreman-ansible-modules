Converting strings to Candlepin labels
======================================

This filter will convert arbitrary strings to Candlepin labels::

    {{ 'Default Organization' | cp_label }}
    # => 'Default_Organization'
