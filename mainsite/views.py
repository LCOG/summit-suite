import base64
import os
import requests

from django.contrib.auth.models import User
from django.http.response import HttpResponse

from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from mainsite.helpers import record_error
from mainsite.serializers import AuthTokenSerializerWithoutPassword
from people.models import Employee


class ObtainAuthTokenWithoutPassword(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializerWithoutPassword

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
        except User.DoesNotExist:
            message = f'User {request.data["username"]} does not exist'
            record_error('Error logging in with MS SSO', message, request)
            return Response({'error': message}, status=404)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


obtain_auth_token_without_password = ObtainAuthTokenWithoutPassword.as_view()

class ObtainZoomAccessToken(APIView):
    def post(self, request, *args, **kwargs):
        client_id = os.environ.get('ZOOM_CLIENT_ID')
        client_secret = os.environ.get('ZOOM_CLIENT_SECRET')
        redirect_url = os.environ.get('ZOOM_REDIRECT_URL')
        ascii_string = f'{ client_id }: { client_secret }'.encode('ascii')
        encoded_string = base64.b64encode(ascii_string).decode('ascii')
        response = requests.post(
            'https://zoom.us/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'code': request.data['code'],
                'redirect_uri': redirect_url,
            },
            headers={
                'Authorization': f'Basic { encoded_string }',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        return Response(response)

obtain_zoom_access_token = ObtainZoomAccessToken.as_view()


def health_check_view(request):
    return HttpResponse("OK")