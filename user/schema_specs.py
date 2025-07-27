from drf_spectacular.utils import OpenApiResponse
from rest_framework.status import HTTP_200_OK

USER_DELETE = {
    HTTP_200_OK: OpenApiResponse(
        {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
            },
        },
        description="Deleting your account will delete your access and all your information",
    ),
}
