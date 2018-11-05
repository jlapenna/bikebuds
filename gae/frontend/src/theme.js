import { createMuiTheme } from '@material-ui/core/styles';

export default createMuiTheme({
  typography: {
    useNextVariants: true,
  },
  palette: {
    primary: {
      main: '#03dac6',
    },
    secondary: {
      main: '#ff4081',
    }
  }
});
