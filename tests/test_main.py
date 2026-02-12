from email2qa.main import confirm_checkpoint_reset


def test_confirm_checkpoint_reset_force_skips_prompt() -> None:
    result = confirm_checkpoint_reset(True, input_fn=lambda _: "")
    assert result is True


def test_confirm_checkpoint_reset_accepts_exact_token() -> None:
    result = confirm_checkpoint_reset(False, input_fn=lambda _: "RESET")
    assert result is True


def test_confirm_checkpoint_reset_rejects_other_values() -> None:
    result = confirm_checkpoint_reset(False, input_fn=lambda _: "yes")
    assert result is False
