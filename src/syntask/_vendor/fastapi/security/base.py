from syntask._vendor.fastapi.openapi.models import SecurityBase as SecurityBaseModel


class SecurityBase:
    model: SecurityBaseModel
    scheme_name: str
