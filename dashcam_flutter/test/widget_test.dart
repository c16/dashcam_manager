// Basic Flutter widget test for Dashcam Manager

import 'package:flutter_test/flutter_test.dart';

import 'package:dashcam_flutter/main.dart';
import 'package:dashcam_flutter/services/preferences_service.dart';

void main() {
  testWidgets('App launches successfully', (WidgetTester tester) async {
    // Initialize preferences service for testing
    final preferencesService = await PreferencesService.init();

    // Build our app and trigger a frame.
    await tester.pumpWidget(DashcamApp(preferencesService: preferencesService));

    // Verify that the main screen loads
    expect(find.text('Dashcam Manager'), findsOneWidget);
    expect(find.text('Not connected'), findsOneWidget);
    expect(find.text('Connect'), findsOneWidget);
  });
}
