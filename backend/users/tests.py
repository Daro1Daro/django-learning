import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from ninja.errors import HttpError

from .models import User
from .api import register, UserInput
from .exceptions import InvalidActivationToken
from .auth_token import AuthToken
from . import commands
from . import queries


def create_user(email: str, password: str, is_active: bool = False):
    return User.objects.create(email=email, password=password, is_active=is_active)


@patch("users.api.create_user")
@patch("users.api.default_token_generator.make_token")
@patch("users.api.reverse")
@patch("users.api.send_mail")
class RegisterViewTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.URL = reverse("api-1:register")

    def test_register_sends_activation_email_on_success(
        self,
        mock_send_mail: MagicMock,
        mock_reverse: MagicMock,
        mock_make_token: MagicMock,
        mock_create_user: MagicMock,
    ):
        """
        Calls create_user, make_token, reverse, build_absolute_uri and send_mail with correct parameters in positive case scenario.
        """
        EMAIL = "test@test.com"
        PASSWORD = "pass"

        CREATE_USER_RETURN_VALUE: User = User(pk=1, email=EMAIL, password=PASSWORD)
        MAKE_TOKEN_RETURN_VALUE = "token"
        REVERSE_RETURN_VALUE = "activation-url"
        BUILD_ABSOLUTE_URI_RETURN_VALUE = "http://activation-url?token=123"

        payload = UserInput.construct(email=EMAIL, password=PASSWORD)
        request = self.request_factory.post(
            path=self.URL,
            content_type="application/json",
        )

        mock_create_user.return_value = CREATE_USER_RETURN_VALUE
        mock_make_token.return_value = MAKE_TOKEN_RETURN_VALUE
        mock_reverse.return_value = REVERSE_RETURN_VALUE
        request.build_absolute_uri = MagicMock(
            return_value=BUILD_ABSOLUTE_URI_RETURN_VALUE
        )

        response = register(request=request, payload=payload)

        self.assertEqual(response["detail"], "User registered successfully!")

        mock_create_user.assert_called_once_with(email=EMAIL, password=PASSWORD)
        mock_make_token.assert_called_once_with(CREATE_USER_RETURN_VALUE)
        mock_reverse.assert_called_once_with(
            "api-1:activate",
            args=[CREATE_USER_RETURN_VALUE.pk, MAKE_TOKEN_RETURN_VALUE],
        )
        request.build_absolute_uri.assert_called_once_with(REVERSE_RETURN_VALUE)

        mock_send_mail.assert_called_once_with(
            subject="Activate your account",
            message=f"Click the link to activate your account: {BUILD_ABSOLUTE_URI_RETURN_VALUE}",
            from_email="noreply@test.com",
            recipient_list=[CREATE_USER_RETURN_VALUE.email],
        )

    def test_user_creation_failure(
        self,
        mock_send_mail: MagicMock,
        mock_reverse: MagicMock,
        mock_make_token: MagicMock,
        mock_create_user: MagicMock,
    ):
        """
        If user creation fails, 400 is returned.
        """

        mock_create_user.side_effect = ValueError

        response = self.client.post(
            path=self.URL,
            data={
                "email": "",
                "password": "",
            },
            content_type="application/json",
        )

        content = json.loads(response.text)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content["detail"], "User creation failed.")

        mock_create_user.assert_called_once_with(email="", password="")
        mock_reverse.assert_not_called()
        mock_make_token.assert_not_called()
        mock_send_mail.assert_not_called()


