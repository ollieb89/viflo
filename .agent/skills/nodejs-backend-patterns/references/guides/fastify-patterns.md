# Fastify Patterns

Extracted from [SKILL.md](../../SKILL.md)

## Basic Setup

```typescript
import Fastify from "fastify";
import helmet from "@fastify/helmet";
import cors from "@fastify/cors";
import compress from "@fastify/compress";

const fastify = Fastify({
  logger: {
    level: process.env.LOG_LEVEL || "info",
    transport: {
      target: "pino-pretty",
      options: { colorize: true },
    },
  },
});

// Plugins
await fastify.register(helmet);
await fastify.register(cors, { origin: true });
await fastify.register(compress);

// Type-safe routes with schema validation
fastify.post<{
  Body: { name: string; email: string };
  Reply: { id: string; name: string };
}>(
  "/users",
  {
    schema: {
      body: {
        type: "object",
        required: ["name", "email"],
        properties: {
          name: { type: "string", minLength: 1 },
          email: { type: "string", format: "email" },
        },
      },
    },
  },
  async (request, reply) => {
    const { name, email } = request.body;
    return { id: "123", name };
  },
);

await fastify.listen({ port: 3000, host: "0.0.0.0" });
```

## Plugin Architecture

Fastify uses a plugin-based architecture for modularity:

```typescript
// plugins/database.ts
import fp from "fastify-plugin";
import { Pool } from "pg";

export default fp(async (fastify, opts) => {
  const pool = new Pool({
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT || "5432"),
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
  });

  fastify.decorate("db", pool);

  fastify.addHook("onClose", async (instance) => {
    await pool.end();
  });
});

// types/fastify.d.ts
declare module "fastify" {
  interface FastifyInstance {
    db: Pool;
  }
}
```

## Schema Validation

Fastify uses JSON Schema for validation:

```typescript
// routes/users.ts
const createUserSchema = {
  body: {
    type: "object",
    required: ["name", "email", "password"],
    properties: {
      name: { type: "string", minLength: 1, maxLength: 100 },
      email: { type: "string", format: "email" },
      password: { type: "string", minLength: 8, pattern: "^(?=.*[A-Z])" },
    },
  },
  response: {
    201: {
      type: "object",
      properties: {
        id: { type: "string" },
        name: { type: "string" },
        email: { type: "string" },
      },
    },
  },
};

fastify.post("/users", { schema: createUserSchema }, async (request, reply) => {
  const user = await userService.create(request.body);
  reply.status(201).send(user);
});
```

## Authentication Hook

```typescript
// hooks/auth.ts
import { FastifyRequest, FastifyReply } from "fastify";
import jwt from "jsonwebtoken";

export async function authenticateHook(
  request: FastifyRequest,
  reply: FastifyReply,
) {
  try {
    const token = request.headers.authorization?.replace("Bearer ", "");

    if (!token) {
      reply.status(401).send({ error: "No token provided" });
      return;
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET!);
    request.user = decoded;
  } catch (err) {
    reply.status(401).send({ error: "Invalid token" });
  }
}

// Apply to routes
fastify.register(async (instance) => {
  instance.addHook("preHandler", authenticateHook);

  instance.get("/protected", async (request) => {
    return { user: request.user };
  });
});
```

## Error Handler

```typescript
// error-handler.ts
import { FastifyError, FastifyRequest, FastifyReply } from "fastify";

fastify.setErrorHandler(
  (error: FastifyError, request: FastifyRequest, reply: FastifyReply) => {
    // Log error
    request.log.error(error);

    // Handle validation errors
    if (error.validation) {
      return reply.status(400).send({
        status: "error",
        message: "Validation failed",
        errors: error.validation,
      });
    }

    // Handle custom errors
    if (error.statusCode) {
      return reply.status(error.statusCode).send({
        status: "error",
        message: error.message,
      });
    }

    // Default: 500
    reply.status(500).send({
      status: "error",
      message:
        process.env.NODE_ENV === "production"
          ? "Internal server error"
          : error.message,
    });
  },
);
```

## Route Prefixing

```typescript
// routes/api.ts
export default async function apiRoutes(fastify, opts) {
  // User routes
  fastify.register(import("./users"), { prefix: "/users" });

  // Order routes
  fastify.register(import("./orders"), { prefix: "/orders" });
}

// app.ts
fastify.register(import("./routes/api"), { prefix: "/api/v1" });
// Results in /api/v1/users, /api/v1/orders
```

## Lifecycle Hooks

```typescript
// hooks lifecycle
fastify.addHook("onRequest", async (request, reply) => {
  // Called on each request (before routing)
  request.log.info("Incoming request");
});

fastify.addHook("preParsing", async (request, reply, payload) => {
  // Before body parsing
  return payload;
});

fastify.addHook("preValidation", async (request, reply) => {
  // Before validation
});

fastify.addHook("preHandler", async (request, reply) => {
  // Before handler (common for auth)
});

fastify.addHook("preSerialization", async (request, reply, payload) => {
  // Before response serialization
  return payload;
});

fastify.addHook("onSend", async (request, reply, payload) => {
  // Before sending response
  return payload;
});

fastify.addHook("onResponse", async (request, reply) => {
  // After response sent (logging, metrics)
  request.log.info({
    statusCode: reply.statusCode,
    responseTime: reply.elapsedTime,
  });
});
```
