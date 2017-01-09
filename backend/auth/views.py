"""This module contains views related to authentication."""

import json

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class SessionLoginView(View):
    """This set of views allows users to log in and out using HTTP sessions."""

    def delete(self, request, *args, **kwargs):
        """
        Log the user out.

        :param request: request that was made
        :return: 200 OK or 401 if unauthorized
        """
        if not request.user.is_authenticated:
            return JsonResponse({"error": "unauthorized"}, status=401)

        logout(request)
        return JsonResponse({})

    @method_decorator(sensitive_post_parameters("password"))
    @method_decorator(csrf_protect)
    @never_cache
    def post(self, request, *args, **kwargs):
        """
        Log a user in.

        :param request: request that was made
        :return: "", 200 on success, else the error that occurred with status 401
        """
        form = AuthenticationForm(request, data=json.loads(request.body.decode("utf8")))

        if form.is_valid():
            if not form.get_user().is_staff:
                return JsonResponse({"global": "Only administrators are allowed to login here."}, status=403)
            login(request, form.get_user())

            return JsonResponse({})

        return JsonResponse({"global": "Username not recognized or password incorrect"}, status=401)


@csrf_exempt
@require_http_methods(["POST"])
@never_cache
def reset_password(request):
    form = PasswordResetForm(json.loads(request.body.decode("utf-8")))
    if form.is_valid():
        opts = {
            "use_https": request.is_secure(),
            "token_generator": default_token_generator,
            "email_template_name": "registration/password_reset_email.html",
            "subject_template_name": "registration/password_reset_subject.txt",
            "request": request,
        }
        form.save(**opts)
        return JsonResponse({})
    return JsonResponse({"email": "Not found or not valid"}, status=400)
