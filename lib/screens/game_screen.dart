import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';

import '../config.dart';
import '../models/game_models.dart';
import '../state/game_controller.dart';
import 'results_screen.dart';

class GameScreen extends StatefulWidget {
  final GameController controller;
  const GameScreen({super.key, required this.controller});

  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> with TickerProviderStateMixin {
  GameController get c => widget.controller;

  int _timeLeft = 0;
  bool _timeExpired = false;
  Timer? _displayTimer;
  int _shownRound = -1;
  bool _navigated = false;
  String? _myGuessedPlayerId;

  late AnimationController _shakeController;
  late Animation<double> _shakeAnimation;

  @override
  void initState() {
    super.initState();
    _shakeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    _shakeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _shakeController, curve: Curves.elasticIn),
    );
    c.addListener(_onChange);
    _syncToRound();
  }

  @override
  void dispose() {
    _displayTimer?.cancel();
    _shakeController.dispose();
    c.removeListener(_onChange);
    super.dispose();
  }

  void _onChange() {
    if (!mounted) return;

    if (c.phase == GamePhase.finished && !_navigated) {
      _navigated = true;
      _displayTimer?.cancel();
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => ResultsScreen(controller: c)),
      );
      return;
    }

    // New round started on the backend -> restart the local display countdown.
    if (c.phase == GamePhase.inRound && c.roundIndex != _shownRound) {
      _myGuessedPlayerId = null;
      _syncToRound();
    }

    // Round revealed -> stop the timer, shake if we were wrong.
    if (c.phase == GamePhase.revealed) {
      _displayTimer?.cancel();
      final wrong = c.hasGuessedThisRound && (c.lastPointsEarned ?? 0) == 0;
      if (wrong) _shakeController.forward(from: 0);
    }

    setState(() {});
  }

  void _syncToRound() {
    _shownRound = c.roundIndex;
    _timeExpired = false;
    _displayTimer?.cancel();
    _computeTimeLeft();
    _displayTimer = Timer.periodic(
      const Duration(seconds: 1),
      (_) => setState(_computeTimeLeft),
    );
    setState(() {});
  }

  /// Derives remaining time from the server's round_ends_at deadline instead
  /// of decrementing a local counter, so a late-arriving round_started event
  /// or a missed tick still lands on the correct remaining time.
  void _computeTimeLeft() {
    final endsAt = c.roundEndsAt;
    final remainingMs = endsAt == null
        ? 0
        : endsAt - DateTime.now().millisecondsSinceEpoch;
    _timeLeft = (remainingMs / 1000).ceil().clamp(0, c.roundSeconds);
    if (_timeLeft <= 0) {
      _timeExpired = true;
      _displayTimer?.cancel();
    }
  }

  void _guess(GamePlayer player) {
    if (c.hasGuessedThisRound || _timeExpired || c.phase != GamePhase.inRound) return;
    _myGuessedPlayerId = player.id;
    c.guess(player.id, _timeLeft);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1A1A2E), Color(0xFF0F3460)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              _topBar(),
              const SizedBox(height: 8),
              _timerBar(),
              const SizedBox(height: 16),
              Expanded(child: _photoArea()),
              const SizedBox(height: 16),
              if (c.phase == GamePhase.revealed) _resultBanner(),
              if (c.phase == GamePhase.inRound) _guessButtons(),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _topBar() {
    final myScore = c.me?.score ?? 0;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              'Round ${c.roundIndex + 1}',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFFE94560).withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                const Icon(Icons.star, color: Color(0xFFFFD700), size: 18),
                const SizedBox(width: 4),
                Text(
                  '$myScore',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _timerBar() {
    final progress = c.roundSeconds == 0 ? 0.0 : _timeLeft / c.roundSeconds;
    final color = _timeLeft <= 3
        ? const Color(0xFFE94560)
        : const Color(0xFF4ECDC4);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.timer, color: color, size: 20),
              const SizedBox(width: 6),
              Text(
                '$_timeLeft',
                style: TextStyle(
                  color: color,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress,
              backgroundColor: Colors.white.withValues(alpha: 0.1),
              valueColor: AlwaysStoppedAnimation(color),
              minHeight: 6,
            ),
          ),
        ],
      ),
    );
  }

  Widget _photoArea() {
    final photo = c.currentPhoto;
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        color: Colors.black.withValues(alpha: 0.2),
      ),
      clipBehavior: Clip.antiAlias,
      child: photo == null
          ? const Center(child: CircularProgressIndicator(color: Colors.white))
          : Image.network(
              '$apiBase${photo.url}',
              fit: BoxFit.cover,
              width: double.infinity,
              errorBuilder: (context, error, stack) => const Center(
                child: Icon(
                  Icons.broken_image,
                  color: Colors.white54,
                  size: 64,
                ),
              ),
              loadingBuilder: (context, child, progress) => progress == null
                  ? child
                  : const Center(
                      child: CircularProgressIndicator(color: Colors.white),
                    ),
            ),
    );
  }

  Widget _resultBanner() {
    final correct = (c.lastPointsEarned ?? 0) > 0;
    final ownerId = c.revealedOwnerId;
    String ownerName = 'someone';
    for (final p in c.players) {
      if (p.id == ownerId) ownerName = p.name;
    }
    return AnimatedBuilder(
      animation: _shakeAnimation,
      builder: (context, child) {
        final shake = correct ? 0.0 : sin(_shakeAnimation.value * 3 * pi) * 8;
        return Transform.translate(offset: Offset(shake, 0), child: child);
      },
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: correct
              ? Colors.greenAccent.withValues(alpha: 0.15)
              : const Color(0xFFE94560).withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: correct
                ? Colors.greenAccent.withValues(alpha: 0.4)
                : const Color(0xFFE94560).withValues(alpha: 0.4),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              correct ? Icons.check_circle : Icons.cancel,
              color: correct ? Colors.greenAccent : const Color(0xFFE94560),
              size: 28,
            ),
            const SizedBox(width: 10),
            Flexible(
              child: Text(
                correct
                    ? 'Correct! +${c.lastPointsEarned} points'
                    : "It was $ownerName's photo",
                style: TextStyle(
                  color: correct ? Colors.greenAccent : const Color(0xFFE94560),
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _guessButtons() {
    // You guess who took the photo — everyone except yourself is a candidate.
    final candidates = c.players.where((p) => p.id != c.myPlayerId).toList();
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Wrap(
        spacing: 10,
        runSpacing: 10,
        alignment: WrapAlignment.center,
        children: candidates.map((player) {
          final disabled = c.hasGuessedThisRound || _timeExpired;
          final isSelected =
              c.hasGuessedThisRound && player.id == _myGuessedPlayerId;
          return GestureDetector(
            onTap: disabled ? null : () => _guess(player),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
              decoration: BoxDecoration(
                color: player.color.withValues(
                  alpha: isSelected ? 0.35 : (disabled ? 0.05 : 0.15),
                ),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: player.color.withValues(alpha: isSelected ? 1.0 : 0.3),
                  width: isSelected ? 2 : 1,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(player.avatar, color: player.color, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    player.name,
                    style: TextStyle(
                      color: Colors.white.withValues(
                        alpha: isSelected ? 1.0 : 0.9,
                      ),
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (isSelected) ...[
                    const SizedBox(width: 6),
                    Icon(Icons.check_circle, color: player.color, size: 16),
                  ],
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
