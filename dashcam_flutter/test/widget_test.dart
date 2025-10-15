// Basic Flutter widget test for Dashcam Manager

import 'package:flutter_test/flutter_test.dart';

import 'package:dashcam_flutter/main.dart';

void main() {
  testWidgets('App launches successfully', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const DashcamApp());

    // Verify that the main screen loads
    expect(find.text('Dashcam Manager'), findsOneWidget);
    expect(find.text('Not connected'), findsOneWidget);
    expect(find.text('Connect'), findsOneWidget);
  });
}
