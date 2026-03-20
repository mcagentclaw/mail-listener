from __future__ import annotations

import mail_listener


def test_version_present() -> None:
    assert mail_listener.__version__ == "0.1.0"
