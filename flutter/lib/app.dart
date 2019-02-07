import 'package:bikebuds/bikebuds_util.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/main_screen.dart';
import 'package:flutter/material.dart';

void main() => runApp(App());

class App extends StatefulWidget {
  @override
  _AppState createState() => _AppState();
}

class _AppState extends State<App> {
  FirebaseState firebase;
  BikebudsState bikebuds;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: 'Bikebuds',
        theme: ThemeData(
          primaryColor: Color(0xFF03dac6),
          accentColor: Color(0xFFff4081),
        ),
        home: MainScreen(onSignedIn: _handleSignedIn));
  }

  _handleSignedIn(FirebaseState firebase, BikebudsState bikebuds,
      FirebaseSignInState signedInState) {
    print('App._handleSignedIn: $firebase $signedInState');
    this.firebase = firebase;
    this.bikebuds = bikebuds;

    bikebuds.registerClient();
    firebase.registerMessaging();
  }
}
