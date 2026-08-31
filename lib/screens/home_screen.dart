import 'package:flutter/material.dart';

import '../state/game_controller.dart';
import '../theme/app_theme.dart';
import '../ui/app_buttons.dart';
import '../ui/error_text.dart';
import '../ui/gradient_scaffold.dart';
import 'lobby_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _nameController = TextEditingController();
  final _codeController = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _nameController.dispose();
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _createRoom() => _run((c) => c.createAndHost(_name));

  Future<void> _joinRoom() {
    final code = _codeController.text.trim().toUpperCase();
    if (code.isEmpty) {
      setState(() => _error = 'Enter a game code to join');
      return Future.value();
    }
    return _run((c) => c.joinByCode(code, _name));
  }

  String get _name {
    final n = _nameController.text.trim();
    return n.isEmpty ? 'Player' : n;
  }

  /// Runs an async action that sets up a GameController, then navigates to the
  /// lobby. Shows a spinner and surfaces errors.
  Future<void> _run(Future<void> Function(GameController) action) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    final controller = GameController();
    try {
      await action(controller);
      if (!mounted) {
        controller.dispose();
        return;
      }
      // Home created it, so Home tears it down: awaiting the push means this
      // runs whenever the game flow unwinds back here, however it unwinds.
      // Without it every game leaks a live WebSocket and an http.Client.
      await Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => LobbyScreen(controller: controller)),
      );
      controller.dispose();
    } catch (e) {
      controller.dispose();
      if (mounted) setState(() => _error = friendlyError(e));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final text = Theme.of(context).textTheme;
    return GradientScaffold(
      gradient: AppGradient.diagonal,
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(28),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 20),
              Image.asset('assets/branding/logo_mark.png',
                  width: 96, height: 96),
              const SizedBox(height: 16),
              Text(
                'PHOTO\nBLAME',
                textAlign: TextAlign.center,
                style: text.displayLarge,
              ),
              const SizedBox(height: 8),
              Text(
                'Guess whose photo it is!',
                style: TextStyle(fontSize: 15, color: colors.onSurfaceMuted),
              ),
              const SizedBox(height: 36),
              _textField(_nameController, 'Your name', Icons.person),
              const SizedBox(height: 28),
              if (_error != null) ...[
                Text(
                  _error!,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: colors.brand),
                ),
                const SizedBox(height: 12),
              ],
              if (_busy)
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: CircularProgressIndicator(color: colors.brand),
                )
              else ...[
                PrimaryButton(
                  label: 'CREATE GAME',
                  icon: Icons.add,
                  onPressed: _createRoom,
                  height: 56,
                  radius: 16,
                ),
                const SizedBox(height: 24),
                Row(
                  children: [
                    Expanded(
                        child: Divider(
                            color: colors.onSurfaceStrong
                                .withValues(alpha: 0.2))),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      child: Text('OR JOIN',
                          style: TextStyle(
                              color: colors.onSurfaceStrong
                                  .withValues(alpha: 0.4),
                              fontSize: 12,
                              letterSpacing: 2)),
                    ),
                    Expanded(
                        child: Divider(
                            color: colors.onSurfaceStrong
                                .withValues(alpha: 0.2))),
                  ],
                ),
                const SizedBox(height: 20),
                _textField(_codeController, 'Game code', Icons.tag,
                    caps: true),
                const SizedBox(height: 16),
                SecondaryButton(
                  label: 'JOIN GAME',
                  icon: Icons.login,
                  onPressed: _joinRoom,
                  height: 52,
                  radius: 16,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _textField(
    TextEditingController controller,
    String hint,
    IconData icon, {
    bool caps = false,
  }) {
    final white = context.colors.onSurfaceStrong;
    return TextField(
      controller: controller,
      textCapitalization:
          caps ? TextCapitalization.characters : TextCapitalization.words,
      style: TextStyle(color: white),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: TextStyle(color: white.withValues(alpha: 0.4)),
        prefixIcon: Icon(icon, color: white.withValues(alpha: 0.6)),
        filled: true,
        fillColor: white.withValues(alpha: 0.08),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
      ),
    );
  }
}
