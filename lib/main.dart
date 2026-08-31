import 'package:flutter/material.dart';

import 'config.dart';
import 'screens/home_screen.dart';
import 'theme/app_theme.dart';
import 'ui/gradient_scaffold.dart';

void main() {
  runApp(const PhotoBlameApp());
}

class PhotoBlameApp extends StatelessWidget {
  const PhotoBlameApp({super.key});

  @override
  Widget build(BuildContext context) {
    final problem = apiBaseProblem;
    return MaterialApp(
      title: 'Photo Blame',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      // A build with no usable backend can't do anything at all, so it says so
      // on the first screen instead of letting every action fail one spinner
      // at a time — which is what a TestFlight tester would otherwise report.
      home: problem == null
          ? const HomeScreen()
          : _MisconfiguredScreen(problem: problem),
    );
  }
}

class _MisconfiguredScreen extends StatelessWidget {
  final String problem;

  const _MisconfiguredScreen({required this.problem});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return GradientScaffold(
      gradient: AppGradient.diagonal,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.settings_ethernet, size: 56, color: colors.brand),
              const SizedBox(height: 20),
              Text(
                'Not configured',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              Text(
                problem,
                textAlign: TextAlign.center,
                style: TextStyle(color: colors.onSurfaceMuted, fontSize: 15),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
