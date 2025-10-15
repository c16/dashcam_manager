import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/app_state.dart';
import 'services/preferences_service.dart';
import 'ui/screens/main_screen.dart';
import 'ui/screens/mobile_main_screen.dart';
import 'ui/widgets/responsive_layout.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final preferencesService = await PreferencesService.init();
  runApp(DashcamApp(preferencesService: preferencesService));
}

class DashcamApp extends StatelessWidget {
  final PreferencesService preferencesService;

  const DashcamApp({super.key, required this.preferencesService});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppState(preferencesService: preferencesService),
      child: MaterialApp(
        title: 'Dashcam Manager',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.light,
          ),
          useMaterial3: true,
        ),
        darkTheme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.dark,
          ),
          useMaterial3: true,
        ),
        themeMode: ThemeMode.system,
        home: const ResponsiveLayout(
          mobile: MobileMainScreen(),
          desktop: MainScreen(),
        ),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
