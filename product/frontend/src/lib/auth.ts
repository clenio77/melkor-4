"use client";
import { login, refresh } from "./api";

export type Tokens = { access: string; refresh: string };

export async function performLogin(email: string, password: string): Promise<Tokens> {
  const data = await login(email, password);
  return { access: data.access as string, refresh: data.refresh as string };
}

export async function refreshTokens(refreshToken: string): Promise<string> {
  const data = await refresh(refreshToken);
  return data.access as string;
}

