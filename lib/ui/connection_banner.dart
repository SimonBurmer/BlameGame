import 'package:flutter/material.dart';

import '../state/game_controller.dart';
import 'error_text.dart';

/// Shown when the live connection has dropped.
///
/// Events that fired while disconnected are gone, so reconnecting re-seeds
/// from the server snapshot. Without this a dropped socket leaves the player
/// staring at a frozen screen with no explanation and no way back in.
class ConnectionBanner extends StatefulWidget {
  final GameController controller;

  const ConnectionBanner({super.key, required this.controller});

  @override
  State<ConnectionBanner> createState() => _ConnectionBannerState();
}

class _ConnectionBannerState extends State<ConnectionBanner> {
  bool _retrying = false;

  Future<void> _retry() async {
    setState(() => _retrying = true);
    try {
      await widget.controller.reconnect();
    } on Exception catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Still offline: ${friendlyError(e)}')),
      );
    } finally {
      if (mounted) setState(() => _retrying = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.controller.connectionError == null) {
      return const SizedBox.shrink();
    }
    final scheme = Theme.of(context).colorScheme;
    return Material(
      color: scheme.errorContainer,
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: Row(
            children: [
              Icon(Icons.cloud_off, size: 20, color: scheme.onErrorContainer),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Connection lost',
                  style: TextStyle(
                    color: scheme.onErrorContainer,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              if (_retrying)
                SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: scheme.onErrorContainer,
                  ),
                )
              else
                TextButton(
                  onPressed: _retry,
                  child: Text(
                    'RETRY',
                    style: TextStyle(color: scheme.onErrorContainer),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
