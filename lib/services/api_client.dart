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

  Uri _uri(String path, [Map<String, dynamic>? query]) =>
      Uri.parse('$baseUrl$path').replace(
        queryParameters: query?.map((k, v) => MapEntry(k, '$v')),
      );

  Map<String, dynamic> _decode(http.Response resp) {
    if (resp.statusCode < 200 || resp.statusCode >= 300) {
      throw ApiException(resp.statusCode, resp.body);
    }
    return jsonDecode(resp.body) as Map<String, dynamic>;
  }

  /// Create a new room; returns its join code.
  Future<String> createRoom() async {
    final resp = await _http.post(_uri('/rooms'));
    return _decode(resp)['code'] as String;
  }

  /// Join a room by code; returns (playerId, isHost).
  Future<({String playerId, bool isHost})> joinRoom(
    String code,
    String name,
  ) async {
    final resp = await _http.post(
      _uri('/rooms/$code/join'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'name': name}),
    );
    final body = _decode(resp);
    return (playerId: body['player_id'] as String, isHost: body['is_host'] as bool);
  }

  /// Upload a photo owned by [ownerId]. Returns the stored photo's relative URL.
  Future<String> uploadPhoto(
    String code,
    String ownerId,
    Uint8List bytes, {
    String filename = 'photo.jpg',
  }) async {
    final request = http.MultipartRequest(
      'POST',
      _uri('/rooms/$code/photos', {'owner_id': ownerId}),
    )..files.add(http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: filename,
        contentType: MediaType('image', 'jpeg'),
      ));
    final streamed = await _http.send(request);
    final resp = await http.Response.fromStream(streamed);
    return _decode(resp)['url'] as String;
  }

  /// Fetch the current room snapshot (players, state, rounds).
  Future<({String state, List<GamePlayer> players})> getRoom(String code) async {
    final resp = await _http.get(_uri('/rooms/$code'));
    final body = _decode(resp);
    final players = (body['players'] as List<dynamic>)
        .map((e) => GamePlayer.fromJson(e as Map<String, dynamic>))
        .toList();
    return (state: body['state'] as String, players: players);
  }

  /// Host starts the game.
  Future<void> startGame(
    String code, {
    required String hostId,
    int totalRounds = 5,
    int roundSeconds = 10,
  }) async {
    final resp = await _http.post(
      _uri('/rooms/$code/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'host_id': hostId,
        'total_rounds': totalRounds,
        'round_seconds': roundSeconds,
      }),
    );
    _decode(resp);
  }

  /// Submit a guess; returns points earned.
  Future<int> submitGuess(
    String code, {
    required String guesserId,
    required String guessedOwnerId,
    required int secondsLeft,
  }) async {
    final resp = await _http.post(
      _uri('/rooms/$code/guess'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'guesser_id': guesserId,
        'guessed_owner_id': guessedOwnerId,
        'seconds_left': secondsLeft,
      }),
    );
    return (_decode(resp)['points'] as num).toInt();
  }

  void close() => _http.close();
}
