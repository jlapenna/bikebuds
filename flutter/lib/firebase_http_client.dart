import 'package:http/http.dart'
    show BaseRequest, BaseClient, Client, Request, StreamedResponse;

class FirebaseHttpClient extends BaseClient {
  String _encodedKey;
  Client _baseClient;
  Map<String, String> _headers;

  FirebaseHttpClient(key, token, [Client httpClient]) {
    _baseClient = httpClient == null ? new Client() : httpClient;
    _encodedKey = Uri.encodeQueryComponent(key);
    _headers = {
      "Authorization": 'Bearer ' + token,
    };
  }

  @override
  Future<StreamedResponse> send(BaseRequest request) {
    return sendWithKey(request);
  }

  Future<StreamedResponse> sendNoKey(BaseRequest request) {
    request.headers.addAll(_headers);
    return _baseClient.send(request);
  }

  Future<StreamedResponse> sendWithKey(BaseRequest request) {
    var url = request.url;
    if (url.queryParameters.containsKey('key')) {
      return new Future.error(new Exception(
          'Tried to make a HTTP request which has already a "key" query '
          'parameter. Adding the API key would override that existing value.'));
    }
    if (url.query == '') {
      url = url.replace(query: 'key=$_encodedKey');
    } else {
      url = url.replace(query: '${url.query}&key=$_encodedKey');
    }
    var modifiedRequest = Request(request.method, url);
    modifiedRequest.headers.addAll(_headers);
    return _baseClient.send(modifiedRequest);
  }
}