@patch("users.api.get_user_by_id")
@patch("users.api.activate_user_account")
class ActivateAccountViewTests(TestCase):
    def setUp(self):
        self.URL_NAME = "api-1:activate"
        self.USER_ID = 1
        self.TOKEN = "token"

    def test_successfully_activates_user_account(
        self,
        mock_activate_user_account: MagicMock,
        mock_get_user_by_id: MagicMock,
    ):
        """
        Calls get_user_by_id, activate_user_account and returns correct message.
        """
        GET_USER_BY_ID_RETURN_VALUE: User = User(
            pk=self.USER_ID, email="test@test.com", password="pass", is_active=False
        )

        mock_get_user_by_id.return_value = GET_USER_BY_ID_RETURN_VALUE

        response = self.client.get(
            path=reverse(self.URL_NAME, args=[self.USER_ID, self.TOKEN])
        )

        content = json.loads(response.text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["detail"], "Account activated successfully!")

        mock_get_user_by_id.assert_called_once_with(uid=self.USER_ID)
        mock_activate_user_account.assert_called_once_with(
            user=GET_USER_BY_ID_RETURN_VALUE, token=self.TOKEN
        )

    def test_response_when_user_account_is_already_active(
        self,
        mock_activate_user_account: MagicMock,
        mock_get_user_by_id: MagicMock,
    ):
        """
        Calls get_user_by_id and returns correct message.
        """
        GET_USER_BY_ID_RETURN_VALUE: User = User(
            pk=self.USER_ID, email="test@test.com", password="pass", is_active=True
        )

        mock_get_user_by_id.return_value = GET_USER_BY_ID_RETURN_VALUE

        response = self.client.get(
            path=reverse(self.URL_NAME, args=[self.USER_ID, self.TOKEN])
        )

        GET_USER_BY_ID_RETURN_VALUE: User = User(
            pk=self.USER_ID, email="test@test.com", password="pass"
        )

        content = json.loads(response.text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["detail"], "Account is already active.")

        mock_get_user_by_id.assert_called_once_with(uid=self.USER_ID)
        mock_activate_user_account.assert_not_called()

    def test_response_when_token_is_invalid(
        self,
        mock_activate_user_account: MagicMock,
        mock_get_user_by_id: MagicMock,
    ):
        """
        Calls get_user_by_id, activate_user_account and returns correct message with 401 code.
        """
        GET_USER_BY_ID_RETURN_VALUE: User = User(
            pk=self.USER_ID, email="test@test.com", password="pass"
        )

        mock_get_user_by_id.return_value = GET_USER_BY_ID_RETURN_VALUE
        mock_activate_user_account.side_effect = InvalidActivationToken

        response = self.client.get(
            path=reverse(self.URL_NAME, args=[self.USER_ID, self.TOKEN])
        )

        content = json.loads(response.text)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(content["detail"], "Invalid or expired token.")

        mock_get_user_by_id.assert_called_once_with(uid=self.USER_ID)
        mock_activate_user_account.assert_called_once_with(
            user=GET_USER_BY_ID_RETURN_VALUE, token=self.TOKEN
        )


@patch("users.api.AuthToken.create_tokens")
@patch("users.api.authenticate")
class LoginViewTests(TestCase):
    def setUp(self):
        self.USER_ID = 1
        self.EMAIL = "test@test.com"
        self.PASSWORD = "password"
        self.REQUEST_ARGS = {
            "path": reverse("api-1:login"),
            "data": {
                "email": self.EMAIL,
                "password": self.PASSWORD,
            },
            "content_type": "application/json",
        }

    def test_successful_login_returns_expected_response(
        self,
        mock_authenticate: MagicMock,
        mock_create_tokens: MagicMock,
    ):
        """
        Calls authenticate and AuthToken.create_token and return access and refresh token.
        """
        ACCESS_TOKEN = "access_token"
        REFRESH_TOKEN = "refresh_token"

        AUTHENTICATE_RETURN_VALUE: User = User(
            pk=self.USER_ID, email=self.EMAIL, password=self.PASSWORD, is_active=True
        )
        CREATE_TOKENS_RETURN_VALUE = {
            "access_token": ACCESS_TOKEN,
            "refresh_token": REFRESH_TOKEN,
        }

        mock_authenticate.return_value = AUTHENTICATE_RETURN_VALUE
        mock_create_tokens.return_value = CREATE_TOKENS_RETURN_VALUE

        response = self.client.post(**self.REQUEST_ARGS)

        self.assertEqual(mock_authenticate.call_args[1]["email"], self.EMAIL)
        self.assertEqual(mock_authenticate.call_args[1]["password"], self.PASSWORD)

        content = json.loads(response.text)
        token_cookie = response.cookies["refresh_token"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, {"access_token": ACCESS_TOKEN, "email": self.EMAIL})
        self.assertEqual(token_cookie.value, REFRESH_TOKEN)
        self.assertTrue(token_cookie["httponly"])
        self.assertEqual(token_cookie["samesite"].lower(), "lax")
        self.assertTrue(token_cookie["secure"])

    def test_login_failure_on_authentication(
        self,
        mock_authenticate: MagicMock,
        mock_create_tokens: MagicMock,
    ):
        """
        Returns 401 and correct message on authentication failure.
        """
        AUTHENTICATE_RETURN_VALUE = None
        mock_authenticate.return_value = AUTHENTICATE_RETURN_VALUE

        response = self.client.post(**self.REQUEST_ARGS)

        self.assertEqual(mock_authenticate.call_args[1]["email"], self.EMAIL)
        self.assertEqual(mock_authenticate.call_args[1]["password"], self.PASSWORD)
        mock_create_tokens.assert_not_called()

        content = json.loads(response.text)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(content["detail"], "Invalid credentials.")

    def test_failure_on_account_not_active(
        self,
        mock_authenticate: MagicMock,
        mock_create_tokens: MagicMock,
    ):
        """
        Returns 401 and correct message on authentication failure.
        """
        AUTHENTICATE_RETURN_VALUE: User = User(
            pk=self.USER_ID, email=self.EMAIL, password=self.PASSWORD, is_active=False
        )
        mock_authenticate.return_value = AUTHENTICATE_RETURN_VALUE

        response = self.client.post(**self.REQUEST_ARGS)

        self.assertEqual(mock_authenticate.call_args[1]["email"], self.EMAIL)
        self.assertEqual(mock_authenticate.call_args[1]["password"], self.PASSWORD)
        mock_create_tokens.assert_not_called()

        content = json.loads(response.text)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(content["detail"], "Account is not active.")


