import 'dart:async';

import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';

void main() => runApp(MyApp());

final GoogleSignIn _googleSignIn = GoogleSignIn();
final FirebaseAuth _auth = FirebaseAuth.instance;

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bikebuds',
      theme: ThemeData(
        primaryColor: Color(0xFF03dac6),
        accentColor: Color(0xFFff4081),
      ),
      home: MyHomePage(title: 'Bikebuds'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  StreamSubscription<FirebaseUser> _listener;
  bool _loading = true;
  FirebaseUser _currentUser;

  @override
  void initState() {
    super.initState();
    _initListener();
    _signIn();
  }

  @override
  void dispose() {
    super.dispose();
    _listener?.cancel();
  }

  void _signIn() async {
    try {
      var googleUser = await _googleSignIn.signIn();
      var googleAuth = await googleUser.authentication;
      await _auth.signInWithGoogle(
          idToken: googleAuth.idToken, accessToken: googleAuth.accessToken);
      print("Completed signing in.");
    } catch (e) {
      print("Failed signing in.");
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  void _initListener() async {
    _listener = _auth.onAuthStateChanged.listen((FirebaseUser user) {
      print("Listener Event: " + user.toString());
      setState(() {
        _currentUser = user;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    String toDisplay = _loading
        ? "Signing in..."
        : (_currentUser == null
            ? "Sign in Failed"
            : (_currentUser?.displayName ?? _currentUser));
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            new Text(toDisplay),
          ],
        ),
      ),
    );
  }
}
