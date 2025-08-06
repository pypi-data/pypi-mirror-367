import pytest
from model_bakery import baker
from pytest_bdd import given, parsers, scenarios, then, when

from django.contrib.auth.models import Permission
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from huscy.projects import services

pytestmark = pytest.mark.django_db

scenarios('viewsets')


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_user(user):
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def principal_investigator(django_user_model):
    return baker.make(django_user_model)


@given('I am admin user', target_fixture='client')
def admin_client(admin_user, api_client):
    api_client.login(username=admin_user.username, password='password')
    return api_client


@given('I am staff user', target_fixture='client')
def staff_user_client(staff_user, api_client):
    api_client.login(username=staff_user.username, password='password')
    return api_client


@given('I am normal user', target_fixture='client')
def user_client(user, api_client):
    api_client.login(username=user.username, password='password')
    return api_client


@given('I am anonymous user', target_fixture='client')
def anonymous_client(api_client):
    return api_client


@given(parsers.parse('I have {codename} permission'), target_fixture='codename')
def assign_permission(user, codename):
    permission = Permission.objects.get(codename=codename)
    user.user_permissions.add(permission)


@given('one project with local id 123')
def project_with_local_id_123(research_unit):
    return baker.make('projects.Project', research_unit=research_unit, local_id=123)


@given('one project member as coordinator', target_fixture='coordinator')
def coordinator(django_user_model, project):
    user = baker.make(django_user_model)
    services.create_membership(project, user, is_coordinator=True)
    return user


@given('I am project coordinator')
def coordinator_membership(user, project):
    services.create_membership(project, user, is_coordinator=True)


@given('I am project member with write permission')
def membership_with_write_permission(user, project):
    services.create_membership(project, user, has_write_permission=True)


@given('I am project member with read permission')
def membership_with_read_permission(user, project):
    services.create_membership(project, user)


@when('I try to create a membership', target_fixture='request_result')
def create_membership(django_user_model, client, project):
    user = baker.make(django_user_model)
    return client.post(
        reverse('membership-list', kwargs=dict(project_pk=project.pk)),
        data=dict(user=user.id, is_coordinator=False)
    )


@when('I try to create a project', target_fixture='request_result')
def create_project(client, research_unit, principal_investigator):
    data = dict(
        principal_investigator=principal_investigator.pk,
        research_unit=research_unit.pk,
        title='title',
    )
    return client.post(reverse('project-list'), data=data)


@when('I try to create a project with invalid local id', target_fixture='request_result')
def create_project_with_invalid_local_id(client, research_unit, principal_investigator):
    data = dict(
        local_id='string',
        principal_investigator=principal_investigator.pk,
        research_unit=research_unit.pk,
        title='title',
    )
    return client.post(reverse('project-list'), data=data)


@when('I try to create a project with local id 123', target_fixture='request_result')
def create_project_with_local_id_123(client, research_unit, principal_investigator):
    data = dict(
        local_id=123,
        principal_investigator=principal_investigator.pk,
        research_unit=research_unit.pk,
        title='title',
    )
    return client.post(reverse('project-list'), data=data)


@when('I try to create a research unit', target_fixture='request_result')
def create_research_unit(client, principal_investigator):
    return client.post(
        reverse('researchunit-list'),
        data=dict(name='research unit name', principal_investigator=principal_investigator.pk)
    )


@when('I try to delete a membership', target_fixture='request_result')
def delete_membership(client, project, membership):
    return client.delete(
        reverse('membership-detail', kwargs=dict(project_pk=project.pk, pk=membership.id))
    )


@when('I try to delete a project', target_fixture='request_result')
def delete_project(client, project):
    return client.delete(reverse('project-detail', kwargs=dict(pk=project.pk)))


@when('I try to delete a research unit', target_fixture='request_result')
def delete_research_unit(client, research_unit):
    return client.delete(reverse('researchunit-detail', kwargs=dict(pk=research_unit.pk)))


@when('I try to list memberships', target_fixture='request_result')
def list_memberships(client, project):
    return client.get(reverse('membership-list', kwargs=dict(project_pk=project.pk)))


@when('I try to list projects', target_fixture='request_result')
def list_projects(client, project):
    return client.get(reverse('project-list'))


@when('I try to list research units', target_fixture='request_result')
def list_research_units(client):
    return client.get(reverse('researchunit-list'))


@when('I try to partial update the project description', target_fixture='request_result')
def partial_update_project_description(client, project):
    return client.patch(
        reverse('project-detail', kwargs=dict(pk=project.pk)),
        data=dict(description='new description')
    )


