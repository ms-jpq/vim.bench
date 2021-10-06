import {
  CompletionItem,
  CompletionItemKind,
  InsertTextFormat,
  InsertTextMode,
  createConnection,
} from "vscode-languageserver/node";
import { argv, stdin, stdout } from "process";

import { randomBytes } from "crypto";

const len = 12;
const count = 12;

const conn = createConnection(stdin, stdout);

const gen = function* (
  len: number,
  n: number
): IterableIterator<CompletionItem> {
  for (let i = 0; i < n; i++) {
    const rand = randomBytes(len).toString();
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

conn.onCompletion(() => ({ isIncomplete: true, items: [...gen(len, count)] }));
conn.listen();
