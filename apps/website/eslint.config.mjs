import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  {
    // src/components/ui is vendored from the Aceternity UI registry. It is
    // upstream's code, not ours: it is read and patched where this repo's
    // TypeScript settings demand it (see the header on each edited file), but
    // holding somebody else's components to our hook and ref rules would mean
    // rewriting them, and every rewrite is lost the next time one is re-fetched.
    // Everything under src/app, src/components/site and src/lib is linted
    // normally.
    files: ["src/components/ui/**"],
    rules: {
      "react-hooks/exhaustive-deps": "off",
      "react-hooks/refs": "off",
      "react-hooks/purity": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "@next/next/no-img-element": "off",
      "prefer-const": "off",
    },
  },
]);

export default eslintConfig;