@when('I try to partial update the project local id', target_fixture='request_result')
def partial_update_project_local_id(client, project):
    return client.patch(
        reverse('project-detail', kwargs=dict(pk=project.pk)),
        data=dict(local_id=555)
    )


@when('I try to partial update the project research unit', target_fixture='request_result')
def partial_update_project_research_unit(client, project):
    research_unit = baker.make('projects.ResearchUnit')
    return client.patch(
        reverse('project-detail', kwargs=dict(pk=project.pk)),
        data=dict(research_unit=research_unit.pk)
    )


@when('I try to partial update the project title', target_fixture='request_result')
def partial_update_project_title(client, project):
    return client.patch(
        reverse('project-detail', kwargs=dict(pk=project.pk)),
        data=dict(title='new title')
    )


@when('I try to partial update a research unit', target_fixture='request_result')
def partial_update_research_unit(client, research_unit):
    return client.patch(
        reverse('researchunit-detail', kwargs=dict(pk=research_unit.pk)),
        data=dict(name='new research unit name')
    )


@when('I try to retrieve a membership', target_fixture='request_result')
def retrieve_membership(client, project, membership):
    return client.get(
        reverse('membership-detail', kwargs=dict(project_pk=project.pk, pk=membership.pk))
    )


@when('I try to retrieve a project', target_fixture='request_result')
def retrieve_project(client, project):
    return client.get(reverse('project-detail', kwargs=dict(pk=project.pk)))


@when('I try to retrieve a research unit', target_fixture='request_result')
def retrieve_research_unit(client, research_unit):
    return client.get(reverse('researchunit-detail', kwargs=dict(pk=research_unit.pk)))


@when('I try to set the principal investigator', target_fixture='request_result')
def set_principal_investigator(client, project, coordinator):
    return client.put(
        reverse('project-principalinvestigator', kwargs=dict(pk=project.pk)),
        data=dict(principal_investigator=coordinator.pk)
    )


@when('I try to set normal team member as principal investigator', target_fixture='request_result')
def set_normal_team_member_as_principal_investigator(django_user_model, client, project):
    user = baker.make(django_user_model)
    services.create_membership(project, user, has_write_permission=True)

    return client.put(
        reverse('project-principalinvestigator', kwargs=dict(pk=project.pk)),
        data=dict(principal_investigator=user.pk)
    )


@when('I try to set any user as principal investigator', target_fixture='request_result')
def set_any_user_as_principal_investigator(django_user_model, client, project):
    user = baker.make(django_user_model)

    return client.put(
        reverse('project-principalinvestigator', kwargs=dict(pk=project.pk)),
        data=dict(principal_investigator=user.pk)
    )


@when('I try to update a membership', target_fixture='request_result')
def update_membership(client, project, membership):
    return client.put(
        reverse('membership-detail', kwargs=dict(project_pk=project.pk, pk=membership.id)),
        data=dict(
            user=membership.user.id,
            is_coordinator=False,
            has_write_permission=True,
        ),
    )


@when('I try to update the project', target_fixture='request_result')
def update_project(client, project):
    return client.put(
        reverse('project-detail', kwargs=dict(pk=project.pk)),
        data=dict(description='new description', local_id=555, title='new title')
    )


@when('I try to update the project local id to 123', target_fixture='request_result')
def update_project_local_id_to_123(client, project):
    return client.put(
        reverse('project-detail', kwargs=dict(pk=project.pk)),
        data=dict(description='new description', local_id=123, title='new title')
    )


@when('I try to update a research unit', target_fixture='request_result')
def update_research_unit(client, research_unit):
    return client.put(
        reverse('researchunit-detail', kwargs=dict(pk=research_unit.pk)),
        data=dict(
            name='new research unit name',
            code='RU',
            principal_investigator=research_unit.principal_investigator.pk
        )
    )


@then(parsers.parse('I get status code {status_code:d}'))
def assert_status_code(request_result, status_code):
    assert request_result.status_code == status_code, request_result.content


@then('I get error message that research unit and local id must make a unique set')
def error_research_unit_and_local_id_must_make_a_unique_set(request_result):
    assert request_result.json() == {
        'non_field_errors': ['The fields local_id, research_unit must make a unique set.'],
    }


@then('I get error message that local id must be a valid integer')
def error_valid_integer_is_required(request_result):
    assert request_result.json() == {
        'local_id': ['A valid integer is required.'],
    }


@then('I get error message that local id already exists')
def error_local_id_already_exists(request_result):
    assert request_result.json() == {
        'local_id': ['Local ID already exists.'],
    }


@then('I get error message that only project coordinators can become principal investigators')
def error_only_project_coordinators_can_become_principal_investigators(request_result):
    assert request_result.json() == {
        'detail': 'Only project members who are coordinators can become principal investigators.'
    }
