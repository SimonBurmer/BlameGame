import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/game_models.dart';
import '../services/api_client.dart';
import '../services/game_socket.dart';

/// Which phase of the game the UI is in.
enum GamePhase { lobby, inRound, revealed, finished }

/// Holds all live game state and owns the API + WebSocket connections.
///
/// Screens listen to this ([ChangeNotifier]) and rebuild when it changes.
/// One controller instance is created when a player creates/joins a room and
/// passed down through the screens.
class GameController extends ChangeNotifier {
  final ApiClient api;

  GameController({ApiClient? api}) : api = api ?? ApiClient();

  // Identity / room
  String? roomCode;
  String? myPlayerId;
  bool isHost = false;

  // Live state
  final List<GamePlayer> players = [];
  GamePhase phase = GamePhase.lobby;

  // Round state
  int roundIndex = 0;
  PhotoInfo? currentPhoto;
  String? revealedOwnerId;
  bool hasGuessedThisRound = false;
  int? lastPointsEarned;

  // Results
  List<GamePlayer> finalRankings = [];

  GameSocket? _socket;
  StreamSubscription<GameEvent>? _sub;

  GamePlayer? get me {
    for (final p in players) {
      if (p.id == myPlayerId) return p;
    }
    return null;
  }

  /// Create a room and join it as the host.
  Future<void> createAndHost(String name) async {
    final code = await api.createRoom();
    await _join(code, name);
  }

  /// Join an existing room by code.
  Future<void> joinByCode(String code, String name) => _join(code, name);

  Future<void> _join(String code, String name) async {
    final result = await api.joinRoom(code, name);
    roomCode = code;
    myPlayerId = result.playerId;
    isHost = result.isHost;

    // Seed the current player list, then connect the socket for live updates.
    final snapshot = await api.getRoom(code);
    players
      ..clear()
      ..addAll(snapshot.players);

    _connectSocket();
    notifyListeners();
  }

  void _connectSocket() {
    _socket = GameSocket.connect(roomCode!, myPlayerId!);
    _sub = _socket!.events.listen(_onEvent);
  }

  void _onEvent(GameEvent event) {
    switch (event) {
      case PlayerJoined(:final player):
        if (!players.any((p) => p.id == player.id)) {
          players.add(player);
        }
      case RoundStarted(:final roundIndex, :final photo):
        this.roundIndex = roundIndex;
        currentPhoto = photo;
        revealedOwnerId = null;
        hasGuessedThisRound = false;
        lastPointsEarned = null;
        phase = GamePhase.inRound;
      case RoundRevealed(:final ownerId):
        revealedOwnerId = ownerId;
        phase = GamePhase.revealed;
      case GuessResult(:final guesserId, :final points):
        if (guesserId == myPlayerId) {
          lastPointsEarned = points;
        }
      case GameFinished(:final rankings):
        finalRankings = rankings;
        phase = GamePhase.finished;
      case UnknownEvent():
        break;
    }
    notifyListeners();
  }

  /// Uploads a single photo (bytes already read) for the local player.
  Future<void> uploadPhoto(
    Uint8List bytes, {
    String filename = 'photo.jpg',
  }) async {
    await api.uploadPhoto(roomCode!, myPlayerId!, bytes, filename: filename);
  }

  /// Batch-uploads photos for the local player. Each image is sent as its own
  /// multipart call because the backend accepts one photo per request.
  /// Returns the number successfully uploaded.
  Future<int> uploadPhotos(List<Uint8List> photos) async {
    var uploaded = 0;
    for (var i = 0; i < photos.length; i++) {
      await api.uploadPhoto(
        roomCode!,
        myPlayerId!,
        photos[i],
        filename: 'photo_$i.jpg',
      );
      uploaded++;
    }
    return uploaded;
  }

  /// Host starts the game.
  Future<void> startGame({int totalRounds = 5, int roundSeconds = 10}) async {
    await api.startGame(
      roomCode!,
      hostId: myPlayerId!,
      totalRounds: totalRounds,
      roundSeconds: roundSeconds,
    );
  }

  /// Submit a guess for the current round.
  Future<void> guess(String guessedOwnerId, int secondsLeft) async {
    if (hasGuessedThisRound) return;
    hasGuessedThisRound = true;
    notifyListeners();
    await api.submitGuess(
      roomCode!,
      guesserId: myPlayerId!,
      guessedOwnerId: guessedOwnerId,
      secondsLeft: secondsLeft,
    );
  }

  @override
  void dispose() {
    _sub?.cancel();
    _socket?.close();
    api.close();
    super.dispose();
  }
}
