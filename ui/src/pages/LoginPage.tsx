import { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Tab,
  Tabs,
  Alert,
} from '@mui/material';
import { Check, Close } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../api';

function RequirementItem({ met, label }: { met: boolean; label: string }) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      {met ? (
        <Check sx={{ fontSize: 16, color: 'success.main' }} />
      ) : (
        <Close sx={{ fontSize: 16, color: 'text.disabled' }} />
      )}
      <Typography
        variant="caption"
        sx={{ color: met ? 'success.main' : 'text.secondary' }}
      >
        {label}
      </Typography>
    </Box>
  );
}

function validateEmail(email: string): boolean {
  return /^.+@.+\..{2,}$/.test(email);
}

export default function LoginPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [signupForm, setSignupForm] = useState({ email: '', password: '', confirmPassword: '', firstName: '', lastName: '' });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!loginForm.email || !loginForm.password) {
      setError('Email and password are required');
      return;
    }

    if (!validateEmail(loginForm.email)) {
      setError('Please enter a valid email address');
      return;
    }

    try {
      const response = await apiRequest('/users/login', {
        method: 'POST',
        body: JSON.stringify(loginForm),
      });

      if (!response.ok) {
        const data = await response.json();
        setError(data.error || 'Login failed');
        return;
      }

      const data = await response.json();
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      navigate('/');
    } catch {
      setError('Unexpected error occurred during login, please try again later!');
    }
  };

  // Password requirements checks
  const pw = signupForm.password;
  const pwRequirements = {
    length: pw.length >= 8,
    uppercase: /[A-Z]/.test(pw),
    lowercase: /[a-z]/.test(pw),
    number: /[0-9]/.test(pw),
    special: /[!@#$%^&*()_+\-=\[\]{}|;:',.<>?/~`]/.test(pw),
  };
  const allPwMet = Object.values(pwRequirements).every(Boolean);
  const emailValid = validateEmail(signupForm.email);
  const passwordsMatch = signupForm.password === signupForm.confirmPassword && signupForm.confirmPassword.length > 0;

  // Name requirements
  const validateName = (name: string) => ({
    length: name.trim().length >= 3,
    lettersOnly: /^[a-zA-Z\s]*$/.test(name) && name.trim().length > 0,
  });
  const firstNameReqs = validateName(signupForm.firstName);
  const lastNameReqs = validateName(signupForm.lastName);
  const nameValid = firstNameReqs.length && firstNameReqs.lettersOnly && lastNameReqs.length && lastNameReqs.lettersOnly;

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!signupForm.firstName || !signupForm.lastName || !signupForm.email || !signupForm.password || !signupForm.confirmPassword) {
      setError('All fields are required');
      return;
    }

    if (!nameValid) {
      setError('First and last name must be at least 3 characters and contain only letters');
      return;
    }

    if (!emailValid) {
      setError('Please enter a valid email address');
      return;
    }

    if (!allPwMet) {
      setError('Password does not meet all requirements');
      return;
    }

    if (!passwordsMatch) {
      setError('Passwords do not match');
      return;
    }

    try {
      const response = await apiRequest('/users/signup', {
        method: 'POST',
        body: JSON.stringify({
          email: signupForm.email,
          password: signupForm.password,
          name: `${signupForm.firstName.trim()} ${signupForm.lastName.trim()}`,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        setError(data.error || 'Signup failed');
        return;
      }

      // Signup successful — switch to login tab so user can sign in
      setSignupForm({ email: '', password: '', confirmPassword: '', firstName: '', lastName: '' });
      setTab(0);
      setLoginForm({ email: signupForm.email, password: '' });
      setError('');
      setSuccess('Account created successfully. Please log in.');
    } catch {
      setError('Unable to connect to server');
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Room Booker
        </Typography>

        <Tabs value={tab} onChange={(_, v) => {setTab(v); setError(''); setSuccess('');}} centered sx={{ mb: 3 }}>
          <Tab label="Login" />
          <Tab label="Sign Up" />
        </Tabs>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {tab === 0 && (
          <Box component="form" onSubmit={handleLogin} sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 400, mx: 'auto' }}>
            <TextField
              label="Email"
              required
              value={loginForm.email}
              onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
            />
            <TextField
              label="Password"
              type="password"
              required
              value={loginForm.password}
              onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
            />
            <Button type="submit" variant="contained" size="large">
              Login
            </Button>
          </Box>
        )}

        {tab === 1 && (
          <Box sx={{ display: 'flex', gap: 4 }}>
            {/* Sign up form */}
            <Box component="form" onSubmit={handleSignup} sx={{ display: 'flex', flexDirection: 'column', gap: 2, flex: 1 }}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  label="First Name"
                  required
                  value={signupForm.firstName}
                  onChange={(e) => setSignupForm({ ...signupForm, firstName: e.target.value })}
                  sx={{ flex: 1 }}
                />
                <TextField
                  label="Last Name"
                  required
                  value={signupForm.lastName}
                  onChange={(e) => setSignupForm({ ...signupForm, lastName: e.target.value })}
                  sx={{ flex: 1 }}
                />
              </Box>
              <TextField
                label="Email"
                required
                value={signupForm.email}
                onChange={(e) => setSignupForm({ ...signupForm, email: e.target.value })}
                error={signupForm.email.length > 0 && !emailValid}
                helperText={signupForm.email.length > 0 && !emailValid ? 'Enter a valid email (e.g. user@example.com)' : ''}
              />
              <TextField
                label="Password"
                type="password"
                required
                value={signupForm.password}
                onChange={(e) => setSignupForm({ ...signupForm, password: e.target.value })}
              />
              <TextField
                label="Confirm Password"
                type="password"
                required
                value={signupForm.confirmPassword}
                onChange={(e) => setSignupForm({ ...signupForm, confirmPassword: e.target.value })}
                error={signupForm.confirmPassword.length > 0 && !passwordsMatch}
                helperText={signupForm.confirmPassword.length > 0 && !passwordsMatch ? 'Passwords do not match' : ''}
              />
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={!nameValid || !allPwMet || !emailValid || !passwordsMatch}
              >
                Sign Up
              </Button>
            </Box>

            {/* Requirements panel */}
            <Box sx={{ minWidth: 220, pt: 1 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Name Requirements
              </Typography>
              <RequirementItem met={firstNameReqs.length} label="First name at least 3 characters" />
              <RequirementItem met={firstNameReqs.lettersOnly} label="First name letters only" />
              <RequirementItem met={lastNameReqs.length} label="Last name at least 3 characters" />
              <RequirementItem met={lastNameReqs.lettersOnly} label="Last name letters only" />

              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Email Requirements
              </Typography>
              <RequirementItem met={emailValid} label="Valid email format (user@domain.xx)" />

              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Password Requirements
              </Typography>
              <RequirementItem met={pwRequirements.length} label="At least 8 characters" />
              <RequirementItem met={pwRequirements.uppercase} label="One uppercase letter" />
              <RequirementItem met={pwRequirements.lowercase} label="One lowercase letter" />
              <RequirementItem met={pwRequirements.number} label="One number" />
              <RequirementItem met={pwRequirements.special} label="One special character" />

              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Confirmation
              </Typography>
              <RequirementItem met={passwordsMatch} label="Passwords match" />
            </Box>
          </Box>
        )}
      </Paper>
    </Container>
  );
}
