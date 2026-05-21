import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import '../models/player.dart';
import '../models/mock_photos.dart';
import 'results_screen.dart';

class GameScreen extends StatefulWidget {
  const GameScreen({super.key});

  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> with TickerProviderStateMixin {
  static const int totalRounds = 5;
  static const int roundDurationSeconds = 10;

  int _currentRound = 0;
  int _timeLeft = roundDurationSeconds;
  Timer? _countdownTimer;
  bool _hasGuessed = false;
  String? _selectedPlayer;
  bool _showResult = false;
  bool _guessCorrect = false;

  late AnimationController _zoomController;
  late Animation<double> _zoomAnimation;
  late AnimationController _shakeController;
  late Animation<double> _shakeAnimation;

  late List<MockPhoto> _roundPhotos;

  @override
  void initState() {
    super.initState();
    // Shuffle and pick photos for this game
    _roundPhotos = List.of(mockPhotos)..shuffle(Random());

    _zoomController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: roundDurationSeconds),
    );
    _zoomAnimation = Tween<double>(begin: 4.0, end: 1.0).animate(
      CurvedAnimation(parent: _zoomController, curve: Curves.easeOut),
    );

    _shakeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    _shakeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _shakeController, curve: Curves.elasticIn),
    );

    _startRound();
  }

  @override
  void dispose() {
    _countdownTimer?.cancel();
    _zoomController.dispose();
    _shakeController.dispose();
    super.dispose();
  }

  MockPhoto get _currentPhoto =>
      _roundPhotos[_currentRound % _roundPhotos.length];

  void _startRound() {
    setState(() {
      _timeLeft = roundDurationSeconds;
      _hasGuessed = false;
      _selectedPlayer = null;
      _showResult = false;
    });

    _zoomController.reset();
    _zoomController.forward();

    _countdownTimer?.cancel();
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_timeLeft <= 1) {
        timer.cancel();
        if (!_hasGuessed) {
          _onTimeUp();
        }
      } else {
        setState(() => _timeLeft--);
      }
    });
  }

  void _onTimeUp() {
    setState(() {
      _hasGuessed = true;
      _showResult = true;
      _guessCorrect = false;
    });
    _shakeController.forward(from: 0);
    Future.delayed(const Duration(seconds: 2), _advanceRound);
  }

  void _onGuess(String playerName) {
    if (_hasGuessed) return;
    _countdownTimer?.cancel();

    final correct = playerName == _currentPhoto.ownerName;
    if (correct) {
      // Award points based on time remaining
      final pointsEarned = (_timeLeft * 100);
      mockPlayers.firstWhere((p) => p.name == 'You').score += pointsEarned;
    }

    setState(() {
      _selectedPlayer = playerName;
      _hasGuessed = true;
      _showResult = true;
      _guessCorrect = correct;
    });

    if (!correct) {
      _shakeController.forward(from: 0);
    }

    Future.delayed(const Duration(seconds: 2), _advanceRound);
  }

  void _advanceRound() {
    if (_currentRound >= totalRounds - 1) {
      // Assign random scores to other players for the mock
      final rng = Random();
      for (var p in mockPlayers) {
        if (p.name != 'You') {
          p.score = rng.nextInt(3000) + 500;
        }
      }
      Navigator.of(context).pushReplacement(
        PageRouteBuilder(
          pageBuilder: (_, __, ___) => const ResultsScreen(),
          transitionsBuilder: (_, animation, __, child) {
            return FadeTransition(opacity: animation, child: child);
          },
          transitionDuration: const Duration(milliseconds: 500),
        ),
      );
    } else {
      setState(() => _currentRound++);
      _startRound();
    }
  }

  @override
  Widget build(BuildContext context) {
    final photo = _currentPhoto;

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
              _buildTopBar(),
              const SizedBox(height: 8),
              _buildTimerBar(),
              const SizedBox(height: 16),
              // Photo area
              Expanded(child: _buildPhotoArea(photo)),
              const SizedBox(height: 16),
              // Result banner
              if (_showResult) _buildResultBanner(photo),
              // Player guess buttons
              if (!_showResult) _buildGuessButtons(),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTopBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Round indicator
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              'Round ${_currentRound + 1}/$totalRounds',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          // Score
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
                  '${mockPlayers.firstWhere((p) => p.name == "You").score}',
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

  Widget _buildTimerBar() {
    final progress = _timeLeft / roundDurationSeconds;
    final timerColor = _timeLeft <= 3
        ? const Color(0xFFE94560)
        : const Color(0xFF4ECDC4);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.timer, color: timerColor, size: 20),
              const SizedBox(width: 6),
              Text(
                '$_timeLeft',
                style: TextStyle(
                  color: timerColor,
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
              valueColor: AlwaysStoppedAnimation(timerColor),
              minHeight: 6,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPhotoArea(MockPhoto photo) {
    return AnimatedBuilder(
      animation: _zoomAnimation,
      builder: (context, child) {
        return ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 24),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: photo.dominantColor.withValues(alpha: 0.3),
                  blurRadius: 30,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: Transform.scale(
                scale: _zoomAnimation.value,
                child: Container(
                  decoration: BoxDecoration(
                    gradient: RadialGradient(
                      colors: [
                        photo.dominantColor,
                        photo.dominantColor.withValues(alpha: 0.6),
                        const Color(0xFF1A1A2E),
                      ],
                      stops: const [0.0, 0.5, 1.0],
                    ),
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          photo.icon,
                          size: 80,
                          color: Colors.white.withValues(alpha: 0.9),
                        ),
                        const SizedBox(height: 12),
                        if (_zoomAnimation.value < 2.0)
                          Text(
                            photo.label,
                            style: TextStyle(
                              color: Colors.white.withValues(alpha: 0.7),
                              fontSize: 16,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildResultBanner(MockPhoto photo) {
    return AnimatedBuilder(
      animation: _shakeAnimation,
      builder: (context, child) {
        final shake = _guessCorrect ? 0.0 : sin(_shakeAnimation.value * 3 * pi) * 8;
        return Transform.translate(
          offset: Offset(shake, 0),
          child: child,
        );
      },
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: _guessCorrect
              ? Colors.greenAccent.withValues(alpha: 0.15)
              : const Color(0xFFE94560).withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: _guessCorrect
                ? Colors.greenAccent.withValues(alpha: 0.4)
                : const Color(0xFFE94560).withValues(alpha: 0.4),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _guessCorrect ? Icons.check_circle : Icons.cancel,
              color: _guessCorrect ? Colors.greenAccent : const Color(0xFFE94560),
              size: 28,
            ),
            const SizedBox(width: 10),
            Flexible(
              child: Text(
                _guessCorrect
                    ? 'Correct! +${_timeLeft * 100} points'
                    : 'Wrong! It was ${photo.ownerName}\'s photo',
                style: TextStyle(
                  color: _guessCorrect
                      ? Colors.greenAccent
                      : const Color(0xFFE94560),
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

  Widget _buildGuessButtons() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Wrap(
        spacing: 10,
        runSpacing: 10,
        alignment: WrapAlignment.center,
        children: mockPlayers.map((player) {
          final isSelected = _selectedPlayer == player.name;
          return GestureDetector(
            onTap: () => _onGuess(player.name),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(
                horizontal: 18,
                vertical: 12,
              ),
              decoration: BoxDecoration(
                color: isSelected
                    ? player.color.withValues(alpha: 0.4)
                    : player.color.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isSelected
                      ? player.color
                      : player.color.withValues(alpha: 0.3),
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
                      color: Colors.white.withValues(alpha: 0.9),
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
