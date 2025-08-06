import jwt
from django.apps import apps
from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

OIDC_USER_MAPPING = (
    ("username", "gaspar"),
    ("email", "email"),
    ("first_name", "given_name"),
    ("last_name", "family_name"),
)


class EPFLOIDCAB(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        sciper = claims.get("uniqueid")
        if not sciper:
            return self.UserModel.objects.none()

        is_app_using_profile = hasattr(settings, "AUTH_PROFILE_MODULE")

        if is_app_using_profile:
            user_profile_model = apps.get_model(
                *settings.AUTH_PROFILE_MODULE.split(".")
            )
            try:
                user_profile = user_profile_model.objects.filter(
                    sciper=sciper
                ).latest("id")
                return self.UserModel.objects.filter(id=user_profile.user.id)
            except user_profile_model.DoesNotExist:
                return self.UserModel.objects.none()
        else:
            return self.UserModel.objects.filter(sciper=sciper)

    def create_user(self, claims):
        is_app_using_profile = hasattr(settings, "AUTH_PROFILE_MODULE")

        if is_app_using_profile:
            user = self.UserModel.objects.create_user(
                username=claims.get("gaspar"),
                email=claims.get("email"),
                first_name=claims.get("given_name"),
                last_name=claims.get("family_name"),
            )
            user_profile_model = apps.get_model(
                *settings.AUTH_PROFILE_MODULE.split(".")
            )
            profile, _ = user_profile_model.objects.get_or_create(user=user)
            profile.sciper = claims.get("uniqueid")
            profile.save()
        else:
            user = self.UserModel.objects.create_user(
                username=claims.get("gaspar"),
                email=claims.get("email"),
                first_name=claims.get("given_name"),
                last_name=claims.get("family_name"),
                sciper=claims.get("uniqueid"),
            )

        return user

    def update_user(self, user, claims):
        for model_field, oidc_field in OIDC_USER_MAPPING:
            if claims.get(oidc_field):
                setattr(user, model_field, claims.get(oidc_field))

        user.save()
        return user

    def get_userinfo(self, access_token, id_token, payload):
        """
        Get user info from both user info endpoint (default) and
        merge with ID token information.
        """
        userinfo = super(EPFLOIDCAB, self).get_userinfo(
            access_token, id_token, payload
        )

        id_token_decoded: str = jwt.decode(
            id_token, options={"verify_signature": False}
        )

        userinfo.update(id_token_decoded)

        return userinfo
