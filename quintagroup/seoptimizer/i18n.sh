#!/bin/sh
i18ndude rebuild-pot --pot "locales/quintagroup.seoptimizer.pot" --create quintagroup.seoptimizer .
i18ndude sync --pot "locales/quintagroup.seoptimizer.pot" \
    "locales/es/LC_MESSAGES/quintagroup.seoptimizer.po" \
    "locales/fr/LC_MESSAGES/quintagroup.seoptimizer.po" \
    "locales/uk/LC_MESSAGES/quintagroup.seoptimizer.po" \
    "locales/de/LC_MESSAGES/quintagroup.seoptimizer.po"
