import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:flutter_application_1/models/game_models.dart';
import 'package:flutter_application_1/services/api_client.dart';
import 'package:flutter_application_1/state/game_controller.dart';

import 'support/fakes.dart';

const _snapshot = {
  'state': 'lobby',
  'round_seconds': 10,
  'players': [
    {'id': 'me', 'name': 'Emma', 'is_host': true, 'score': 0},
    {'id': 'p2', 'name': 'Jake', 'is_host': false, 'score': 0},
  ],
};

const _joinOk = {'player_id': 'me', 'is_host': true};
const _guessOk = {'points': 800, 'correct': true};

/// A controller that has completed a join, plus the fakes behind it.
Future<(GameController, FakeGameSocket, RecordingClient)> joinedController({
  Object? guess = _guessOk,
}) async {
  final recording = RecordingClient(
    join: _joinOk,
    snapshot: _snapshot,
    guess: guess,
  );
  final socket = FakeGameSocket();
  final controller = GameController(
    api: ApiClient(httpClient: recording.client, baseUrl: 'http://test'),
    socketFactory: fakeSocketFactory(socket),
  );
  await controller.joinByCode('ABC12', 'Emma');
  return (controller, socket, recording);
}

void main() {
  group('joining', () {
    test('wires identity, roster, and socket', () async {
      final (c, socket, _) = await joinedController();

      expect(c.roomCode, 'ABC12');
      expect(c.myPlayerId, 'me');
      expect(c.isHost, isTrue);
      expect(c.roundSeconds, 10);
      expect(c.players.map((p) => p.name), ['Emma', 'Jake']);
      // The socket must be opened for the room we actually joined.
      expect(socket.code, 'ABC12');
      expect(socket.playerId, 'me');
    });

    test('a failed snapshot leaves no half-joined controller', () async {
      final recording = RecordingClient(join: _joinOk, snapshot: 500);
      final controller = GameController(
        api: ApiClient(httpClient: recording.client, baseUrl: 'http://test'),
        socketFactory: fakeSocketFactory(FakeGameSocket()),
      );

      await expectLater(
        controller.joinByCode('ABC12', 'Emma'),
        throwsA(isA<ApiException>()),
      );
      expect(controller.roomCode, isNull);
      expect(controller.myPlayerId, isNull);
    });

    test('a player who joins during the snapshot is not lost', () async {
      // The socket is opened before the snapshot is fetched, so an event that
      // races the snapshot must survive the merge rather than be overwritten.
      final socket = FakeGameSocket();
      // Fire the event while the snapshot request is in flight -- i.e. after
      // the socket is connected but before the roster comes back.
      final client = MockClient((request) async {
        if (request.url.path.endsWith('/join')) {
          return http.Response(jsonEncode(_joinOk), 200);
        }
        socket.emit(PlayerJoined(player(id: 'late', name: 'Sam')));
        await pumpEventQueue();
        return http.Response(jsonEncode(_snapshot), 200);
      });
      final controller = GameController(
        api: ApiClient(httpClient: client, baseUrl: 'http://test'),
        socketFactory: fakeSocketFactory(socket),
      );

      await controller.joinByCode('ABC12', 'Emma');

      expect(
        controller.players.map((p) => p.name),
        containsAll(['Emma', 'Jake', 'Sam']),
      );
    });

    test('the exposed player list cannot be mutated by callers', () async {
      final (c, _, _) = await joinedController();
      expect(() => c.players.add(player(id: 'x')), throwsUnsupportedError);
    });
  });

  group('events', () {
    test('player_joined appends, and ignores a duplicate id', () async {
      final (c, socket, _) = await joinedController();

      socket.emit(PlayerJoined(player(id: 'p3', name: 'Sam')));
      await pumpEventQueue();
      expect(c.players.length, 3);

      socket.emit(PlayerJoined(player(id: 'p3', name: 'Sam')));
      await pumpEventQueue();
      expect(c.players.length, 3, reason: 'a replayed join must not duplicate');
    });

    test('round_started resets every per-round field', () async {
      final (c, socket, _) = await joinedController();

      // Drive round 0 into a guessed + revealed state.
      socket.emit(const RoundStarted(
        roundIndex: 0,
        photo: PhotoInfo(id: 'ph0', ownerId: 'p2', url: '/a.jpg'),
        roundEndsAt: 1000,
      ));
      await pumpEventQueue();
      await c.guess('p2');
      socket.emit(const GuessResult(guesserId: 'me', points: 700, correct: true));
      socket.emit(const RoundRevealed(roundIndex: 0, ownerId: 'p2'));
      await pumpEventQueue();
      expect(c.phase, GamePhase.revealed);

      socket.emit(const RoundStarted(
        roundIndex: 1,
        photo: PhotoInfo(id: 'ph1', ownerId: 'me', url: '/b.jpg'),
        roundEndsAt: 2000,
      ));
      await pumpEventQueue();

      expect(c.roundIndex, 1);
      expect(c.currentPhoto?.id, 'ph1');
      expect(c.roundEndsAt, 2000);
      expect(c.revealedOwnerId, isNull);
      expect(c.hasGuessedThisRound, isFalse);
      expect(c.lastPointsEarned, isNull);
      expect(c.phase, GamePhase.inRound);
    });

    test('guess_result accumulates the live score', () async {
      final (c, socket, _) = await joinedController();

      socket.emit(const GuessResult(guesserId: 'me', points: 800, correct: true));
      await pumpEventQueue();
      expect(c.me?.score, 800, reason: 'the in-game score badge reads this');
      expect(c.lastPointsEarned, 800);

      socket.emit(const GuessResult(guesserId: 'me', points: 300, correct: true));
      await pumpEventQueue();
      expect(c.me?.score, 1100, reason: 'scores accumulate across rounds');
    });

    test('another player\'s guess_result updates them, not me', () async {
      final (c, socket, _) = await joinedController();

      socket.emit(const GuessResult(guesserId: 'p2', points: 500, correct: true));
      await pumpEventQueue();

      expect(c.players.firstWhere((p) => p.id == 'p2').score, 500);
      expect(c.me?.score, 0);
      expect(c.lastPointsEarned, isNull, reason: 'only my own result banners');
    });

    test('photos_updated refreshes readiness and unblocks starting', () async {
      final (c, socket, _) = await joinedController();
      expect(c.canStart, isFalse, reason: 'nobody has uploaded yet');

      socket.emit(PhotosUpdated([
        player(id: 'me', name: 'Emma', isHost: true, photoCount: 3),
        player(id: 'p2', name: 'Jake', photoCount: 2),
      ]));
      await pumpEventQueue();

      expect(c.players.every((p) => p.hasPhotos), isTrue);
      expect(c.canStart, isTrue);
    });

    test('one uploader is not enough to start', () async {
      final (c, socket, _) = await joinedController();

      socket.emit(PhotosUpdated([
        player(id: 'me', name: 'Emma', isHost: true, photoCount: 5),
        player(id: 'p2', name: 'Jake'),
      ]));
      await pumpEventQueue();

      expect(c.canStart, isFalse);
    });

    test('game_finished stores rankings and finishes', () async {
      final (c, socket, _) = await joinedController();

      socket.emit(GameFinished([
        player(id: 'p2', name: 'Jake', score: 900),
        player(id: 'me', name: 'Emma', score: 400),
      ]));
      await pumpEventQueue();

      expect(c.phase, GamePhase.finished);
      expect(c.finalRankings.first.name, 'Jake');
      expect(() => c.finalRankings.add(player()), throwsUnsupportedError);
    });

    test('room_reset restores a clean lobby for the next game', () async {
      final (c, socket, _) = await joinedController();
      socket.emit(const RoundStarted(
        roundIndex: 2,
        photo: PhotoInfo(id: 'ph', ownerId: 'p2', url: '/a.jpg'),
        roundEndsAt: 1000,
      ));
      socket.emit(GameFinished([player(id: 'me', score: 900)]));
      await pumpEventQueue();

      socket.emit(RoomReset([
        player(id: 'me', name: 'Emma', isHost: true, score: 900),
        player(id: 'p2', name: 'Jake', score: 400),
      ]));
      await pumpEventQueue();

      expect(c.phase, GamePhase.lobby);
      expect(c.roundIndex, 0);
      expect(c.currentPhoto, isNull);
      expect(c.roundEndsAt, isNull);
      expect(c.revealedOwnerId, isNull);
      expect(c.hasGuessedThisRound, isFalse);
      expect(c.lastPointsEarned, isNull);
      expect(c.finalRankings, isEmpty);
      // Scores carry over between games.
      expect(c.me?.score, 900);
    });

    test('an unknown event type is ignored, not fatal', () async {
      final (c, socket, _) = await joinedController();
      socket.emit(const UnknownEvent('something_new'));
      await pumpEventQueue();
      expect(c.phase, GamePhase.lobby);
    });
  });

  group('connection loss', () {
    test('a dropped socket surfaces instead of freezing silently', () async {
      final (c, socket, _) = await joinedController();
      expect(c.connectionError, isNull);

      socket.dropConnection();
      await pumpEventQueue();

      expect(c.connectionError, isNotNull);
    });

    test('a stream error surfaces too', () async {
      final (c, socket, _) = await joinedController();
      socket.emitError(Exception('boom'));
      await pumpEventQueue();
      expect(c.connectionError, isNotNull);
    });

    test('reconnect re-seeds from the server and clears the error', () async {
      final (c, socket, recording) = await joinedController();
      socket.dropConnection();
      await pumpEventQueue();
      expect(c.connectionError, isNotNull);

      await c.reconnect();

      expect(c.connectionError, isNull);
      // Events missed while offline are gone, so state must come from the
      // snapshot, not be assumed.
      expect(recording.countEndingWith('/ABC12'), 2);
      expect(c.players.length, 2);
    });

    test('normal disposal does not raise a connection error', () async {
      final (c, _, _) = await joinedController();
      c.dispose();
      await pumpEventQueue();
      expect(c.connectionError, isNull);
    });
  });

  group('guessing', () {
    test('locks the round and sends the round index', () async {
      final (c, socket, recording) = await joinedController();
      socket.emit(const RoundStarted(
        roundIndex: 4,
        photo: PhotoInfo(id: 'ph', ownerId: 'p2', url: '/a.jpg'),
        roundEndsAt: 1000,
      ));
      await pumpEventQueue();

      await c.guess('p2');

      expect(c.hasGuessedThisRound, isTrue);
      final body = (recording.requests.last as dynamic).body as String;
      expect(body, contains('"round_index":4'));
      expect(body, isNot(contains('seconds_left')));
    });

    test('a second guess in the same round makes no request', () async {
      final (c, _, recording) = await joinedController();

      await c.guess('p2');
      await c.guess('p2');

      expect(recording.countEndingWith('/guess'), 1);
    });

    test('a failed guess releases the lock so the player can retry', () async {
      final (c, _, _) = await joinedController(guess: 500);

      await expectLater(c.guess('p2'), throwsA(isA<ApiException>()));

      expect(
        c.hasGuessedThisRound,
        isFalse,
        reason: 'a transient failure must not lock the player out of the round',
      );
    });
  });

  group('uploading', () {
    test('one failed photo does not cost the rest of the batch', () async {
      var uploadAttempts = 0;
      final socket = FakeGameSocket();
      final client = MockClient((request) async {
        if (request.url.path.contains('/photos')) {
          uploadAttempts++;
          // The second photo fails; the others must still land.
          if (uploadAttempts == 2) {
            return http.Response('{"detail":"too large"}', 413);
          }
          return http.Response(jsonEncode({'url': '/p.jpg'}), 200);
        }
        if (request.url.path.endsWith('/join')) {
          return http.Response(jsonEncode(_joinOk), 200);
        }
        return http.Response(jsonEncode(_snapshot), 200);
      });
      final c = GameController(
        api: ApiClient(httpClient: client, baseUrl: 'http://test'),
        socketFactory: fakeSocketFactory(socket),
      );
      await c.joinByCode('ABC12', 'Emma');

      final uploaded = await c.uploadPhotos([
        Uint8List.fromList([1]),
        Uint8List.fromList([2]),
        Uint8List.fromList([3]),
      ]);

      expect(uploadAttempts, 3, reason: 'the batch continues past a failure');
      expect(uploaded, 2, reason: 'and reports how many actually landed');
    });
  });
}
