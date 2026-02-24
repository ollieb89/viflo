# Auth.js (NextAuth v5) Patterns

## Setup

```typescript
// auth.ts — single source of truth for the whole app
import NextAuth from 'next-auth';
import GitHub from 'next-auth/providers/github';
import { PrismaAdapter } from '@auth/prisma-adapter';
import { db } from '@/lib/db';

export const { handlers, signIn, signOut, auth } = NextAuth({
  adapter: PrismaAdapter(db),
  providers: [GitHub],
  callbacks: {
    session({ session, user }) {
      session.user.id = user.id; // expose DB id to client-side session
      return session;
    },
  },
});
```

```typescript
// app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/auth';
export const { GET, POST } = handlers;
```

## Server-Side Session

```typescript
import { auth } from '@/auth';
import { redirect } from 'next/navigation';

// In a Server Component or Route Handler
export default async function Page() {
  const session = await auth();
  if (!session) redirect('/sign-in');
  return <div>Hello {session.user.name}</div>;
}
```

## Client-Side Session

```typescript
'use client';
import { useSession } from 'next-auth/react';

export function Nav() {
  const { data: session, status } = useSession();
  if (status === 'loading') return null;
  if (!session) return <a href="/api/auth/signin">Sign in</a>;
  return <span>{session.user?.name}</span>;
}
```

Wrap your root layout with `<SessionProvider>`:
```typescript
// app/layout.tsx
import { SessionProvider } from 'next-auth/react';
export default function Layout({ children }) {
  return <SessionProvider>{children}</SessionProvider>;
}
```

## Prisma Schema (required for database sessions)

```prisma
model User {
  id            String    @id @default(cuid())
  name          String?
  email         String    @unique
  emailVerified DateTime?
  image         String?
  accounts      Account[]
  sessions      Session[]
}

model Account {
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  user              User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  @@id([provider, providerAccountId])
}

model Session {
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model VerificationToken {
  identifier String
  token      String
  expires    DateTime
  @@id([identifier, token])
}
```

## Environment Variables

```bash
AUTH_SECRET=<random-32-char-string>  # generate: openssl rand -base64 32
AUTH_GITHUB_ID=...
AUTH_GITHUB_SECRET=...
```

## JWT Secret Rollover (zero-downtime rotation)

```typescript
// auth.ts — pass array to support graceful rollover
export const { handlers, signIn, signOut, auth } = NextAuth({
  secret: [process.env.AUTH_SECRET_NEW!, process.env.AUTH_SECRET_OLD!],
  // new tokens use index 0; existing tokens validated against all entries
});
```
