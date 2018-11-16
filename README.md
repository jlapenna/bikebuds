# Bikebuds

This is not an officially supported Google product.

## Setup

From the root directory:

  1. ./setup_dev.sh  # Installs pre-res
  2. Ensure you have the proper service keys in private/service_keys
  3. ./setup_env.sh  # Sets up 

## Running Locally

  1. ./gae/local.sh

You should be able to visit localhost:8080 to see the frontend.

## API Updates

If you add a new API method (or you're starting android dev), be sure to call
update_api:

```
./gae/update_api.sh local
```

### Local android development

Build a client jar (do this once or when changing the api) and set-up port
forwards (do this every time you plug in your device)..

  1. ./gae/update_api.sh local
  2. ./android/local.sh
  3. Launch your APK.

## API Updates

If you add a new API method, be sure to call update_api.

./gae/update_api.sh local
