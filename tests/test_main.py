from email2qa.main import build_parser, confirm_checkpoint_reset


def test_confirm_checkpoint_reset_force_skips_prompt() -> None:
    result = confirm_checkpoint_reset(True, input_fn=lambda _: "")
    assert result is True


def test_confirm_checkpoint_reset_accepts_exact_token() -> None:
    result = confirm_checkpoint_reset(False, input_fn=lambda _: "RESET")
    assert result is True


def test_confirm_checkpoint_reset_rejects_other_values() -> None:
    result = confirm_checkpoint_reset(False, input_fn=lambda _: "yes")
    assert result is False


def test_parser_verbose_defaults_to_false() -> None:
    args = build_parser().parse_args([])
    assert args.verbose is False


def test_parser_verbose_can_be_enabled() -> None:
    args = build_parser().parse_args(["--verbose"])
    assert args.verbose is True
