// Widget test for the home screen. Runs headless with `flutter test` — no
// emulator. It pumps the app and checks the home UI renders, without touching
// the network (we never tap Create/Join here).

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:flutter_application_1/main.dart';

void main() {
  testWidgets('Home screen renders title and actions', (tester) async {
    await tester.pumpWidget(const PhotoRouletteApp());

    expect(find.text('PHOTO\nROULETTE'), findsOneWidget);
    expect(find.text('CREATE GAME'), findsOneWidget);
    expect(find.text('JOIN GAME'), findsOneWidget);

    // Name and game-code fields are present.
    expect(find.byType(TextField), findsNWidgets(2));
  });
}
