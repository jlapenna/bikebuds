#Flutter Wrapper
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.**  { *; }
-keep class io.flutter.plugins.**  { *; }

# Eg: Warning: com.google.common.base.Converter: can't find referenced class com.google.errorprone.annotations.CanIgnoreReturnValue
# Removed 650 warnings...
-dontwarn com.google.errorprone.annotations.**

# Removed 30 warnings...
-dontwarn com.google.j2objc.annotations.*

# Removed 6 warnings...
-dontwarn java.lang.ClassValue

# Removed 1 warning...
-dontwarn org.codehaus.mojo.animal_sniffer.IgnoreJRERequirement
