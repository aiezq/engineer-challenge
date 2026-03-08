import { NextRequest, NextResponse } from "next/server";
import { ACCESS_TOKEN_COOKIE, GRAPHQL_API_URL } from "@/lib/server/backend";

export async function POST(request: NextRequest) {
  const token = request.cookies.get(ACCESS_TOKEN_COOKIE)?.value;
  const body = await request.text();

  const headers = new Headers({
    "Content-Type": request.headers.get("content-type") || "application/json",
  });

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let upstream: Response;
  try {
    upstream = await fetch(GRAPHQL_API_URL, {
      method: "POST",
      headers,
      body,
      cache: "no-store",
    });
  } catch {
    return NextResponse.json(
      { errors: [{ message: "GraphQL backend unavailable" }] },
      { status: 503 },
    );
  }

  const payload = await upstream.text();

  return new NextResponse(payload, {
    status: upstream.status,
    headers: {
      "Content-Type": upstream.headers.get("content-type") || "application/json",
    },
  });
}
