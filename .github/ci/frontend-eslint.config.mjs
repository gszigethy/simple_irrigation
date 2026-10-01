import { createRequire } from "node:module";

const require = createRequire(new URL("./node-tools/package.json", import.meta.url));
const parser = require("@typescript-eslint/parser");

export default [{
  files: ["**/*.ts"],
  languageOptions: { parser, ecmaVersion: "latest", sourceType: "module" },
  rules: {
    "no-dupe-args": "error",
    "no-dupe-keys": "error",
    "no-unreachable": "error",
    "no-constant-condition": "error",
    "no-self-assign": "error",
    "valid-typeof": "error",
    "use-isnan": "error"
  }
}];
