import 'dart:async';
import 'dart:convert';

import 'package:blame_game/models/game_models.dart';
import 'package:blame_game/services/game_socket.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

/// A [GameSocket] stand-in driven by the test.
///
/// `GameSocket` has a private constructor, but Dart's implicit interfaces let
/// a test implement its two public members — so no production abstraction is
/// needed to make socket-driven state testable.
class FakeGameSocket implements GameSocket {
  final _controller = StreamController<GameEvent>.broadcast();

  /// What [GameController] passed to the factory.
  String? code;
  String? playerId;
  bool closed = false;

  /// Push an event as if the server had sent it.
  void emit(GameEvent event) => _controller.add(event);

  /// Simulate the connection dropping.
  void dropConnection() => _controller.close();

  void emitError(Object error) => _controller.addError(error);

  @override
  Stream<GameEvent> get events => _controller.stream;

  @override
  Future<void> close() async {
    closed = true;
    await _controller.close();
  }
}

/// Builds a socket factory that records its arguments into [socket].
GameSocketFactory fakeSocketFactory(FakeGameSocket socket) {
  return (String code, String playerId) {
    socket.code = code;
    socket.playerId = playerId;
    return socket;
  };
}

/// A player with sensible defaults, so tests only state what they care about.
GamePlayer player({
  String id = 'p1',
  String name = 'Emma',
  int score = 0,
  bool isHost = false,
  int photoCount = 0,
}) =>
    GamePlayer(
      id: id,
      name: name,
      score: score,
      isHost: isHost,
      photoCount: photoCount,
    );

/// An [http.Client] that answers by endpoint role, and records what it saw.
///
/// Keyed by role rather than by path substring: `/rooms/{code}` and
/// `/rooms/{code}/guess` share a prefix, so substring matching silently
/// answers a guess with a room snapshot.
class RecordingClient {
  final List<http.BaseRequest> requests = [];

  /// Each value is either a JSON-encodable body (answered 200) or an `int`
  /// status code to fail with.
  final Object? join;
  final Object? snapshot;
  final Object? guess;
  final Object? photos;
  final Object? reset;

  RecordingClient({
    this.join,
    this.snapshot,
    this.guess,
    this.photos,
    this.reset,
  });

  MockClient get client => MockClient((request) async {
        requests.add(request);
        return _respond(_routeFor(request.url.path));
      });

  Object? _routeFor(String path) {
    if (path.endsWith('/join')) return join;
    if (path.endsWith('/guess')) return guess;
    if (path.endsWith('/reset')) return reset;
    if (path.contains('/photos')) return photos;
    return snapshot;
  }

  http.Response _respond(Object? route) {
    if (route == null) return http.Response('{"detail":"no route"}', 404);
    if (route is int) return http.Response('{"detail":"boom"}', route);
    return http.Response(jsonEncode(route), 200);
  }

  int countFor(String pathFragment) =>
      requests.where((r) => r.url.path.contains(pathFragment)).length;

  /// Requests whose path ends with [suffix].
  int countEndingWith(String suffix) =>
      requests.where((r) => r.url.path.endsWith(suffix)).length;
}
