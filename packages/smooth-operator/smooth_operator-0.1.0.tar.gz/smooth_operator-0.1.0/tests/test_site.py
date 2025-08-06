import pytest
from smooth_operator.core.site import Site
from smooth_operator.channels.terminus import TerminusChannel


# Mock the TerminusChannel to avoid actual API calls during tests
class MockTerminusChannel:
    def execute(self, command, **kwargs):
        return {
            "stdout": "Mocked output",
            "stderr": "",
            "returncode": 0,
            "success": True
        }

    def clone_content(self, source_site, source_env, target_site, target_env, content_type="database"):
        return {
            "stdout": f"Cloned {content_type} from {source_site}.{source_env} to {target_site}.{target_env}",
            "stderr": "",
            "returncode": 0,
            "success": True
        }


# Replace actual TerminusChannel with mock for testing
pytest.MonkeyPatch().setattr("smooth_operator.channels.terminus.TerminusChannel", MockTerminusChannel)


def test_site_initialization():
    """Test that Site objects are properly initialized."""
    site = Site(
        site_id="cwb-shine-template2",
        name="SHiNE Template 2",
        environments=["dev", "test", "live"],
        tags=["drupal", "test"]
    )

    assert site.site_id == "cwb-shine-template2"
    assert site.name == "SHiNE Template 2"
    assert site.environments == ["dev", "test", "live"]
    assert site.tags == ["drupal", "test"]


def test_site_clone():
    """Test the site clone operation."""
    source_site = Site(
        site_id="cwb-shine-template2",
        name="SHiNE Template 2",
        environments=["dev", "test", "live"]
    )

    target_site = Site(
        site_id="cwb-mainlined10-upgrade-test-3",
        name="MainlineD10 upgrade test",
        environments=["dev", "test", "live"]
    )

    result = source_site.clone(
        source_env="live",
        target_site=target_site,
        target_env="dev",
        clone_database=True,
        clone_files=True
    )

    assert result["success"] is True
    assert "database" in result
    assert "files" in result