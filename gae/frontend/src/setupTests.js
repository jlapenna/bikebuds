// https://create-react-app.dev/docs/running-tests#on-your-own-environment
import '@testing-library/jest-dom/extend-expect';

// Make testing more like production, by default.
import { config } from './config';

// For config.json overrides.
var originalConfig = {};

beforeEach(() => {
  // For config.json overrides.
  Object.assign(originalConfig, config);
  config.isDev = false;
  config.fakeUser = '';
});

afterEach(() => {
  // For config.json overrides.
  for (let [key, value] of Object.entries(originalConfig)) {
    config[key] = value;
  }
});
