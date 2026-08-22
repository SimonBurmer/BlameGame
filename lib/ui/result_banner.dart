import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// The correct/incorrect banner shown under the photo.
///
/// One widget for both the instant "you guessed" feedback and the round
/// reveal: they were separate near-identical copies, and only one of them had
/// the [Flexible] that keeps a long message from overflowing.
class ResultBanner extends StatelessWidget {
  final bool correct;
  final String message;

  const ResultBanner({
    super.key,
    required this.correct,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final color = correct ? colors.correct : colors.wrong;
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            correct ? Icons.check_circle : Icons.cancel,
            color: color,
            size: 28,
          ),
          const SizedBox(width: 10),
          Flexible(
            child: Text(
              message,
              style: TextStyle(
                color: color,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
