import test from "node:test";
import assert from "node:assert/strict";

import { normalizeAccount, resolveApiUrl } from "../src/utils/api-runtime.js";

test("resolveApiUrl defaults to same-origin relative paths", () => {
  assert.equal(resolveApiUrl("/login"), "/login");
  assert.equal(resolveApiUrl("/api/v2/tasks/stream"), "/api/v2/tasks/stream");
});

test("resolveApiUrl respects configured API base URLs", () => {
  assert.equal(
    resolveApiUrl("/login", "http://127.0.0.1:5410"),
    "http://127.0.0.1:5410/login",
  );
  assert.equal(
    resolveApiUrl("download/file.mp4", "http://127.0.0.1:5410/"),
    "http://127.0.0.1:5410/download/file.mp4",
  );
});

test("normalizeAccount supports legacy array rows", () => {
  assert.deepEqual(
    normalizeAccount([2, 5, "bili.json", "Bili User", 1, "https://example.com/a.png"]),
    {
      id: 2,
      type: 5,
      filePath: "bili.json",
      name: "Bili User",
      status: "\u6b63\u5e38",
      platform: "B\u7ad9",
      avatar: "https://example.com/a.png",
    },
  );
});

test("normalizeAccount supports object rows", () => {
  assert.deepEqual(
    normalizeAccount({
      id: 3,
      type: 4,
      filePath: "kuaishou.json",
      userName: "\u5feb\u624b\u53f7",
      status: 0,
      avatar: "",
    }),
    {
      id: 3,
      type: 4,
      filePath: "kuaishou.json",
      name: "\u5feb\u624b\u53f7",
      status: "\u5f02\u5e38",
      platform: "\u5feb\u624b",
      avatar: "",
    },
  );
});
