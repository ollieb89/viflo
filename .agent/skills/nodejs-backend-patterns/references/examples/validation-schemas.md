# Validation Schema Examples

Extracted from [SKILL.md](../../SKILL.md)

## Zod Validation

### Installation

```bash
npm install zod
```

### Basic User Schema

```typescript
import { z } from "zod";

export const createUserSchema = z.object({
  body: z.object({
    name: z.string().min(1, "Name is required").max(100),
    email: z.string().email("Invalid email format"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/^(?=.*[A-Z])/, "Must contain at least one uppercase letter")
      .regex(/^(?=.*[0-9])/, "Must contain at least one number"),
    age: z.number().int().min(18).optional(),
    role: z.enum(["user", "admin"]).default("user"),
  }),
});

export type CreateUserDTO = z.infer<typeof createUserSchema>;
```

### Update User Schema

```typescript
export const updateUserSchema = z.object({
  params: z.object({
    id: z.string().uuid("Invalid user ID"),
  }),
  body: z.object({
    name: z.string().min(1).max(100).optional(),
    email: z.string().email().optional(),
    age: z.number().int().min(0).optional(),
  }),
});
```

### Query Parameters Schema

```typescript
export const paginationSchema = z.object({
  query: z.object({
    page: z.string().transform(Number).pipe(z.number().min(1)).default("1"),
    limit: z
      .string()
      .transform(Number)
      .pipe(z.number().min(1).max(100))
      .default("20"),
    sort: z.string().optional(),
    order: z.enum(["asc", "desc"]).default("asc"),
    search: z.string().optional(),
  }),
});
```

### Nested Object Schema

```typescript
export const createOrderSchema = z.object({
  body: z.object({
    userId: z.string().uuid(),
    items: z
      .array(
        z.object({
          productId: z.string().uuid(),
          quantity: z.number().int().min(1),
          price: z.number().positive(),
        }),
      )
      .min(1),
    shippingAddress: z.object({
      street: z.string().min(1),
      city: z.string().min(1),
      zipCode: z.string().regex(/^\d{5}$/),
      country: z.string().length(2),
    }),
  }),
});
```

## Joi Validation

### Installation

```bash
npm install joi
```

### Basic User Schema

```typescript
import Joi from "joi";

export const createUserSchema = Joi.object({
  body: Joi.object({
    name: Joi.string().min(1).max(100).required(),
    email: Joi.string().email().required(),
    password: Joi.string()
      .min(8)
      .pattern(/^(?=.*[A-Z])/)
      .pattern(/^(?=.*[0-9])/)
      .required(),
    age: Joi.number().integer().min(18).optional(),
    role: Joi.string().valid("user", "admin").default("user"),
  }),
});
```

### Login Schema

```typescript
export const loginSchema = Joi.object({
  body: Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().required(),
    rememberMe: Joi.boolean().default(false),
  }),
});
```

### ID Parameter Schema

```typescript
export const idParamSchema = Joi.object({
  params: Joi.object({
    id: Joi.string().uuid().required(),
  }),
});
```

### Custom Validation Messages

```typescript
export const userSchema = Joi.object({
  body: Joi.object({
    username: Joi.string()
      .alphanum()
      .min(3)
      .max(30)
      .required()
      .messages({
        "string.alphanum": "Username must only contain letters and numbers",
        "string.min": "Username must be at least 3 characters",
        "string.max": "Username cannot exceed 30 characters",
        "any.required": "Username is required",
      }),
    email: Joi.string().email().required().messages({
      "string.email": "Please provide a valid email address",
      "any.required": "Email is required",
    }),
  }),
});
```

## Express Middleware Integration

### Zod Middleware

```typescript
// middleware/validate-zod.ts
import { Request, Response, NextFunction } from "express";
import { AnyZodObject, ZodError } from "zod";

export const validate = (schema: AnyZodObject) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const errors = error.errors.map((err) => ({
          field: err.path.join("."),
          message: err.message,
        }));
        return res.status(400).json({
          status: "error",
          message: "Validation failed",
          errors,
        });
      }
      next(error);
    }
  };
};
```

### Joi Middleware

```typescript
// middleware/validate-joi.ts
import { Request, Response, NextFunction } from "express";
import Joi from "joi";

export const validateJoi = (schema: Joi.ObjectSchema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const dataToValidate = {
      body: req.body,
      query: req.query,
      params: req.params,
    };

    const { error, value } = schema.validate(dataToValidate, {
      abortEarly: false,
      stripUnknown: true,
    });

    if (error) {
      const errors = error.details.map((detail) => ({
        field: detail.path.join("."),
        message: detail.message,
      }));
      return res.status(400).json({
        status: "error",
        message: "Validation failed",
        errors,
      });
    }

    // Update request with validated values
    req.body = value.body;
    req.query = value.query;
    req.params = value.params;
    next();
  };
};
```

## Advanced Patterns

### Conditional Validation with Zod

```typescript
const conditionalSchema = z
  .object({
    type: z.enum(["individual", "business"]),
    businessName: z.string().optional(),
    taxId: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.type === "business") {
        return !!data.businessName && !!data.taxId;
      }
      return true;
    },
    {
      message: "Business name and tax ID required for business accounts",
      path: ["businessName"],
    },
  );
```

### Custom Validators with Joi

```typescript
const customJoi = Joi.extend((joi) => ({
  type: "password",
  base: joi.string(),
  messages: {
    "password.complexity":
      "Password must contain uppercase, lowercase, number, and special character",
  },
  validate(value, helpers) {
    const hasUpper = /[A-Z]/.test(value);
    const hasLower = /[a-z]/.test(value);
    const hasNumber = /[0-9]/.test(value);
    const hasSpecial = /[!@#$%^&*]/.test(value);

    if (!hasUpper || !hasLower || !hasNumber || !hasSpecial) {
      return { value, errors: helpers.error("password.complexity") };
    }
  },
}));

const passwordSchema = Joi.object({
  password: customJoi.password().min(8).required(),
});
```

### Array Validation

```typescript
// Zod
const batchSchema = z.object({
  items: z.array(z.string().uuid()).min(1).max(100),
});

// Joi
const batchSchemaJoi = Joi.object({
  items: Joi.array()
    .items(Joi.string().uuid())
    .min(1)
    .max(100)
    .unique()
    .required(),
});
```

### Date Validation

```typescript
// Zod
const dateRangeSchema = z.object({
  startDate: z.coerce.date(),
  endDate: z.coerce.date(),
}).refine((data) => data.endDate > data.startDate, {
  message: "End date must be after start date",
  path: ["endDate"],
});

// Joi
const dateRangeSchemaJoi = Joi.object({
  startDate: Joi.date().iso().required(),
  endDate: Joi.date().iso().greater(Joi.ref("startDate")).required(),
});
```
