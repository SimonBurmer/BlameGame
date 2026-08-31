import 'package:flutter/material.dart';

/// Shows a transient message on the nearest [ScaffoldMessenger].
///
/// Safe to call after an `await`: a screen that has since been popped simply
/// shows nothing, rather than throwing on a defunct element. Every screen used
/// to spell this out inline, and half of them forgot the guard.
void showSnack(BuildContext context, String message) {
  if (!context.mounted) return;
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
}
