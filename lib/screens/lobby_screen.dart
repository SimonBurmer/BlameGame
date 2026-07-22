import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../models/game_models.dart';
import '../state/game_controller.dart';
import 'game_screen.dart';

class LobbyScreen extends StatefulWidget {
  final GameController controller;
  const LobbyScreen({super.key, required this.controller});

  @override
  State<LobbyScreen> createState() => _LobbyScreenState();
}

class _LobbyScreenState extends State<LobbyScreen> {
  GameController get c => widget.controller;
  bool _photoUploaded = false;
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
    // When the backend starts the game, move everyone to the game screen.
    if (!_navigated && c.phase != GamePhase.lobby) {
      _navigated = true;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => GameScreen(controller: c)),
      );
      return;
    }
    if (mounted) setState(() {});
  }

  Future<void> _pickPhoto() async {
    final picker = ImagePicker();
    final file = await picker.pickImage(source: ImageSource.gallery);
    if (file == null) return;
    final bytes = await file.readAsBytes();
    try {
      await c.uploadPhoto(bytes, filename: file.name);
      if (mounted) setState(() => _photoUploaded = true);
    } catch (e) {
      _snack('Upload failed: $e');
    }
  }

  Future<void> _start() async {
    try {
      await c.startGame(totalRounds: 5, roundSeconds: 10);
    } catch (e) {
      _snack('Could not start: $e');
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
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: const Icon(Icons.arrow_back_ios,
                          color: Colors.white),
                    ),
                    const Expanded(
                      child: Text('LOBBY',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 3)),
                    ),
                    const SizedBox(width: 24),
                  ],
                ),
              ),
              _gameCode(),
              const SizedBox(height: 12),
              Text('Share this code with friends',
                  style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.4),
                      fontSize: 13)),
              const SizedBox(height: 28),
              Text('PLAYERS (${c.players.length})',
                  style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.6),
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 2)),
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
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('Game Code: ',
              style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.6), fontSize: 16)),
          Text(
            c.roomCode ?? '-----',
            style: const TextStyle(
                color: Color(0xFFE94560),
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 6),
          ),
        ],
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
        border:
            Border.all(color: player.color.withValues(alpha: 0.3), width: 1.5),
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
                  fontWeight: FontWeight.w600),
            ),
          ),
          if (player.isHost)
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFFE94560).withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text('HOST',
                  style: TextStyle(
                      color: Color(0xFFE94560),
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1)),
            )
          else
            Icon(Icons.check_circle,
                color: Colors.greenAccent.withValues(alpha: 0.7)),
        ],
      ),
    );
  }

  Widget _bottomControls() {
    // Everyone can add a photo; only the host can start.
    final canStart = c.isHost && c.players.length >= 2;
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
      child: Column(
        children: [
          SizedBox(
            width: double.infinity,
            height: 50,
            child: OutlinedButton.icon(
              onPressed: _pickPhoto,
              icon: Icon(_photoUploaded ? Icons.check : Icons.add_a_photo,
                  color: Colors.white),
              label: Text(
                _photoUploaded ? 'PHOTO ADDED — ADD ANOTHER' : 'ADD A PHOTO',
                style: const TextStyle(
                    color: Colors.white, fontWeight: FontWeight.bold),
              ),
              style: OutlinedButton.styleFrom(
                side: BorderSide(color: Colors.white.withValues(alpha: 0.3)),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
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
                  disabledBackgroundColor:
                      const Color(0xFFE94560).withValues(alpha: 0.3),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16)),
                ),
                child: Text(
                  canStart ? 'START GAME' : 'NEED 2+ PLAYERS',
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 2),
                ),
              ),
            )
          else
            Text('Waiting for the host to start…',
                style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.5), fontSize: 14)),
        ],
      ),
    );
  }
}
