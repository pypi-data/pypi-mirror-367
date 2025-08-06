import pytest

from django.contrib.admin.sites import AdminSite

from huscy.projects.admin import MembershipAdmin
from huscy.projects.models import Membership

pytestmark = pytest.mark.django_db


@pytest.fixture
def membership_admin():
    return MembershipAdmin(model=Membership, admin_site=AdminSite())


def test_has_add_permission(membership_admin):
    assert membership_admin.has_add_permission(request=None) is False


def test_has_change_permission(membership_admin):
    assert membership_admin.has_change_permission(request=None) is False


def test_list_display_project(membership_admin, project, membership):
    expected_result = f'{project.id} ({project.local_id_name} {project.title})'

    assert membership_admin._project(membership) == expected_result