@patch("app.api.AuthToken.is_token_blacklisted")
@patch("users.api.AuthToken.blacklist_token")
class LogoutViewTests(TestCase):
    def setUp(self):
        # TODO: move authorization in tests the top level?
        user = create_user(email="test@test.com", password="pass")
        self.TOKENS = AuthToken.create_tokens(user.id)
        self.client.cookies["refresh_token"] = self.TOKENS["refresh_token"]

    def test_succesful_logout(
        self, mock_blacklist_token: MagicMock, mock_is_token_blacklisted: MagicMock
    ):
        """
        Blacklists access and refresh token.
        """
        mock_is_token_blacklisted.return_value = False

        response = self.client.post(
            path=reverse("api-1:logout"),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.TOKENS['access_token']}",
        )

        self.assertEqual(mock_blacklist_token.call_count, 2)
        self.assertEqual(
            mock_blacklist_token.call_args_list[0][1]["token"],
            self.TOKENS["access_token"],
        )
        self.assertEqual(
            mock_blacklist_token.call_args_list[1][1]["token"],
            self.TOKENS["refresh_token"],
        )

        content = json.loads(response.text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["detail"], "You have successfully logged out.")


class CreateUserCommandTests(TestCase):
    def test_user_is_created(self):
        email = "test@email.com"

        created_user = commands.create_user(email=email, password="pass")
        user = User.objects.get(email=email)

        self.assertEqual(created_user, user)

    def test_throws_exception_if_email_already_exists(self):
        email = "existing@email.com"
        password = "pass"

        commands.create_user(email=email, password=password)

        with self.assertRaises(HttpError):
            commands.create_user(email=email, password="pass")


class ActivateUserCommandTests(TestCase):
    def test_user_is_activated(self):
        user = create_user(email="test@user.com", password="pass")
        self.assertFalse(user.is_active)

        token = default_token_generator.make_token(user)
        commands.activate_user_account(user=user, token=token)
        self.assertTrue(user.is_active)

    def test_throws_exception_if_token_is_invalid(self):
        user = create_user(email="test@user.com", password="pass")
        with self.assertRaises(InvalidActivationToken):
            commands.activate_user_account(user=user, token="invalid_token")


class GetUserByIdQueryTests(TestCase):
    def test_returns_correct_user(self):
        user = create_user(email="test@email.com", password="pass")
        retrieved_user = queries.get_user_by_id(user.id)

        self.assertEqual(user, retrieved_user)
