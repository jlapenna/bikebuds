/*
 * Copyright 2018 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

package com.joelapenna.bikebuds;

import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;

import com.appspot.backend_dot_bikebuds_app.bikebuds.Bikebuds;
import com.appspot.backend_dot_bikebuds_app.bikebuds.model.ApiBikebudsResponse;
import com.firebase.ui.auth.AuthUI;
import com.firebase.ui.auth.IdpResponse;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.api.client.http.HttpHeaders;
import com.google.api.client.http.HttpRequest;
import com.google.api.client.http.HttpRequestInitializer;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.auth.GetTokenResult;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "Bikebuds";

    private static final int RC_SIGN_IN = 100;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        FirebaseAuth auth = FirebaseAuth.getInstance();
        if (auth.getCurrentUser() != null) {
            finishSignIn(auth.getCurrentUser(), null /* response */);
        } else {
            startSignIn();
        }
    }

    private void finishSignIn(FirebaseUser user, IdpResponse response) {
        Log.d(TAG, "finishSignIn: " + user.getDisplayName());
        final Task<GetTokenResult> tokenTask = user.getIdToken(true);
        tokenTask.addOnCompleteListener(new OnCompleteListener<GetTokenResult>() {
            @Override
            public void onComplete(@NonNull final Task<GetTokenResult> task) {
                String token = task.isSuccessful() ? task.getResult().getToken() : null;
                AuthenticatedHttpRequestInitializer httpRequestInitializer =
                        token != null ? new AuthenticatedHttpRequestInitializer(token) : null;
                Bikebuds.Builder builder = new Bikebuds.Builder(new NetHttpTransport(),
                        JacksonFactory.getDefaultInstance(), httpRequestInitializer)
                        .setRootUrl(getResources().getString(R.string.backend_url) + "/_ah/api/");
                asyncGetUser(builder.build());
            }
        });
    }

    private void asyncGetUser(final Bikebuds bikebuds) {
        CompletableFuture.runAsync(() -> {
            try {
                final Bikebuds.GetUser request = bikebuds.getUser();
                Log.d(TAG, "GetUser Request: " + request);
                ApiBikebudsResponse response = request.execute();
                Log.d(TAG, "GetUser Response content: " + response.getContent());
            } catch (IOException e) {
                Log.d(TAG, "GetUser Unable to execute: ", e);
            }
        });
    }

    private void startSignIn() {
        Log.d(TAG, "startSignIn");
        List<AuthUI.IdpConfig> providers = Arrays.asList(
                new AuthUI.IdpConfig.GoogleBuilder().build());

        // Create and launch sign-in intent
        startActivityForResult(
                AuthUI.getInstance()
                        .createSignInIntentBuilder()
                        .setAvailableProviders(providers)
                        .build(),
                RC_SIGN_IN);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        Log.d(TAG, "onActivityResult: " + requestCode + " " + resultCode + " " + data);

        if (requestCode == RC_SIGN_IN) {
            IdpResponse response = IdpResponse.fromResultIntent(data);

            if (resultCode == RESULT_OK) {
                // Successfully signed in
                FirebaseUser user = FirebaseAuth.getInstance().getCurrentUser();
                finishSignIn(user, response);
            } else {
                signInFailed(response);
            }
        }
    }

    private void signInFailed(IdpResponse resultCode) {
        Log.d(TAG, "signInFailed");
    }

    private static class AuthenticatedHttpRequestInitializer implements HttpRequestInitializer {
        private final String token;

        public AuthenticatedHttpRequestInitializer(String token) {
            this.token = token;
        }

        @Override
        public void initialize(HttpRequest request) throws IOException {
            HttpHeaders headers = request.getHeaders();
            if (headers == null) {
                headers = new HttpHeaders();
                request.setHeaders(headers);
            }
            headers.put("Authorization", Arrays.asList("Bearer " + token));
        }
    }
}
