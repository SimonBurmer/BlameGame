import 'package:flutter/material.dart';

import '../config.dart';
import '../models/game_models.dart';
import '../services/photo_sampler.dart';
import '../state/game_controller.dart';
import '../theme/app_theme.dart';
import '../ui/connection_banner.dart';
import '../ui/player_cosmetics.dart';
import 'game_screen.dart';

class LobbyScreen extends StatefulWidget {
  final GameController controller;
  const LobbyScreen({super.key, required this.controller});

  @override
  State<LobbyScreen> createState() => _LobbyScreenState();
}

class _LobbyScreenState extends State<LobbyScreen> {
  GameController get c => widget.controller;
  final _sampler = PhotoSampler();
  bool _photoUploaded = false;
  bool _uploading = false;
  bool _navigated = false;

  @override
  void initState() {
    super.initState();
    c.addListener(_onChange);
  }

  @override
  void dispose() {
    c.removeListener(_onChange);
    super.dispose();
  }

  void _onChange() {
    // Guard first: this fires from the WebSocket stream, so the State can be
    // defunct by now and Navigator.of(context) would throw.
    if (!mounted) return;
    // Kicked out: leave the lobby instead of sitting in a room we're not in.
    if (!_navigated && c.hasLeftRoom) {
      _navigated = true;
      final reason = c.removedFromRoom;
      // Grab the messenger before popping: showing the snackbar on this route
      // and then popping takes the explanation down with the lobby, so the
      // kicked player is ejected with no idea why.
      final messenger = ScaffoldMessenger.of(context);
      Navigator.of(context).pop();
      if (reason != null) {
        messenger.showSnackBar(SnackBar(content: Text(reason)));
      }
      return;
    }
    // When the backend starts the game, move everyone to the game screen.
    if (!_navigated && c.phase != GamePhase.lobby) {
      _navigated = true;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => GameScreen(controller: c)),
      );
      return;
    }
    setState(() {});
  }

  /// Auto-samples random photos from the camera roll and batch-uploads them.
  Future<void> _addPhotos() async {
    if (_uploading) return;
    setState(() => _uploading = true);
    try {
      final photos = await _sampler.sampleRandomPhotos(count: photoSampleCount);
      if (photos.isEmpty) {
        _snack('No photos found in your camera roll');
        return;
      }
      final uploaded = await c.uploadPhotos(photos);
      if (mounted) setState(() => _photoUploaded = true);
      _snack('Added $uploaded photo${uploaded == 1 ? '' : 's'}');
    } on PhotoPermissionDenied {
      _snack('Photo access denied — enable it in Settings to add photos');
    } catch (e) {
      _snack('Upload failed: $e');
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  Future<void> _start() async {
    try {
      await c.startGame(totalRounds: 5, roundSeconds: 10);
    } catch (e) {
      _snack('Could not start: $e');
    }
  }

  /// Leave the room. We pop regardless: the player asked to go, so a failed
  /// call shouldn't trap them in a lobby they've mentally left.
  Future<void> _leave() async {
    try {
      await c.leaveRoom();
    } catch (_) {
      // Ignored on purpose -- see above.
    }
    if (mounted && !_navigated) {
      _navigated = true;
      Navigator.of(context).pop();
    }
  }

  Future<void> _kick(GamePlayer player) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text('Remove ${player.name}?'),
        content: Text("They'll be dropped from the room and lose their photos."),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            child: const Text('Remove'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await c.kickPlayer(player.id);
    } catch (e) {
      _snack('Could not remove ${player.name}: $e');
    }
  }

  void _snack(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF1A1A2E), Color(0xFF16213E), Color(0xFF0F3460)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              ConnectionBanner(controller: c),
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    // IconButton, not a bare GestureDetector: a 24x24 icon is
                    // half the 48x48 minimum tap target and carries no button
                    // semantics for screen readers.
                    IconButton(
                      onPressed: _leave,
                      tooltip: 'Leave room',
                      icon: const Icon(
                        Icons.arrow_back_ios,
                        color: Colors.white,
                      ),
                    ),
                    const Expanded(
                      child: Text(
                        'LOBBY',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 3,
                        ),
                      ),
                    ),
                    const SizedBox(width: 24),
                  ],
                ),
              ),
              _gameCode(),
              const SizedBox(height: 12),
              Text(
                'Share this code with friends',
                style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.4),
                  fontSize: 13,
                ),
              ),
              const SizedBox(height: 28),
              Text(
                'PLAYERS (${c.players.length})',
                style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.6),
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 2,
                ),
              ),
              const SizedBox(height: 16),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  itemCount: c.players.length,
                  itemBuilder: (context, i) => _playerTile(c.players[i]),
                ),
              ),
              _bottomControls(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _gameCode() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 40),
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 24),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.15)),
      ),
      // FittedBox: the code is 24pt with 6pt letter-spacing, which overflows a
      // narrow phone (and any phone at a large text scale) without it.
      child: FittedBox(
        fit: BoxFit.scaleDown,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Game Code: ',
              style: TextStyle(
                color: context.colors.onSurfaceMuted,
                fontSize: 16,
              ),
            ),
            Text(
              c.roomCode ?? '-----',
              style: TextStyle(
                color: context.colors.brand,
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 6,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _playerTile(GamePlayer player) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: player.color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: player.color.withValues(alpha: 0.3),
          width: 1.5,
        ),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 22,
            backgroundColor: player.color.withValues(alpha: 0.3),
            child: Icon(player.avatar, color: player.color, size: 26),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              player.id == c.myPlayerId ? '${player.name} (you)' : player.name,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          if (player.isHost)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFFE94560).withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'HOST',
                style: TextStyle(
                  color: Color(0xFFE94560),
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            )
          else if (player.hasPhotos)
            Icon(
              Icons.check_circle,
              semanticLabel: '${player.name} has added photos',
              color: Colors.greenAccent.withValues(alpha: 0.7),
            )
          else
            Icon(
              Icons.hourglass_empty,
              semanticLabel: '${player.name} has not added photos yet',
              color: Colors.white.withValues(alpha: 0.35),
            ),
          // Only the host can kick, and never themselves — the server enforces
          // both, this just keeps the button from offering an impossible action.
          if (c.isHost && player.id != c.myPlayerId)
            IconButton(
              onPressed: () => _kick(player),
              tooltip: 'Remove ${player.name}',
              icon: Icon(
                Icons.person_remove,
                color: Colors.white.withValues(alpha: 0.5),
              ),
            ),
        ],
      ),
    );
  }

  /// Why START is disabled, so the host isn't left guessing.
  String _blockedReason() {
    if (c.players.length < 2) return 'NEED 2+ PLAYERS';
    return 'NEED PHOTOS FROM 2+ PLAYERS';
  }

  Widget _bottomControls() {
    // Everyone can add a photo; only the host can start, and only once at
    // least two people have contributed (the server enforces the same rule).
    final canStart = c.canStart;
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
      child: Column(
        children: [
          SizedBox(
            width: double.infinity,
            height: 50,
            child: OutlinedButton.icon(
              onPressed: _uploading ? null : _addPhotos,
              icon: _uploading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Icon(
                      _photoUploaded ? Icons.check : Icons.add_a_photo,
                      color: Colors.white,
                    ),
              label: Text(
                _uploading
                    ? 'ADDING PHOTOS…'
                    : _photoUploaded
                    ? 'PHOTOS ADDED — ADD MORE'
                    : 'ADD PHOTOS',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              style: OutlinedButton.styleFrom(
                side: BorderSide(color: Colors.white.withValues(alpha: 0.3)),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),
          if (c.isHost)
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: canStart ? _start : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFE94560),
                  disabledBackgroundColor: const Color(
                    0xFFE94560,
                  ).withValues(alpha: 0.3),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: Text(
                  canStart ? 'START GAME' : _blockedReason(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
              ),
            )
          else
            Text(
              'Waiting for the host to start…',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.5),
                fontSize: 14,
              ),
            ),
        ],
      ),
    );
  }
}
