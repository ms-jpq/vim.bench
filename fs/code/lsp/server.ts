import {
  CompletionItem,
  CompletionItemKind,
  InsertTextFormat,
  InsertTextMode,
  createConnection,
} from "vscode-languageserver/node";
import { env, stdin, stdout } from "process";

import { notEqual } from "assert";
import { randomBytes } from "crypto";

const word_len = parseInt(env.LSP_WORD_LEN ?? "");
notEqual(word_len, NaN);
const reps = parseInt(env.LSP_REPS ?? "");
notEqual(reps, NaN);
const cache = parseInt(env.LSP_CACHE ?? "");
notEqual(cache, NaN);

const conn = createConnection(stdin, stdout);

const gen = function* (): IterableIterator<CompletionItem> {
  for (let i = 0; i < reps; i++) {
    const rand = randomBytes(word_len).toString("hex");
    yield {
      label: rand,
      kind: CompletionItemKind.Text,
      documentation: { kind: "markdown", value: rand },
      deprecated: false,
      preselect: false,
      sortText: rand,
      filterText: rand,
      insertText: rand,
      insertTextFormat: InsertTextFormat.PlainText,
      insertTextMode: InsertTextMode.asIs,
      command: { title: rand, command: rand },
      data: [rand, rand, rand, rand, rand, rand],
    };
  }
};

conn.onInitialize(() => ({
  capabilities: {
    completionProvider: {},
  },
}));
conn.onCompletion(() => ({ isIncomplete: cache > 0, items: [...gen()] }));
conn.listen();
