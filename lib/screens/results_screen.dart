import 'package:flutter/material.dart';

import '../models/game_models.dart';
import '../state/game_controller.dart';
import '../ui/error_text.dart';
import '../ui/player_cosmetics.dart';
import 'lobby_screen.dart';

class ResultsScreen extends StatefulWidget {
  final GameController controller;
  const ResultsScreen({super.key, required this.controller});

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  GameController get controller => widget.controller;
  bool _resetting = false;
  bool _navigated = false;

  List<GamePlayer> get _ranked => controller.finalRankings;

  @override
  void initState() {
    super.initState();
    controller.addListener(_onChange);
  }

  @override
  void dispose() {
    controller.removeListener(_onChange);
    super.dispose();
  }

  void _onChange() {
    if (!mounted) return;
    // Any player (not just the host who triggered it) lands back in the
    // lobby once the backend confirms the reset over the WebSocket.
    if (!_navigated && controller.phase == GamePhase.lobby) {
      _navigated = true;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => LobbyScreen(controller: controller)),
      );
      return;
    }
    // Without this the leaderboard is a frozen snapshot: late-arriving
    // results and connection changes would never render.
    setState(() {});
  }

  Future<void> _startNewRound() async {
    setState(() => _resetting = true);
    try {
      await controller.resetRoom();
      // Navigation happens in _onChange once the room_reset event arrives.
    } catch (e) {
      if (!mounted) return;
      setState(() => _resetting = false);
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Could not start new round: ${friendlyError(e)}')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final winner = _ranked.isNotEmpty ? _ranked.first : null;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1A1A2E), Color(0xFF16213E), Color(0xFF0F3460)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              const SizedBox(height: 24),
              _trophy(winner),
              const SizedBox(height: 32),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Row(
                  children: [
                    Text('LEADERBOARD',
                        style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.5),
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 2)),
                    const Spacer(),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  itemCount: _ranked.length,
                  itemBuilder: (context, i) => _tile(_ranked[i], i + 1),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
                child: Column(
                  children: [
                    if (controller.isHost) ...[
                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: ElevatedButton(
                          onPressed: _resetting ? null : _startNewRound,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF4ECDC4),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(14)),
                          ),
                          child: _resetting
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                      strokeWidth: 2, color: Colors.white),
                                )
                              : const Text('START NEW ROUND',
                                  style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                      letterSpacing: 2)),
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],
                    SizedBox(
                      width: double.infinity,
                      height: 52,
                      child: ElevatedButton(
                        onPressed: () => Navigator.of(context)
                            .popUntil((route) => route.isFirst),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFE94560),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14)),
                        ),
                        child: const Text('BACK TO HOME',
                            style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 2)),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _trophy(GamePlayer? winner) {
    return Column(
      children: [
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: const LinearGradient(
                colors: [Color(0xFFFFD700), Color(0xFFFFA500)]),
            boxShadow: [
              BoxShadow(
                  color: const Color(0xFFFFD700).withValues(alpha: 0.4),
                  blurRadius: 30,
                  spreadRadius: 5),
            ],
          ),
          child: const Icon(Icons.emoji_events, size: 56, color: Colors.white),
        ),
        const SizedBox(height: 16),
        const Text('WINNER',
            style: TextStyle(
                color: Color(0xFFFFD700),
                fontSize: 16,
                fontWeight: FontWeight.bold,
                letterSpacing: 6)),
        const SizedBox(height: 8),
        Text(winner?.name ?? '—',
            style: const TextStyle(
                color: Colors.white,
                fontSize: 36,
                fontWeight: FontWeight.w900)),
        Text('${winner?.score ?? 0} pts',
            style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7), fontSize: 18)),
      ],
    );
  }

  Widget _tile(GamePlayer player, int rank) {
    final medalColors = {
      1: const Color(0xFFFFD700),
      2: const Color(0xFFC0C0C0),
      3: const Color(0xFFCD7F32),
    };
    final medalColor = medalColors[rank];
    final isMe = player.id == controller.myPlayerId;

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: rank == 1
            ? const Color(0xFFFFD700).withValues(alpha: 0.08)
            : Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(14),
        border: rank == 1
            ? Border.all(color: const Color(0xFFFFD700).withValues(alpha: 0.3))
            : null,
      ),
      child: Row(
        children: [
          SizedBox(
            width: 36,
            child: medalColor != null
                ? Icon(Icons.workspace_premium, color: medalColor, size: 28)
                : Text('#$rank',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.5),
                        fontSize: 16,
                        fontWeight: FontWeight.bold)),
          ),
          const SizedBox(width: 12),
          CircleAvatar(
            radius: 20,
            backgroundColor: player.color.withValues(alpha: 0.3),
            child: Icon(player.avatar, color: player.color, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(player.name,
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w600)),
                if (isMe)
                  Text("That's you!",
                      style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.4),
                          fontSize: 12)),
              ],
            ),
          ),
          Text('${player.score}',
              style: TextStyle(
                  color:
                      rank == 1 ? const Color(0xFFFFD700) : Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold)),
          const SizedBox(width: 4),
          Text('pts',
              style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.4), fontSize: 12)),
        ],
      ),
    );
  }
}
