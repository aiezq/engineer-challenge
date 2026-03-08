import { gql } from '@apollo/client';

export const LOGIN_MUTATION = gql`
  mutation Authenticate($email: String!, $password: String!) {
    authenticate(input: {
      email: $email,
      password: $password
    }) {
      accessToken
      userId
    }
  }
`;

export const REGISTER_MUTATION = gql`
  mutation Register($email: String!, $password: String!) {
    register(input: {
      email: $email,
      password: $password
    }) {
      id
      email
    }
  }
`;

export const REQUEST_RESET_MUTATION = gql`
  mutation RequestPasswordReset($email: String!) {
    requestPasswordReset(input: {
      email: $email
    })
  }
`;

export const RESET_PASSWORD_MUTATION = gql`
  mutation ResetPassword($token: String!, $newPassword: String!) {
    resetPassword(input: {
      token: $token,
      newPassword: $newPassword
    })
  }
`;
