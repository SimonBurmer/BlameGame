import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart' show MediaType;

import '../config.dart';
import '../models/game_models.dart';

/// Thrown when the backend returns a non-2xx response.
class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);
  @override
  String toString() => 'ApiException($statusCode): $message';
}

/// Thin wrapper over the FastAPI REST endpoints.
///
/// An [http.Client] is injected so tests can pass a mock and avoid the network.
class ApiClient {
  final http.Client _http;
  final String baseUrl;

  ApiClient({http.Client? httpClient, String? baseUrl})
      : _http = httpClient ?? http.Client(),
        baseUrl = baseUrl ?? apiBase;

  /// Every call is bounded: a backend that accepts the connection but never
  /// responds (cold start, half-open socket after a network switch) would
  /// otherwise hang the UI on a spinner with no way to cancel.
  static const Duration _timeout = Duration(seconds: 10);

  Uri _uri(String path, [Map<String, dynamic>? query]) =>
      Uri.parse('$baseUrl$path').replace(
        queryParameters: query?.map((k, v) => MapEntry(k, '$v')),
      );

  /// POST a JSON body and decode the response. Shared by every JSON endpoint.
  Future<Map<String, dynamic>> _postJson(
    String path, [
    Map<String, dynamic>? body,
  ]) async {
    final resp = await _http
        .post(
          _uri(path),
          headers: body == null
              ? null
              : const {'Content-Type': 'application/json'},
          body: body == null ? null : jsonEncode(body),
        )
        .timeout(_timeout);
    return _decode(resp);
  }

  Map<String, dynamic> _decode(http.Response resp) {
    if (resp.statusCode < 200 || resp.statusCode >= 300) {
      throw ApiException(resp.statusCode, resp.body);
    }
    return jsonDecode(resp.body) as Map<String, dynamic>;
  }

  /// Create a new room; returns its join code. Game settings (rounds, round
  /// length, hardcore mode) are set afterwards from the lobby.
  Future<String> createRoom() async =>
      (await _postJson('/rooms'))['code'] as String;

  /// Join a room by code; returns (playerId, isHost).
  Future<({String playerId, bool isHost})> joinRoom(
    String code,
    String name,
  ) async {
    final body = await _postJson('/rooms/$code/join', {'name': name});
    return (
      playerId: body['player_id'] as String,
      isHost: body['is_host'] as bool,
    );
  }

  /// The image subtype implied by [bytes]' magic number. Defaults to `jpeg`,
  /// which the server rejects if the bytes really aren't an image.
  static String _imageSubtype(Uint8List bytes) {
    const pngMagic = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];
    if (bytes.length >= pngMagic.length &&
        Iterable<int>.generate(pngMagic.length)
            .every((i) => bytes[i] == pngMagic[i])) {
      return 'png';
    }
    return 'jpeg';
  }

  /// Upload a photo owned by [ownerId]. Returns the stored photo's relative URL.
  Future<String> uploadPhoto(
    String code,
    String ownerId,
    Uint8List bytes, {
    String filename = 'photo',
  }) async {
    // Sniff the bytes rather than trust the picker's filename: the server does
    // the same, and a PNG announced as image/jpeg used to be stored as .jpg.
    final subtype = _imageSubtype(bytes);
    final request = http.MultipartRequest(
      'POST',
      _uri('/rooms/$code/photos', {'owner_id': ownerId}),
    )..files.add(http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: '$filename.$subtype',
        contentType: MediaType('image', subtype),
      ));
    final streamed = await _http.send(request).timeout(_timeout);
    final resp = await http.Response.fromStream(streamed);
    return _decode(resp)['url'] as String;
  }

  /// Fetch the current room snapshot (players, settings, photo mode).
  Future<
      ({
        List<GamePlayer> players,
        int totalRounds,
        int roundSeconds,
        bool hardcore
      })> getRoom(
    String code,
  ) async {
    final resp = await _http.get(_uri('/rooms/$code')).timeout(_timeout);
    final body = _decode(resp);
    final players = (body['players'] as List<dynamic>)
        .map((e) => GamePlayer.fromJson(e as Map<String, dynamic>))
        .toList();
    return (
      players: players,
      totalRounds: (body['total_rounds'] as num?)?.toInt() ?? 5,
      roundSeconds: (body['round_seconds'] as num).toInt(),
      // Absent only when talking to a server older than hardcore mode, where
      // every room is normal. Defaulting the other way would upload blind.
      hardcore: body['hardcore'] as bool? ?? false,
    );
  }

  /// Host updates the lobby game settings. Only the fields passed are changed.
  ///
  /// The server rejects a hardcore change once the room has photos — that lock
  /// is its call, not this client's.
  Future<void> updateSettings(
    String code, {
    required String hostId,
    int? totalRounds,
    int? roundSeconds,
    bool? hardcore,
  }) async {
    // Null means "leave this one alone", so unset fields are dropped rather
    // than sent as null (which the server would read as an explicit value).
    final body = <String, dynamic>{'host_id': hostId};
    if (totalRounds != null) body['total_rounds'] = totalRounds;
    if (roundSeconds != null) body['round_seconds'] = roundSeconds;
    if (hardcore != null) body['hardcore'] = hardcore;
    await _postJson('/rooms/$code/settings', body);
  }

  /// Host starts the game.
  Future<void> startGame(
    String code, {
    required String hostId,
    int totalRounds = 5,
    int roundSeconds = 10,
  }) async {
    await _postJson('/rooms/$code/start', {
      'host_id': hostId,
      'total_rounds': totalRounds,
      'round_seconds': roundSeconds,
    });
  }

  /// Submit a guess; returns points earned.
  ///
  /// [roundIndex] is the round the player was answering. The server rejects it
  /// if the round has already rolled over, so a guess in flight across the
  /// boundary isn't scored against a photo the player never saw.
  ///
  /// How fast the guess was is measured by the server from its own round
  /// deadline — the client does not report it, so a wrong device clock can't
  /// cost points and a patched client can't mint them.
  ///
  /// Callers generally ignore the return value and rely on the broadcast
  /// `guess_result` instead, since every client needs that echo anyway.
  Future<int> submitGuess(
    String code, {
    required String guesserId,
    required String guessedOwnerId,
    required int roundIndex,
  }) async {
    final body = await _postJson('/rooms/$code/guess', {
      'guesser_id': guesserId,
      'guessed_owner_id': guessedOwnerId,
      'round_index': roundIndex,
    });
    return (body['points'] as num).toInt();
  }

  /// Leave a room. The player is removed for everyone.
  Future<void> leaveRoom(String code, {required String playerId}) =>
      _postJson('/rooms/$code/leave', {'player_id': playerId});

  /// Host removes another player from the room.
  Future<void> kickPlayer(
    String code, {
    required String hostId,
    required String playerId,
  }) =>
      _postJson('/rooms/$code/kick', {
        'host_id': hostId,
        'player_id': playerId,
      });

  /// Host resets the room back to the lobby for a new round.
  Future<void> resetRoom(String code, {required String hostId}) =>
      _postJson('/rooms/$code/reset', {'host_id': hostId});

  void close() => _http.close();
}
