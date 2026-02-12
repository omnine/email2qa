from email2qa.preprocess import preprocess_email_body


def test_preprocess_removes_disclaimer_and_quote() -> None:
    body = """
    <p>Hello team,</p>
    <p>Please restart the service and clear cache.</p>
    <p>Thanks,</p>
    <p>Agent</p>
    -----Original Message-----
    From: customer@example.com
    This email and any attachments are confidential
    """

    result = preprocess_email_body(body)

    assert "Original Message" not in result.cleaned_text
    assert "confidential" not in result.cleaned_text.lower()
    assert "restart the service" in result.cleaned_text.lower()


def test_preprocess_flags_short_content() -> None:
    result = preprocess_email_body("ok thanks")
    assert result.has_enough_content is False
