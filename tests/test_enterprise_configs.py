import pathlib
def test_enterprise_configs_present():
    root = pathlib.Path(".")
    assert (root/"Dockerfile").exists()
    assert (root/".github"/"workflows"/"ci_v3.yml").exists()
    assert (root/".pre-commit-config.yaml").exists()
    assert (root/"config"/"logging.conf").exists()