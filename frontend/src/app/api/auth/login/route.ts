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

  let upstream: Response;
  try {
    upstream = await fetch(GRAPHQL_API_URL, {
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
  } catch {
    return NextResponse.json(
      { error: "Сервис авторизации временно недоступен" },
      { status: 503 },
    );
  }

  if (upstream.status >= 500) {
    return NextResponse.json(
      { error: "Сервис авторизации временно недоступен" },
      { status: 502 },
    );
  }

  const payload = await upstream.json();
  const accessToken = payload?.data?.authenticate?.accessToken;
  const upstreamMessage = payload?.errors?.[0]?.message as string | undefined;

  if (!upstream.ok || !accessToken || payload?.errors?.length) {
    if (upstream.status === 429 || upstreamMessage === "Too Many Requests") {
      return NextResponse.json(
        { error: "Слишком много попыток входа. Попробуйте позже" },
        { status: 429 },
      );
    }

    if (upstream.status === 401 || upstreamMessage === "Invalid email or password") {
      return NextResponse.json(
        { error: "Введены неверные данные" },
        { status: 401 },
      );
    }

    return NextResponse.json(
      { error: "Сервис авторизации временно недоступен" },
      { status: 502 },
    );
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
