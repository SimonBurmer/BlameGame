import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_application_1/models/game_models.dart';
import 'package:flutter_application_1/screens/lobby_screen.dart';

import 'support/fakes.dart';
import 'support/pump.dart';

void main() {
  testWidgets('shows the room code and everyone in it', (tester) async {
    final h = await harness();
    await pumpScreen(tester, LobbyScreen(controller: h.controller));

    expect(find.text('ABC12'), findsOneWidget);
    expect(find.text('Emma (you)'), findsOneWidget);
    expect(find.text('Jake'), findsOneWidget);
    expect(find.text('PLAYERS (2)'), findsOneWidget);
  });

  testWidgets('start is blocked until two people have added photos',
      (tester) async {
    final h = await harness();
    await pumpScreen(tester, LobbyScreen(controller: h.controller));

    // Two players, but nobody has uploaded.
    expect(find.text('NEED PHOTOS FROM 2+ PLAYERS'), findsOneWidget);
    expect(find.text('START GAME'), findsNothing);

    await h.emit(
      tester,
      PhotosUpdated([
        player(id: 'me', name: 'Emma', isHost: true, photoCount: 3),
        player(id: 'p2', name: 'Jake', photoCount: 1),
      ]),
    );

    expect(find.text('START GAME'), findsOneWidget);
  });

  testWidgets('one uploader is not enough', (tester) async {
    final h = await harness();
    await pumpScreen(tester, LobbyScreen(controller: h.controller));

    await h.emit(
      tester,
      PhotosUpdated([
        player(id: 'me', name: 'Emma', isHost: true, photoCount: 5),
        player(id: 'p2', name: 'Jake'),
      ]),
    );

    expect(find.text('NEED PHOTOS FROM 2+ PLAYERS'), findsOneWidget);
  });

  testWidgets('players show real readiness, not a decorative tick',
      (tester) async {
    final h = await harness();
    await pumpScreen(tester, LobbyScreen(controller: h.controller));

    // Jake has not uploaded: no green tick for him.
    expect(find.byIcon(Icons.check_circle), findsNothing);
    expect(find.byIcon(Icons.hourglass_empty), findsOneWidget);

    await h.emit(
      tester,
      PhotosUpdated([
        player(id: 'me', name: 'Emma', isHost: true, photoCount: 1),
        player(id: 'p2', name: 'Jake', photoCount: 1),
      ]),
    );

    expect(find.byIcon(Icons.check_circle), findsOneWidget);
    expect(find.byIcon(Icons.hourglass_empty), findsNothing);
  });

  testWidgets('a non-host sees no start button', (tester) async {
    final h = await harness(isHost: false);
    await pumpScreen(tester, LobbyScreen(controller: h.controller));

    expect(find.text('START GAME'), findsNothing);
    expect(find.text('NEED PHOTOS FROM 2+ PLAYERS'), findsNothing);
  });

  testWidgets('the back control is a labelled button, not a bare icon',
      (tester) async {
    final h = await harness();
    await pumpScreen(tester, LobbyScreen(controller: h.controller));

    final backButton = find.byTooltip('Back');
    expect(backButton, findsOneWidget);
    // A bare GestureDetector around an Icon announces nothing to a screen
    // reader and gives a 24x24 target.
    final semantics = tester.getSemantics(backButton);
    expect(semantics.flagsCollection.isButton, isTrue);
    expect(semantics.tooltip, 'Back');
    // Material's minimum tap target, supplied by IconButton's padded target.
    expect(semantics.rect.width, greaterThanOrEqualTo(48));
    expect(semantics.rect.height, greaterThanOrEqualTo(48));
  });

  testWidgets('a dropped connection is surfaced with a retry', (tester) async {
    final h = await harness();
    await pumpScreen(tester, LobbyScreen(controller: h.controller));
    expect(find.text('Connection lost'), findsNothing);

    h.socket.dropConnection();
    await tester.pump();
    await tester.pump();

    expect(find.text('Connection lost'), findsOneWidget);
    expect(find.text('RETRY'), findsOneWidget);
  });
}
