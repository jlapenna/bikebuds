#!/bin/bash
#
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Dependencies for development, in order to start a dev server, for example.

function main() {
  local repo_path="$(get_repo_path)";

  mkdir generated >/dev/null 2>&1;
  pushd generated
  git clone https://github.com/dart-lang/discoveryapis_generator.git
  pushd discoveryapis_generator
  pub get
  patch --ignore-whitespace lib/src/dart_resources.dart << 'INLINE_DIFF'
diff --git a/lib/src/dart_resources.dart b/lib/src/dart_resources.dart
index 9ed04ae..0d180f3 100644
--- a/lib/src/dart_resources.dart
+++ b/lib/src/dart_resources.dart
@@ -218,20 +218,15 @@ class DartResourceMethod {
     validatePathParam(MethodParameter param) {
       templateVars[param.jsonName] = param.name;
 
-      if (param.required) {
-        if (param.type is UnnamedArrayType) {
-          params.writeln(
-              '    if (${param.name} == null || ${param.name}.isEmpty) {');
-        } else {
-          params.writeln('    if (${param.name} == null) {');
-        }
-        params.writeln('      throw new ${imports.core.ref()}ArgumentError'
-            '("Parameter ${param.name} is required.");');
-        params.writeln('    }');
+      if (param.type is UnnamedArrayType) {
+        params.writeln(
+            '    if (${param.name} == null || ${param.name}.isEmpty) {');
       } else {
-        // Is this an error?
-        throw 'non-required path parameter';
+        params.writeln('    if (${param.name} == null) {');
       }
+      params.writeln('      throw new ${imports.core.ref()}ArgumentError'
+          '("Parameter ${param.name} is required.");');
+      params.writeln('    }');
     }
 
     encodeQueryParam(MethodParameter param) {
INLINE_DIFF
  local patch_result="$?";
  if [[ "$patch_result" == "0" ]]; then
    rm lib/src/dart_resources.dart.orig
  else 
    echo "Unable to patch dart_resources.dart. See README.md";
  fi
  popd
  popd

}

main "$@"
