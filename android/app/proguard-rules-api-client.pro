-keepclassmembers class * {
  @com.google.api.client.util.Key <fields>;
}

-keepattributes Signature,RuntimeVisibleAnnotations,AnnotationDefault

-dontwarn com.google.errorprone.annotations.**
-dontwarn com.google.api.client.googleapis.testing.**