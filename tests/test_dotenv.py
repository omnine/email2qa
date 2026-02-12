import importlib

from email2qa import config as config_mod


def test_dotenv_loaded_from_cwd(tmp_path, monkeypatch):
    # Ensure environment is clean for the keys we use
    monkeypatch.delenv("EMAIL2QA_EXCHANGE_SERVER", raising=False)
    monkeypatch.delenv("EMAIL2QA_EXCHANGE_EMAIL", raising=False)
    monkeypatch.delenv("EMAIL2QA_EXCHANGE_PASSWORD", raising=False)

    # Create a .env in a temporary directory and change cwd
    env = tmp_path / ".env"
    env.write_text(
        "EMAIL2QA_EXCHANGE_SERVER=mail.example.com\n"
        "EMAIL2QA_EXCHANGE_EMAIL=alice@example.com\n"
        "EMAIL2QA_EXCHANGE_PASSWORD=supersecret\n"
    )
    monkeypatch.chdir(tmp_path)

    # Reload the config module so it re-reads the .env via load_dotenv at import-time
    importlib.reload(config_mod)

    cfg = config_mod.load_config()
    assert cfg.exchange_server == "mail.example.com"
    assert cfg.exchange_email == "alice@example.com"
    assert cfg.exchange_password == "supersecret"
