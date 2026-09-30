from pathlib import Path

def test_competition_config_exists():
    assert Path("configs/competition.yaml").exists()
