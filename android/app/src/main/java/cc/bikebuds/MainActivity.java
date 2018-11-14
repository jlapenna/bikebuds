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

package cc.bikebuds;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.browser.customtabs.CustomTabsIntent;
import androidx.core.content.ContextCompat;

import com.firebase.ui.auth.AuthUI;
import com.firebase.ui.auth.IdpResponse;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.android.material.button.MaterialButton;
import com.google.api.client.http.HttpHeaders;
import com.google.api.client.http.HttpRequest;
import com.google.api.client.http.HttpRequestInitializer;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.auth.GetTokenResult;
import com.squareup.picasso.Picasso;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;

import cc.bikebuds.api.bikebuds.Bikebuds;
import cc.bikebuds.api.bikebuds.model.MainProfileResponse;
import cc.bikebuds.api.bikebuds.model.MainRequest;
import jp.wasabeef.picasso.transformations.CropCircleTransformation;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "Bikebuds";

    private static final int RC_SIGN_IN = 100;
    private EditText editText;
    private TextView nameTextView;
    private ImageView avatarImageView;
    private MaterialButton signOutButton;
    private MaterialButton connectServicesButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        avatarImageView = findViewById(R.id.avatarImageView);
        nameTextView = findViewById(R.id.displayNameTextView);
        signOutButton = findViewById(R.id.signOutButton);
        signOutButton.setOnClickListener(v -> {
            Intent intent = getIntent();
            FirebaseAuth.getInstance().signOut();
            finish();
            startActivity(intent);
        });
        connectServicesButton = findViewById(R.id.connectServicesButton);
        connectServicesButton.setOnClickListener(v -> {
            new CustomTabsIntent.Builder()
                    .setToolbarColor(ContextCompat.getColor(this, R.color.colorPrimary))
                    .setSecondaryToolbarColor(
                            ContextCompat.getColor(this, R.color.colorSecondary))
                    .build()
                    .launchUrl(this,
                            Uri.withAppendedPath(
                                    Uri.parse(getResources().getString(R.string.backend_url)),
                                    "signup"));
        });

        FirebaseAuth auth = FirebaseAuth.getInstance();
        if (auth.getCurrentUser() != null) {
            finishSignIn(auth.getCurrentUser(), null /* response */);
        } else {
            startSignIn();
        }
    }

    private void finishSignIn(FirebaseUser user, IdpResponse response) {
        Log.d(TAG, "finishSignIn: " + user.getDisplayName());
        nameTextView.setText(user.getDisplayName());
        Picasso.get().load(user.getPhotoUrl())
                .transform(new CropCircleTransformation())
                .into(avatarImageView);
        final Task<GetTokenResult> tokenTask = user.getIdToken(true);
        tokenTask.addOnCompleteListener(new OnCompleteListener<GetTokenResult>() {
            @Override
            public void onComplete(@NonNull final Task<GetTokenResult> task) {
                String token = task.isSuccessful() ? task.getResult().getToken() : null;
                AuthenticatedHttpRequestInitializer httpRequestInitializer =
                        token != null ? new AuthenticatedHttpRequestInitializer(token) : null;
                Bikebuds.Builder builder = new Bikebuds.Builder(new NetHttpTransport(),
                        JacksonFactory.getDefaultInstance(), httpRequestInitializer)
                        .setApplicationName("Bikebuds")
                        .setRootUrl(getResources().getString(R.string.api_url) + "/_ah/api/");
                asyncGetUser(builder.build());
            }
        });
    }

    private void asyncGetUser(final Bikebuds bikebuds) {
        CompletableFuture.runAsync(() -> {
            try {
                final Bikebuds.GetProfile request = bikebuds.getProfile(new MainRequest());
                Log.d(TAG, "GetUser Request: " + request);
                MainProfileResponse response = request.execute();
                Log.d(TAG, "GetUser Response content: " + response.getCreated());
                //  editText.setText(response.getCreated().toString());
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
