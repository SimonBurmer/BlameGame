import 'package:flutter_test/flutter_test.dart';
import 'package:photo_blame/config.dart';

void main() {
  test('debug builds fall back to localhost so flutter run just works', () {
    // A test binary is a debug build, so this is the fallback in effect here.
    expect(apiBase, 'http://localhost:8000');
    expect(apiBaseProblem, isNull);
  });

  test('a release build with no API_BASE is rejected, not pointed at loopback',
      () {
    // The old default shipped an IPA aimed at the device's own localhost:
    // every call failed, with nothing on screen to say why.
    expect(apiBaseProblemFor('', release: true), contains('no backend URL'));
    expect(apiBaseProblemFor('', release: false), contains('no backend URL'));
  });

  test('a release build refuses cleartext http, which iOS blocks anyway', () {
    expect(
      apiBaseProblemFor('http://localhost:8000', release: true),
      contains('https'),
    );
    expect(
      apiBaseProblemFor('https://api.example.com', release: true),
      isNull,
    );
  });

  test('a debug build may talk to a local http backend', () {
    expect(apiBaseProblemFor('http://localhost:8000', release: false), isNull);
  });

  test('the socket scheme follows the api scheme', () {
    expect(wsBaseFor('https://api.example.com'), 'wss://api.example.com');
    expect(wsBaseFor('http://localhost:8000'), 'ws://localhost:8000');
  });
}
