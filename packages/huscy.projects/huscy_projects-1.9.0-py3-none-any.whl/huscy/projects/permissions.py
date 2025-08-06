from rest_framework.permissions import BasePermission, SAFE_METHODS
from huscy.projects.models import Membership


class IsProjectCoordinator(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        return Membership.objects.filter(project=view.project, user=request.user,
                                         is_coordinator=True).exists()


class UpdatePrincipalInvestigatorPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, project):
        if bool(request.user and request.user.is_authenticated):
            if request.user.is_superuser:
                return True

            return Membership.objects.filter(project=project, user=request.user,
                                             is_coordinator=True).exists()
        return False


class IsProjectMember(BasePermission):
    def has_permission(self, request, view):
        return Membership.objects.filter(project=view.project, user=request.user).exists()


class ProjectPermission(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, project):
        if request.method in SAFE_METHODS:
            return True

        if request.method == 'DELETE':
            permission = 'projects.delete_project'
        else:
            permission = 'projects.change_project'

        return (request.user.has_perm(permission) or request.user.has_perm(permission, project))


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.method in SAFE_METHODS
