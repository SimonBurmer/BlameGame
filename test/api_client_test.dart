// Unit tests for ApiClient using a mocked http.Client (http/testing.dart).
// No real network, no backend, no emulator — pure `flutter test`.

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:flutter_application_1/services/api_client.dart';

void main() {
  test('createRoom posts to /rooms and returns the code', () async {
    late http.Request captured;
    final mock = MockClient((req) async {
      captured = req;
      return http.Response(jsonEncode({'code': 'ABC12'}), 200);
    });
    final api = ApiClient(httpClient: mock, baseUrl: 'http://test');

    final code = await api.createRoom();

    expect(code, 'ABC12');
    expect(captured.method, 'POST');
    expect(captured.url.toString(), 'http://test/rooms');
  });

  test('joinRoom sends the name and parses player_id + is_host', () async {
    late http.Request captured;
    final mock = MockClient((req) async {
      captured = req;
      return http.Response(
        jsonEncode({'player_id': 'p1', 'is_host': true}),
        200,
      );
    });
    final api = ApiClient(httpClient: mock, baseUrl: 'http://test');

    final result = await api.joinRoom('ABC12', 'Emma');

    expect(result.playerId, 'p1');
    expect(result.isHost, true);
    expect(captured.url.toString(), 'http://test/rooms/ABC12/join');
    expect(jsonDecode(captured.body)['name'], 'Emma');
  });

  test('submitGuess returns points from the response', () async {
    final mock = MockClient((req) async {
      final body = jsonDecode(req.body);
      expect(body['guesser_id'], 'p2');
      expect(body['seconds_left'], 8);
      return http.Response(jsonEncode({'points': 800, 'correct': true}), 200);
    });
    final api = ApiClient(httpClient: mock, baseUrl: 'http://test');

    final points = await api.submitGuess(
      'ABC12',
      guesserId: 'p2',
      guessedOwnerId: 'p1',
      secondsLeft: 8,
    );

    expect(points, 800);
  });

  test('getRoom parses state and players', () async {
    final mock = MockClient((req) async {
      return http.Response(
        jsonEncode({
          'state': 'lobby',
          'players': [
            {'id': 'p1', 'name': 'Emma', 'score': 0, 'is_host': true},
            {'id': 'p2', 'name': 'Jake', 'score': 0, 'is_host': false},
          ],
        }),
        200,
      );
    });
    final api = ApiClient(httpClient: mock, baseUrl: 'http://test');

    final room = await api.getRoom('ABC12');

    expect(room.state, 'lobby');
    expect(room.players.map((p) => p.name), ['Emma', 'Jake']);
  });

  test('resetRoom posts host_id to /rooms/{code}/reset', () async {
    late http.Request captured;
    final mock = MockClient((req) async {
      captured = req;
      return http.Response(jsonEncode({'code': 'ABC12', 'state': 'lobby'}), 200);
    });
    final api = ApiClient(httpClient: mock, baseUrl: 'http://test');

    await api.resetRoom('ABC12', hostId: 'p1');

    expect(captured.method, 'POST');
    expect(captured.url.toString(), 'http://test/rooms/ABC12/reset');
    expect(jsonDecode(captured.body)['host_id'], 'p1');
  });

  test('non-2xx response throws ApiException', () async {
    final mock = MockClient((req) async => http.Response('name taken', 400));
    final api = ApiClient(httpClient: mock, baseUrl: 'http://test');

    expect(
      () => api.joinRoom('ABC12', 'Emma'),
      throwsA(isA<ApiException>()),
    );
  });
}
