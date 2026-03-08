import { NextRequest, NextResponse } from "next/server";
import {
  ACCESS_TOKEN_COOKIE,
  ACCESS_TOKEN_MAX_AGE_SECONDS,
  GRAPHQL_API_URL,
} from "@/lib/server/backend";

const AUTHENTICATE_MUTATION = `
  mutation Authenticate($email: String!, $password: String!) {
    authenticate(input: {
      email: $email,
      password: $password
    }) {
      accessToken
    }
  }
`;

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  const upstream = await fetch(GRAPHQL_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: AUTHENTICATE_MUTATION,
      variables: { email, password },
    }),
    cache: "no-store",
  });

  const payload = await upstream.json();
  const accessToken = payload?.data?.authenticate?.accessToken;

  if (!upstream.ok || !accessToken || payload?.errors?.length) {
    const message =
      payload?.errors?.[0]?.message || "Введены неверные данные";

    return NextResponse.json({ error: message }, { status: 401 });
  }

  const response = NextResponse.json({ ok: true });
  response.cookies.set({
    name: ACCESS_TOKEN_COOKIE,
    value: accessToken,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: ACCESS_TOKEN_MAX_AGE_SECONDS,
  });

  return response;
}
