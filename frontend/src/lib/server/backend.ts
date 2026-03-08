export const GRAPHQL_API_URL =
  process.env.GRAPHQL_URL ||
  process.env.NEXT_PUBLIC_GRAPHQL_URL ||
  "http://localhost:8000/graphql";

export const ACCESS_TOKEN_COOKIE = "orbitto_access_token";
export const ACCESS_TOKEN_MAX_AGE_SECONDS = 60 * 30;
