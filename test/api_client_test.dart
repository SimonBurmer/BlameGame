// Unit tests for ApiClient using a mocked http.Client (http/testing.dart).
// No real network, no backend, no emulator — pure `flutter test`.

import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:photo_blame/services/api_client.dart';

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
      expect(body['guessed_owner_id'], 'p1');
      // Timing is measured server-side; the client only says which round.
      expect(body['round_index'], 3);
      expect(body.containsKey('seconds_left'), isFalse);
      return http.Response(jsonEncode({'points': 800, 'correct': true}), 200);
    });
    final api = ApiClient(httpClient: mock, baseUrl: 'http://test');

    final points = await api.submitGuess(
      'ABC12',
      guesserId: 'p2',
      guessedOwnerId: 'p1',
      roundIndex: 3,
    );

    expect(points, 800);
  });

  test('getRoom parses players and round_seconds', () async {
    final mock = MockClient((req) async {
      return http.Response(
        jsonEncode({
          'state': 'lobby',
          'round_seconds': 15,
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

    expect(room.roundSeconds, 15);
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

  test('uploadPhoto labels the part from the bytes, not the filename', () async {
    // A PNG used to be announced as image/jpeg and stored as .jpg.
    final bodies = <String>[];
    final mock = MockClient((req) async {
      bodies.add(utf8.decode(req.bodyBytes, allowMalformed: true));
      return http.Response(jsonEncode({'url': '/p.png'}), 200);
    });
    final api = ApiClient(httpClient: mock, baseUrl: 'http://test');

    final png = Uint8List.fromList(
      [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 1, 2, 3],
    );
    await api.uploadPhoto('ABC12', 'p1', png, filename: 'photo_0');
    await api.uploadPhoto(
      'ABC12',
      'p1',
      Uint8List.fromList([0xFF, 0xD8, 0xFF, 1, 2, 3]),
      filename: 'photo_1',
    );

    expect(bodies[0], contains('image/png'));
    expect(bodies[0], contains('filename="photo_0.png"'));
    expect(bodies[1], contains('image/jpeg'));
    expect(bodies[1], contains('filename="photo_1.jpeg"'));
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
